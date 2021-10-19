from dataclasses import dataclass
from typing import Protocol

import httpx


@dataclass
class URL(object):
    url: str


class APIReader(Protocol):
    async def read_url(self, url: URL) -> str:
        ...


class AsyncAPIReader(object):
    async def read_url(self, url: URL) -> str:
        async with httpx.AsyncClient() as client:
            result = await client.get(url.url)
            return result.text
