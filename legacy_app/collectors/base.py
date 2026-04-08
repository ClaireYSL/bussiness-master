from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional


@dataclass
class CollectedRecord:
    source_platform: str
    source_id: str
    url: Optional[str] = None
    raw_html: Optional[str] = None
    raw_json: Optional[dict[str, Any]] = None
    fetched_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def normalized_source_platform(self, fallback: str) -> str:
        return self.source_platform or fallback


class BaseCollector(ABC):
    source_platform: str

    @abstractmethod
    async def fetch(self) -> list[CollectedRecord]:
        raise NotImplementedError
