import asyncio
import re
from asyncio.futures import Future
from io import StringIO
from unittest.mock import MagicMock, Mock, patch

import pytest
from rich.console import Console
from textual.app import App
from textual.events import Key

from rest_checker.api_reader import Response
from rest_checker.app import RestChecker
from rest_checker.exceptions import HttpError


def run_on_app(func):
    async def wrapper(self):
        with patch("textual._context.active_app"):

            async def run_test():
                await asyncio.sleep(0.2)
                try:
                    await func(self)
                finally:
                    await self.press_ctrl_c()

            await asyncio.gather(self.current_app.process_messages(), run_test())

    return wrapper


class TestAsyncCase:
    current_app: App
    snapshot: str

    @pytest.fixture(autouse=True)
    def app(self):
        self.api_reader = MagicMock()
        self.api_reader.read_url = Mock(return_value=Future())
        self.console = Console(file=StringIO())
        self.current_app = RestChecker(
            console=self.console, api_reader=self.api_reader, log="test.log"
        )

    @pytest.mark.asyncio
    @run_on_app
    async def test_should_show_go_button(self):
        assert "GO" in self.screen

    @pytest.mark.asyncio
    @run_on_app
    async def test_should_show_error_when_url_is_empty(self):
        await self.press("ctrl+l")
        await self.press("enter")

        assert "Url is required" in self.screen

    @pytest.mark.asyncio
    @run_on_app
    async def test_should_show_error_when_url_is_not_valid(self):
        await self.press("ctrl+l")
        await self.write("htt")
        await self.press("enter")

        assert "Invalid URL" in self.screen

    @pytest.mark.asyncio
    @run_on_app
    async def test_should_show_error_when_status_code_is_not_2xx(self):
        self.api_reader_throws_exception(HttpError("Connection Error"))

        await self.press("ctrl+l")
        await self.write("http://localhost/")
        await self.press("enter")

        assert "Connection Error" in self.screen

    @pytest.mark.asyncio
    @run_on_app
    async def test_should_return_json_from_url(self):
        json = '{"a": 1}'
        self._api_reader_returns_response_with_json(Response(json))

        await self.press("ctrl+l")
        await self.write("http://localhost/")
        await self.press("enter")
        assert self.screen_contains(r"{[\s\n]+\"a\":\s1[\s\n]+}")

    @pytest.mark.asyncio
    @run_on_app
    async def test_should_show_headers(self):
        headers = {"Header1": "val 1", "header-2": "val 2"}
        self._api_reader_returns_response_with_json(Response("{}", headers=headers))

        await self.press("ctrl+l")
        await self.write("http://localhost/")
        await self.press("enter")
        await self.press("h")
        assert self.screen_contains(r"Header1.*val 1")
        assert self.screen_contains(r"header-2.*val 2")

    def screen_contains(self, content_regexp):
        return re.search(content_regexp, self.screen)

    def api_reader_throws_exception(self, exception):
        self.api_reader.read_url.return_value.set_exception(exception)

    @property
    def screen(self):
        return self.current_app.console.file.getvalue()

    async def press_ctrl_c(self):
        await self.current_app.press("ctrl+c")

    async def press(self, key):
        await self.current_app.post_message(Key(self.current_app, key=key))
        await asyncio.sleep(0.1)

    async def write(self, text):
        for char in text:
            await self.current_app.post_message(Key(self.current_app, key=char))

    def _api_reader_returns_response_with_json(self, data):
        self.api_reader.read_url.return_value.set_result(data)
