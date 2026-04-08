from collectors.base import BaseCollector, CollectedRecord


class NewsCollector(BaseCollector):
    source_platform = "news"

    async def fetch(self) -> list[CollectedRecord]:
        return []
