from dataclasses import dataclass
from typing import Dict, Protocol, cast
from http import HTTPStatus
import httpx

from rest_checker.exceptions import BadUrlException, HttpError


@dataclass
class URL(object):
    url: str


class APIReader(Protocol):
    async def read_url(self, url: URL) -> str:
        ...


class AsyncAPIReader(object):
    status_list: Dict[int, str]

    def __init__(self) -> None:
        self.status_list = self._get_status_list()

    def _get_status_list(self):
        return dict(
            [
                (status.value, f"{status.phrase}: {status.description}")
                for status in vars(HTTPStatus).values()
                if isinstance(status, HTTPStatus)
            ]
        )

    async def read_url(self, url: URL) -> str:
        if not url:
            raise BadUrlException()

        async with httpx.AsyncClient() as client:
            result = await client.get(url.url)
            if result.status_code != 200:
                raise HttpError(self.status_list[result.status_code])
            return result.text
