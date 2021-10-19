from dataclasses import dataclass
import sys
from typing import Protocol, cast
from warnings import resetwarnings

from requests import request
from rich import box
from rich.json import JSON
from rich.align import Align
from rich.panel import Panel
from rich.repr import Result
from textual.app import App
from textual.message import Message
from textual.views import GridView
from textual.widget import Reactive
from textual.widgets import Button, ButtonPressed, ScrollView
from textual_inputs import TextInput
from textual import events

import httpx


class UrlChanged(Message, bubble=True):
    pass


class URLField(TextInput):
    def __init__(self, url):
        super().__init__(value=url, title="URL")

    @property
    def url(self) -> str:
        return self.value

    async def on_key(self, event: events.Key) -> None:
        if event.key == "enter":
            await self.emit(UrlChanged(self))


class URLButton(Button, can_focus=True):
    has_focus: Reactive[bool] = Reactive(False)
    mouse_over: Reactive[bool] = Reactive(False)

    def render(self):
        return Panel(
            Align.center(self.label),
            box=box.HEAVY if self.mouse_over else box.ROUNDED,
            style="black on white" if self.has_focus else "white on black",
            height=3,
        )

    async def on_focus(self) -> None:
        self.has_focus = True

    async def on_blur(self) -> None:
        self.has_focus = False

    async def on_enter(self) -> None:
        self.mouse_over = True

    async def on_leave(self) -> None:
        self.mouse_over = False


class URLView(GridView):
    url_field: URLField

    def __init__(self, url: str = "") -> None:
        super().__init__()
        self.url_field = URLField(url)

    async def on_mount(self):
        self.grid.add_column("url")
        self.grid.add_column("button", size=10)
        self.grid.add_row("main", size=3)
        self.grid.add_areas(url="url,main", button="button,main")
        self.grid.place(url=self.url_field)
        self.grid.place(button=URLButton(label="GO"))

    @property
    def url(self):
        return self.url_field.url

    async def on_focus(self):
        await self.url_field.focus()


@dataclass
class URL(object):
    url: str


class APIReader(Protocol):
    async def read_url(self, url: URL) -> str:
        ...


class AsyncAPIReader(object):
    async def read_url(self, url: URL) -> str:
        async with httpx.AsyncClient() as client:
            result = await client.get(url.url)
            return result.text


class RestChecker(App):
    api_reader: APIReader

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api_reader = AsyncAPIReader()

    async def on_mount(self):
        self.url_view = URLView(self.url)
        self.body = ScrollView()
        await self.view.dock(self.url_view, size=3, edge="top")
        await self.view.dock(self.body, edge="bottom")

    async def load_url(self, url):
        self.log(f"Loading url {url}")
        content = await self._get_url_content(url)
        self.log(f"Response: {content}")
        await self.body.update(JSON(content))

    async def on_load(self):
        await self.bind("q", "quit")

        self.url = self._get_url_from_attrs()

        self.body = ScrollView()
        self.url_field = URLField(self.url)

    async def handle_button_pressed(self, message: ButtonPressed) -> None:
        button = cast(URLButton, message.sender)
        button.has_focus = False
        await self.load_url(self.url_view.url)

    async def handle_url_changed(self):
        await self.load_url(self.url_view.url)

    async def on_key(self, event: events.Key) -> None:
        if event.key == "ctrl+l":
            await self.url_view.focus()
        return await super().on_key(event)

    async def _get_url_content(self, url):
        return await self.api_reader.read_url(URL(url))

    def _get_url_from_attrs(self) -> str:
        if len(sys.argv) > 1:
            return sys.argv[1]
        else:
            return ""


if __name__ == "__main__":
    RestChecker.run(title="Rest Checker", log="textual.log")
