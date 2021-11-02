import pytest
import os
import tempfile

from chkapi.storages import TempFileStorage


@pytest.fixture(autouse=True)
def set_tmpdir(tmp_path):
    tempfile.tempdir = None
    os.environ["TMPDIR"] = str(tmp_path)


@pytest.mark.asyncio
async def test_save_url(tmp_path):
    url = "http://localhost/\n"
    storage = TempFileStorage()

    await storage.save(url)

    with open(tmp_path / ".chkapi") as fp:
        assert fp.readline() == url
