from collectors.base import BaseCollector, CollectedRecord


class ContentCollector(BaseCollector):
    source_platform = "content"

    async def fetch(self) -> list[CollectedRecord]:
        return []
