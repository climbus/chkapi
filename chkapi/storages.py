from typing import Protocol


class Storage(Protocol):
    async def save(self, url: str):
        ...


class TempFileStorage:
    async def save(self, url: str):
        pass
