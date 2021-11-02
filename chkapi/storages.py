import os
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
        lines = self._load_existing_lines(tmpdir) or set()
        lines.add(url)
        self._write_lines(tmpdir, lines)

    def _write_lines(self, tmpdir, lines):
        with open(tmpdir / STORAGE_FILE_NAME, "w") as fp:
            fp.write("\n".join(sorted(lines)))

    def _load_existing_lines(self, tmpdir):
        if os.path.exists(tmpdir / STORAGE_FILE_NAME):
            lines = set()
            with open(tmpdir / STORAGE_FILE_NAME, "r") as fp:
                lines.update(fp.readlines())
            return lines
