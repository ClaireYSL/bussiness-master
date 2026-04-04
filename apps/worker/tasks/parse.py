from __future__ import annotations

from collections.abc import Callable
from types import SimpleNamespace
from typing import Optional

from sqlalchemy import delete, select, update
from sqlalchemy.orm import Session, sessionmaker

from parsers.base import BaseParser, ParsedSignal
from parsers.content import ContentParser
from parsers.jobs import JobsParser
from parsers.news import NewsParser
from shared.db import get_session_factory
from shared.models import Company, RawRecord, Signal
from shared.services.resolver import resolve_company

ParserFactory = Callable[[str], BaseParser]

PARSER_REGISTRY: dict[str, type[BaseParser]] = {
    "jobs": JobsParser,
    "news": NewsParser,
    "content": ContentParser,
}

PARSE_STATUS_PENDING = "pending"
PARSE_STATUS_PARSING = "parsing"
PARSE_STATUS_PARSED = "parsed"
PARSE_STATUS_FAILED = "failed"


def get_parser(source_platform: str) -> BaseParser:
    parser_cls = PARSER_REGISTRY.get(source_platform)
    if parser_cls is None:
        raise ValueError(f"Unsupported parser source: {source_platform}")
    return parser_cls()


def _get_or_create_company(session: Session, company_name: str) -> Company:
    return resolve_company(session, company_name)


def _signal_from_parsed(parsed: ParsedSignal, company_id: int) -> Signal:
    return Signal(
        company_id=company_id,
        source_type=parsed.source_platform,
        source_platform=parsed.source_platform,
        signal_type=parsed.signal_type,
        title=parsed.title,
        summary=parsed.summary,
        keywords=parsed.keywords or None,
        published_at=parsed.published_at,
        evidence_url=parsed.evidence_url,
        raw_record_id=parsed.raw_record_id,
        signal_weight=parsed.signal_weight,
        confidence=parsed.confidence,
    )


def _mark_parse_failed(session: Session, raw_record_id: int, error: str) -> None:
    session.execute(
        update(RawRecord)
        .where(RawRecord.id == raw_record_id)
        .values(parse_status=PARSE_STATUS_FAILED, parse_error=error)
    )


def _claim_parse(session: Session, raw_record: RawRecord) -> SimpleNamespace | None:
    if raw_record.parse_status != PARSE_STATUS_PENDING:
        return None

    result = session.execute(
        update(RawRecord)
        .where(
            RawRecord.id == raw_record.id,
            RawRecord.parse_status == PARSE_STATUS_PENDING,
        )
        .values(parse_status=PARSE_STATUS_PARSING, parse_error=None)
    )
    if result.rowcount != 1:
        return None

    return SimpleNamespace(
        id=raw_record.id,
        source_platform=raw_record.source_platform,
        source_id=raw_record.source_id,
        url=raw_record.url,
        raw_html=raw_record.raw_html,
        raw_json=raw_record.raw_json,
    )


def _mark_parse_succeeded(session: Session, raw_record_id: int) -> None:
    session.execute(
        update(RawRecord)
        .where(RawRecord.id == raw_record_id)
        .values(parse_status=PARSE_STATUS_PARSED, parse_error=None)
    )


def run_parse(
    raw_record_id: int,
    *,
    parser_factory: Optional[ParserFactory] = None,
    session_factory: Optional[sessionmaker[Session]] = None,
) -> int:
    factory = session_factory or get_session_factory()
    parser_factory = parser_factory or get_parser

    with factory() as session:
        try:
            with session.begin():
                raw_record = session.get(RawRecord, raw_record_id)
                if raw_record is None:
                    raise ValueError(f"RawRecord not found: {raw_record_id}")

                raw_record = _claim_parse(session, raw_record)
                if raw_record is None:
                    return 0

                parser = parser_factory(raw_record.source_platform)
                parsed_signals = list(parser.parse(raw_record))

                session.execute(
                    delete(Signal).where(Signal.raw_record_id == raw_record.id)
                )
                inserted = 0
                for parsed_signal in parsed_signals:
                    company = _get_or_create_company(session, parsed_signal.company_name)
                    session.add(_signal_from_parsed(parsed_signal, company.id))
                    inserted += 1
                _mark_parse_succeeded(session, raw_record.id)
            return inserted
        except Exception as exc:  # pragma: no cover - exercised through tests
            with session.begin():
                raw_record = session.get(RawRecord, raw_record_id)
                if raw_record is not None:
                    _mark_parse_failed(session, raw_record.id, str(exc))
            raise
