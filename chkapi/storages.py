from pathlib import Path
from tempfile import gettempdir
from typing import Protocol

STORAGE_FILE_NAME = ".chkapi"


class Storage(Protocol):
    async def save(self, url: str):
        ...


class TempFileStorage:
    async def save(self, url: str):
        tmpdir = Path(gettempdir())
        with open(tmpdir / STORAGE_FILE_NAME, "a") as fp:
            fp.write(url + "\n")
