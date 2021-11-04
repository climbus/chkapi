import collections
import os
from pathlib import Path
from tempfile import gettempdir
from typing import Protocol

STORAGE_FILE_NAME = ".chkapi"


class Storage(Protocol):
    async def save(self, url: str):
        ...

    async def find(self, phrase: str):
        ...


class TempFileStorage:
    async def save(self, url: str) -> None:
        tmpdir = Path(gettempdir())
        lines = self._load_existing_lines(tmpdir) or set()
        lines.add(url)
        self._write_lines(tmpdir, lines)

    async def find(self, phrase: str) -> list[str]:
        tmpdir = Path(gettempdir())
        lines = self._load_existing_lines(tmpdir)
        return [line.strip() for line in lines if phrase in line]

    def _write_lines(self, tmpdir, lines: collections.Collection):
        with open(tmpdir / STORAGE_FILE_NAME, "w") as fp:
            fp.write("\n".join(sorted(lines)))

    def _load_existing_lines(self, tmpdir) -> set[str]:
        if os.path.exists(tmpdir / STORAGE_FILE_NAME):
            lines = set()
            with open(tmpdir / STORAGE_FILE_NAME, "r") as fp:
                lines.update(fp.readlines())
            return lines
        return set()
