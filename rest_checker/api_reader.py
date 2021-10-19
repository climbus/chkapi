from dataclasses import dataclass
from typing import Protocol

import httpx

from rest_checker.exceptions import BadUrlException


@dataclass
class URL(object):
    url: str


class APIReader(Protocol):
    async def read_url(self, url: URL) -> str:
        ...


class AsyncAPIReader(object):
    async def read_url(self, url: URL) -> str:
        if not url:
            raise BadUrlException()
        async with httpx.AsyncClient() as client:
            result = await client.get(url.url)
            return result.text
