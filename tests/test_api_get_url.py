import tempfile
import os
import asyncio
from unittest.mock import patch, MagicMock, Mock
from asyncio.futures import Future
from io import StringIO
import re

from rich.console import Console
from pytest_bdd import scenario, when, then, parsers
import pytest
from textual.events import Key

from chkapi.app import CheckApiApp


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
def test_get_url():
    pass


@when(parsers.parse('I press "{key}"'))
def press(key, app, event_loop):
    event_loop.run_until_complete(app.post_message(Key(app, key=key)))
    event_loop.run_until_complete(asyncio.sleep(0.1))


@then(parsers.parse('I see "{text}" on screen'))
def see(text, app):
    assert re.search(text, screen(app))


def screen(app):
    return app.console.file.getvalue()
