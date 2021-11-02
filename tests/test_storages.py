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


@pytest.mark.asyncio
async def test_saves_only_unique_urls(tmp_path):
    url1 = "http://localhost/"
    url2 = "http://127.0.0.1/"

    storage = TempFileStorage()
    await storage.save(url1)
    await storage.save(url1)
    await storage.save(url2)

    with open(tmp_path / STORAGE_FILE_NAME) as fp:
        assert fp.read() == f"{url2}\n{url1}"
