from typing import Protocol
from tempfile import gettempdir
from pathlib import Path


class Storage(Protocol):
    async def save(self, url: str):
        ...


class TempFileStorage:
    async def save(self, url: str):
        tmpdir = Path(gettempdir())
        with open(tmpdir / ".chkapi", "a") as fp:
            fp.write(url + "\n")
