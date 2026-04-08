from __future__ import annotations

import asyncio
from collections.abc import Callable
from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import update
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.dialects.postgresql import insert as postgres_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert

from collectors.base import BaseCollector, CollectedRecord
from collectors.content import ContentCollector
from collectors.jobs import JobsCollector
from collectors.news import NewsCollector
from shared.db import get_session_factory
from shared.models import RawRecord

CollectorFactory = Callable[[str], BaseCollector]

COLLECTOR_REGISTRY: dict[str, type[BaseCollector]] = {
    "jobs": JobsCollector,
    "news": NewsCollector,
    "content": ContentCollector,
}


def get_collector(source: str) -> BaseCollector:
    collector_cls = COLLECTOR_REGISTRY.get(source)
    if collector_cls is None:
        raise ValueError(f"Unsupported collector source: {source}")
    return collector_cls()


async def _resolve_records(fetch_result: Any) -> list[CollectedRecord]:
    if asyncio.iscoroutine(fetch_result):
        fetch_result = await fetch_result
    return list(fetch_result)


def _normalize_record(record: CollectedRecord, default_source: str) -> CollectedRecord:
    if record.source_platform:
        return record
    return CollectedRecord(
        source_platform=default_source,
        source_id=record.source_id,
        url=record.url,
        raw_html=record.raw_html,
        raw_json=record.raw_json,
        fetched_at=record.fetched_at,
    )


def _get_insert_statement(record: CollectedRecord, default_source: str, dialect_name: str):
    values = {
        "source_platform": record.source_platform or default_source,
        "source_id": record.source_id,
        "url": record.url,
        "raw_html": record.raw_html,
        "raw_json": record.raw_json,
        "fetched_at": record.fetched_at or datetime.now(timezone.utc),
        "parse_status": "pending",
        "parse_error": None,
    }
    if dialect_name == "sqlite":
        return sqlite_insert(RawRecord).values(**values)
    return postgres_insert(RawRecord).values(**values)


def _build_update_values(record: CollectedRecord, default_source: str) -> dict[str, Any]:
    return {
        "url": record.url,
        "raw_html": record.raw_html,
        "raw_json": record.raw_json,
        "fetched_at": record.fetched_at or datetime.now(timezone.utc),
        "parse_status": "pending",
        "parse_error": None,
    }


def upsert_raw_records(session: Session, records: list[CollectedRecord], default_source: str) -> int:
    inserted = 0
    seen_keys: set[tuple[str, str]] = set()
    dialect_name = session.get_bind().dialect.name
    for record in records:
        if not record.source_id:
            continue

        normalized = _normalize_record(record, default_source)
        source_platform = normalized.source_platform or default_source
        key = (source_platform, normalized.source_id)
        if key in seen_keys:
            continue

        insert_stmt = _get_insert_statement(normalized, default_source, dialect_name)
        insert_stmt = insert_stmt.on_conflict_do_nothing(
            index_elements=[RawRecord.source_platform, RawRecord.source_id]
        )
        result = session.execute(insert_stmt)
        if result.rowcount == 1:
            inserted += 1
        else:
            update_stmt = (
                update(RawRecord)
                .where(
                    RawRecord.source_platform == source_platform,
                    RawRecord.source_id == normalized.source_id,
                )
                .values(**_build_update_values(normalized, default_source))
            )
            session.execute(update_stmt)
        seen_keys.add(key)

    return inserted


async def collect_source_records(
    source: str,
    *,
    collector_factory: Optional[CollectorFactory] = None,
    session_factory: Optional[sessionmaker[Session]] = None,
) -> int:
    factory = session_factory or get_session_factory()
    collector = collector_factory(source) if collector_factory is not None else get_collector(source)
    records = await _resolve_records(collector.fetch())

    with factory() as session:
        with session.begin():
            return upsert_raw_records(session, records, source)


def collect_source(
    source: str,
    *,
    collector_factory: Optional[CollectorFactory] = None,
    session_factory: Optional[sessionmaker[Session]] = None,
) -> int:
    return asyncio.run(
        collect_source_records(
            source,
            collector_factory=collector_factory,
            session_factory=session_factory,
        )
    )


def collect_all_sources(
    *,
    collector_factory: Optional[CollectorFactory] = None,
    session_factory: Optional[sessionmaker[Session]] = None,
) -> dict[str, int]:
    results: dict[str, int] = {}
    for source in COLLECTOR_REGISTRY:
        results[source] = collect_source(
            source,
            collector_factory=collector_factory,
            session_factory=session_factory,
        )
    return results
