import os
import tempfile

import pytest

from chkapi.storages import STORAGE_FILE_NAME, TempFileStorage


@pytest.fixture(autouse=True)
def set_tmpdir(tmp_path):
    tempfile.tempdir = None
    os.environ["TMPDIR"] = str(tmp_path)


@pytest.mark.asyncio
async def test_save_url(tmp_path):
    url = "http://localhost/\n"
    storage = TempFileStorage()

    await storage.save(url)

    with open(tmp_path / STORAGE_FILE_NAME) as fp:
        assert fp.readline() == url
