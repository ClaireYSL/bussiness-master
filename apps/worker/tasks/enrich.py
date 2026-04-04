from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy.dialects.postgresql import insert as postgres_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.orm import Session, sessionmaker

from collectors.website_contacts import WebsiteContactsCollector
from shared.db import get_session_factory
from shared.models import Contact
from shared.services.enricher import enrich_public_contacts

CollectorFactory = Callable[[], WebsiteContactsCollector]


def _normalize_contact_value(contact_type: str, contact_value: str) -> str:
    if contact_type == "email":
        return contact_value.strip().lower()
    if contact_type == "phone":
        digits = "".join(ch for ch in contact_value if ch.isdigit())
        if digits.startswith("86") and len(digits) > 11:
            digits = digits[2:]
        return digits
    return contact_value.strip().lower().rstrip("/")


def _build_insert_statement(session: Session, values: dict[str, Any]):
    dialect_name = session.get_bind().dialect.name
    if dialect_name == "sqlite":
        return sqlite_insert(Contact).values(**values)
    if dialect_name == "postgresql":
        return postgres_insert(Contact).values(**values)
    raise ValueError(f"Unsupported database dialect: {dialect_name}")


def _upsert_contacts(session: Session, company_id: int, contacts: list[dict[str, Any]]) -> dict[str, int]:
    created = 0
    skipped = 0
    seen: set[tuple[str, str]] = set()

    for contact in contacts:
        contact_type = str(contact.get("contact_type") or "").strip()
        contact_value = str(contact.get("contact_value") or "").strip()
        if not contact_type or not contact_value:
            skipped += 1
            continue

        normalized_value = str(
            contact.get("normalized_value") or _normalize_contact_value(contact_type, contact_value)
        )
        signature = (contact_type, normalized_value)
        if signature in seen:
            skipped += 1
            continue
        seen.add(signature)

        values = {
            "company_id": company_id,
            "contact_type": contact_type,
            "contact_value": contact_value,
            "normalized_value": normalized_value,
            "source_url": contact.get("source_url"),
            "is_public": bool(contact.get("is_public", True)),
            "verified_at": contact.get("verified_at"),
            "created_at": contact.get("created_at") or datetime.now(timezone.utc),
        }
        insert_stmt = _build_insert_statement(session, values)
        insert_stmt = insert_stmt.on_conflict_do_nothing(
            index_elements=[
                Contact.__table__.c.company_id,
                Contact.__table__.c.contact_type,
                Contact.__table__.c.normalized_value,
            ]
        )
        result = session.execute(insert_stmt)
        if result.rowcount == 1:
            created += 1
        else:
            skipped += 1

    return {"created": created, "skipped": skipped}


def run_enrichment(
    company_id: int,
    *,
    collector_factory: Optional[CollectorFactory] = None,
    session_factory: Optional[sessionmaker[Session]] = None,
    source_html: Optional[str] = None,
) -> dict[str, int]:
    factory = session_factory or get_session_factory()
    collector = collector_factory() if collector_factory is not None else WebsiteContactsCollector()

    with factory() as session:
        with session.begin():
            contacts = enrich_public_contacts(
                session,
                company_id,
                collector=collector,
                source_html=source_html,
            )
            return _upsert_contacts(session, company_id, contacts)
