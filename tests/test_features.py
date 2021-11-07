import asyncio
import json
import os
import re
import tempfile
from asyncio.futures import Future
from io import StringIO
from unittest.mock import MagicMock, Mock

import pytest
from pytest_bdd import given, parsers, scenarios, then, when
from rich.console import Console
from textual.events import Key

from chkapi.api_reader import Response
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


scenarios("../features")


@given(parsers.parse('I pressed "{key}"'))
@when(parsers.parse('I press "{key}"'))
def press(key, app, event_loop):
    new_screen_capture(app)
    event_loop.run_until_complete(app.post_message(Key(app, key=key)))
    event_loop.run_until_complete(asyncio.sleep(0.2))


@given(parsers.parse('I wrote "{text}"'))
@when(parsers.parse('I write "{text}"'))
def write(text, app, event_loop):
    new_screen_capture(app)
    for key in text:
        event_loop.run_until_complete(app.post_message(Key(app, key=key)))
    event_loop.run_until_complete(asyncio.sleep(0.2))


@given("server responds with error")
def server_responds_with_error(app):
    exception = HttpError("Connection Error")
    app.api_reader.read_url.return_value.set_exception(exception)


@given(parsers.parse("server responds with data\n{data}"))
def server_responds_with_data(data, app):
    response = Response(data, headers={})
    app.api_reader.read_url.return_value.set_result(response)


@given(parsers.parse("server responds with headers\n{headers}"))
def server_responds_with_headers(headers, app):
    response = Response("{}", headers=json.loads(headers))
    app.api_reader.read_url.return_value.set_result(response)


@given(parsers.parse('url "{url}" was used in the past'))
def url_was_used(url, app, event_loop):
    press("ctrl+l", app, event_loop)
    write(url, app, event_loop)
    press("enter", app, event_loop)
    press("ctrl+l", app, event_loop)
    delete(url, app, event_loop)


def delete(text, app, event_loop):
    for _ in range(len(text)):
        event_loop.run_until_complete(app.post_message(Key(app, key="ctrl+h")))


@given("I focused url field")
def focus_url_field(app, event_loop):
    event_loop.run_until_complete(app.post_message(Key(app, key="ctrl+l")))
    event_loop.run_until_complete(asyncio.sleep(0.2))


@then(parsers.parse('I see "{text}" on screen'))
def see(text, app):
    assert re.compile(text).search(screen(app)), f'"{text}" not found'


@then(parsers.parse('I don\'t see "{text}" on screen'))
def dont_see(text, app):
    app.refresh()
    assert "URL" in screen(app)
    assert not re.search(text, screen(app)), f'"{text} found'


@then(parsers.parse('url "{url}" is selected'))
def url_is_selected(url, app):
    see(f"31;43m{url}", app)


@when("log screen")
@then("log screen")
def log_screen(app):
    app.log(screen(app))


def screen(app):
    return app.console.file.getvalue()


def new_screen_capture(app):
    app.console.file.truncate(0)
