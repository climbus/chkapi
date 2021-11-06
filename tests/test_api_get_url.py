import tempfile
import os
import asyncio
from unittest.mock import patch, MagicMock, Mock
from asyncio.futures import Future
from io import StringIO
import re

from rich.console import Console
from pytest_bdd import scenario, given, when, then, parsers
import pytest
from textual.events import Key

from chkapi.app import CheckApiApp
from chkapi.exceptions import HttpError


@pytest.fixture(autouse=True)
def set_tmpdir(tmp_path):
    tempfile.tempdir = None
    os.environ["TMPDIR"] = str(tmp_path)


@pytest.fixture()
def app(event_loop):
    current_app = create_app()
    run_app(event_loop, current_app)
    yield current_app
    stop_app(event_loop, current_app)


def stop_app(event_loop, current_app):
    event_loop.run_until_complete(
        current_app.post_message(Key(current_app, key="ctrl+c"))
    )


def run_app(event_loop, current_app):
    event_loop.call_soon(asyncio.gather(current_app.process_messages()))


def create_app():
    api_reader = mock_api_reader()
    console = Console(color_system="256", file=StringIO())
    current_app = CheckApiApp(console=console, api_reader=api_reader, log="test.log")
    return current_app


def mock_api_reader():
    api_reader = MagicMock()
    api_reader.read_url = Mock(return_value=Future())
    return api_reader


@scenario("../features/api_get_url.feature", "Empty URL")
def test_empty_url():
    pass


@scenario("../features/api_get_url.feature", "Invalid URL")
def test_invalid_url():
    pass


@scenario("../features/api_get_url.feature", "Connection Error")
def test_connection_error():
    pass


@when(parsers.parse('I press "{key}"'))
def press(key, app, event_loop):
    new_screen_capture(app)
    event_loop.run_until_complete(app.post_message(Key(app, key=key)))
    event_loop.run_until_complete(asyncio.sleep(0.1))


@when(parsers.parse('I write "{text}"'))
def write(text, app, event_loop):
    for key in text:
        event_loop.run_until_complete(app.post_message(Key(app, key=key)))


@given('server responds with error')
def server_responds_with_error(app):
    exception = HttpError("Connection Error")
    app.api_reader.read_url.return_value.set_exception(exception)


@then(parsers.parse('I see "{text}" on screen'))
def see(text, app):
    assert re.search(text, screen(app))


@then(parsers.parse('I don\'t see "{text}" on screen'))
def dont_see(text, app):
    assert "URL" in screen(app)
    assert not re.search(text, screen(app))


def screen(app):
    return app.console.file.getvalue()


def new_screen_capture(app):
    app.console.file.truncate(0)
