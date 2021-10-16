import sys

from requests import request
from rich import box
from rich.align import Align
from rich.panel import Panel
from textual.app import App
from textual.views import GridView
from textual.widget import Reactive
from textual.widgets import Button, Placeholder, ScrollView
from textual_inputs import TextInput


class URLField(TextInput):
    url: str

    def __init__(self, url):
        self.url = url
        super().__init__(value=url, title="URL")

    def set_url(self, url):
        self.url = url
        self.value = url


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
    url: str

    def __init__(self, url: str = "") -> None:
        self.url = url
        super().__init__()

    async def on_mount(self):
        self.grid.add_column("url")
        self.grid.add_column("button", size=10)
        self.grid.add_row("main", size=3)
        self.grid.add_areas(url="url,main", button="button,main")
        self.grid.place(url=URLField(self.url))
        self.grid.place(button=URLButton(label="GO"))


class RestChecker(App):
    async def on_mount(self):
        url_view = URLView(self.url)
        await self.view.dock(url_view, size=3, edge="top")
        await self.view.dock(Placeholder(name="body"), edge="bottom")

        async def load_url():
            self.log(f"loads: {self.url}")
            # content = self._get_url_content()
            # await self.body.update(JSON(content.text))
            self.log("url loaded")

        await self.call_later(load_url)

    async def on_load(self):
        await self.bind("q", "quit")

        self.url = self._get_url_from_attrs()

        self.body = ScrollView()
        self.url_field = URLField(self.url)

    def _get_url_content(self):
        return request("get", self.url)

    def _get_url_from_attrs(self) -> str:
        return sys.argv[1]


RestChecker.run(title="Rest Checker", log="textual.log")
