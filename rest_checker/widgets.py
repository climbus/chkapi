from typing import Optional, cast

from rich import box
from rich.align import Align
from rich.console import RenderableType
from rich.panel import Panel
from rich.text import Text
from textual import events, message
from textual.widget import Reactive, Widget
from textual.widgets import Button, Footer
from textual_inputs import TextInput

from rest_checker.events import CancelSearch, FinishSearch, Search, UrlChanged


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

    async def on_click(self) -> None:
        self.has_focus = False
        await self.emit(UrlChanged(self))


class URLField(TextInput):
    def __init__(self, url):
        super().__init__(value=url, title="URL")

    @property
    def url(self) -> str:
        return self.value

    async def on_key(self, event: events.Key) -> None:
        if event.key == "enter":
            await self.emit(UrlChanged(self))


class CommandPrompt(TextInput):
    def on_mount(self):
        self.visible = False

    async def show(self):
        self.visible = True
        await self.focus()

    async def hide(self):
        self.visible = False
        self.value = ""

    async def on_key(self, event: events.Key) -> None:
        event.prevent_default().stop()
        await super().on_key(event)
        if event.key == "escape":
            await self.hide()
            await self.emit(CancelSearch(self))
            return
        if event.key == "enter":
            await self.hide()
            await self.emit(FinishSearch(self))
            return
        await self.emit(Search(self, self.value))


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


class MessageWidget(Widget):
    message: RenderableType

    def on_mount(self):
        self.visible = False
        self.layout_offset_y = 5

    def show_message(self, message: str):
        self.message = message
        self.visible = True

    def render(self) -> RenderableType:
        return Panel(Align.center(self.message), style="red on black")


class HeadersWidget(Widget):
    headers: dict

    def on_mount(self):
        self.visible = False

    def show(self, headers: dict):
        self.headers = headers
        self.visible = True

    def render(self) -> RenderableType:
        return Panel("\n".join(f"{key} {val}" for key, val in self.headers.items()))
