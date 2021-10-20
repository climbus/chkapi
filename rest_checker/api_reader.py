from dataclasses import dataclass
from typing import Protocol

import httpx

from rest_checker.exceptions import BadUrlException, HttpError


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
            if result.status_code == 404:
                raise HttpError("Url not found")
            return result.text
