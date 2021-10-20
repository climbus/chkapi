import sys
import timeit
from typing import Optional, cast

from rich import align, box
from rich.align import Align
from rich.console import Group, RenderableType
from rich.json import JSON
from rich.panel import Panel
from rich.text import Text
from textual import events
from textual.app import App
from textual.view import View
from textual.views import GridView
from textual.widget import Reactive, Widget
from textual.widgets import Button, Footer, ScrollView
from textual_inputs import TextInput

from rest_checker.api_reader import URL, APIReader, AsyncAPIReader
from rest_checker.events import UrlChanged
from rest_checker.exceptions import BadUrlException, HttpError


class ApiFooter(Footer):
    response_time: Reactive[Optional[float]] = Reactive(None)

    def on_mount(self):
        self.response_time = None

    def render(self) -> RenderableType:
        content = cast(Text, super().render())
        if self.response_time:
            return Text.assemble(
                content,
                Text(
                    f"Response time: {self.response_time:.2f}s",
                    style="white on dark_green",
                    justify="right",
                ),
            )
        return content


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
    label: str = "GO"

    def __init__(self, label=label):
        super().__init__(label=label)

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

    async def on_click(self, event: events.Click) -> None:
        self.has_focus = False
        await self.emit(UrlChanged(self))


class URLView(GridView):
    url_field: URLField
    button: Button

    def __init__(self, url: str) -> None:
        super().__init__()
        self.url_field = URLField(url)
        self.button = URLButton()

    async def on_mount(self):
        self.grid.add_column("url")
        self.grid.add_column("button", size=10)
        self.grid.add_row("main", size=3)
        self.grid.add_areas(url="url,main", button="button,main")
        self.grid.place(url=self.url_field)
        self.grid.place(button=self.button)

    @property
    def url(self):
        return self.url_field.url

    async def on_focus(self):
        await self.url_field.focus()


class RestChecker(App):
    api_reader: APIReader

    footer: ApiFooter
    url_view: URLView
    body: ScrollView

    def __init__(self, url: str="", **kwargs):
        super().__init__(**kwargs)
        self.url = url
        self.api_reader = AsyncAPIReader()

    @classmethod
    def run(cls, url=None):
        super().run(title="Rest Checker", log="textual.log", url=url)

    async def on_mount(self):
        self.body = ScrollView()
        self.url_view = URLView(self.url)
        self.footer = ApiFooter()
        await self.view.dock(self.url_view, size=3, edge="top")
        await self.view.dock(self.footer, edge="bottom")
        await self.view.dock(self.body, edge="top")

    async def load_url(self, url):
        try:
            content, response_time = await self._get_content_with_time(url)
        except HttpError as e:
            content = self._error_message(str(e))
            response_time = None
        except BadUrlException as e:
            content = self._error_message(str(e))
            response_time = None

        await self.body.update(content)
        self.footer.response_time = response_time

    async def _get_content_with_time(self, url):
        start = timeit.default_timer()
        content = JSON(await self._get_url_content(url))
        response_time = timeit.default_timer() - start
        return (content, response_time)

    def _error_message(self, e: str):
        return Panel(Align.center(e), style="red on black")

    async def on_load(self):
        await self.bind("q", "quit")

    async def handle_url_changed(self):
        await self.load_url(self.url_view.url)

    async def on_key(self, event: events.Key) -> None:
        if event.key == "ctrl+l":
            await self.url_view.focus()
        return await super().on_key(event)

    async def _get_url_content(self, url):
        return await self.api_reader.read_url(URL(url))


if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else None
    RestChecker.run(url)
