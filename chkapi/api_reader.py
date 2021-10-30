from dataclasses import dataclass
from http import HTTPStatus
from typing import Dict, Protocol
from urllib.parse import urlparse

import httpx

from chkapi.exceptions import BadUrlException, HttpError


class Response:
    body: str
    headers: dict

    def __init__(self, body: str, headers: dict) -> None:
        self.body = body
        self.headers = headers

    def __eq__(self, other):
        return self.body == other.body and self.headers == other.headers


@dataclass
class URL:
    url: str

    def __post_init__(self):
        url = urlparse(self.url)
        if not url.scheme or not url.netloc:
            raise BadUrlException("Invalid URL")


class APIReader(Protocol):
    async def read_url(self, url: URL) -> Response:
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

    async def read_url(self, url: URL) -> Response:
        if not url:
            raise BadUrlException()

        async with httpx.AsyncClient() as client:
            try:
                result = await client.get(url.url)
            except httpx.ConnectError:
                raise HttpError("Connection Error")
            except Exception as e:
                raise HttpError(str(e))

            if result.status_code != 200:
                raise HttpError(self.status_list[result.status_code])

            return Response(result.text, headers=result.headers)
