import pytest
from pytest_httpserver.httpserver import HTTPServer

from rest_checker.api_reader import URL, AsyncAPIReader, Response
from rest_checker.exceptions import BadUrlException, HttpError


@pytest.mark.asyncio
async def test_none_as_url_should_raise_bad_url_exception():
    reader = AsyncAPIReader()
    with pytest.raises(BadUrlException):
        await reader.read_url(None)  # type: ignore


@pytest.mark.asyncio
async def test_should_get_content_from_server(httpserver: HTTPServer):
    path = "/"
    expected_result = '{"a": 1}'
    httpserver.expect_request(path).respond_with_data(expected_result)
    url = httpserver.url_for(path)

    reader = AsyncAPIReader()
    result = await reader.read_url(URL(url))

    assert result == Response(expected_result)


@pytest.mark.asyncio
async def test_should_raise_http_error_when_status_is_404(httpserver: HTTPServer):
    path = "/"
    httpserver.expect_request(path).respond_with_data("", status=404)
    url = httpserver.url_for(path)

    reader = AsyncAPIReader()

    with pytest.raises(HttpError, match="Not Found: Nothing matches the given URI"):
        await reader.read_url(URL(url))


@pytest.mark.asyncio
async def test_should_raise_http_error_when_connection_error(httpserver: HTTPServer):
    path = "/"
    httpserver.expect_request(path).respond_with_data("", status=200)
    httpserver.stop()
    url = httpserver.url_for(path)
    reader = AsyncAPIReader()

    with pytest.raises(HttpError, match="Connection Error"):
        await reader.read_url(URL(url))
