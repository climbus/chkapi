import pytest

from rest_checker.api_reader import AsyncAPIReader
from rest_checker.exceptions import BadUrlException

@pytest.mark.asyncio
async def test_none_as_url_should_raise_bad_url_exception():
    reader = AsyncAPIReader()
    with pytest.raises(BadUrlException):
        await reader.read_url(None) # type: ignore
