from collectors.base import BaseCollector, CollectedRecord


class JobsCollector(BaseCollector):
    source_platform = "jobs"

    async def fetch(self) -> list[CollectedRecord]:
        return []
