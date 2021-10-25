import re
from collections import namedtuple
from copy import deepcopy
from typing import List, Tuple

from rich.json import JSON
from textual.views import GridView
from textual.widgets import Button, ScrollView

import rest_checker.widgets


class URLView(GridView):
    url_field: rest_checker.widgets.URLField
    button: Button

    def __init__(self, url: str) -> None:
        super().__init__()
        self.url_field = rest_checker.widgets.URLField(url)
        self.button = rest_checker.widgets.URLButton()

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


class ContentView(ScrollView):
    content: JSON
    raw_content: str

    async def set_content(self, content):
        self.content = JSON(content)
        self.raw_content = content
        await self.update(self.content)

    async def search(self, value):
        if self.content:
            self.search_results = SearchResults(value, self.content.text.plain)
            content = self._highlight_found_phrases()
            await self.update(content)

    def _highlight_found_phrases(self):
        if len(self.search_results) == 0:
            return self.content
        content = deepcopy(self.content)
        for result in self.search_results.all():
            content.text.stylize("white on yellow", *result)
        content.text.stylize("red on yellow", *self.search_results.selected())
        return content

    async def clear_search_results(self):
        await self.focus()
        await self.update(self.content)

    async def jump_to_next_search_result(self):
        self.search_results.select_next()
        content = self._highlight_found_phrases()
        await self.update(content)

    async def on_key(self, event):
        if event.key == "n":
            await self.jump_to_next_search_result()


Occurrence = namedtuple("Occurence", "start stop")


class SearchResults:
    def __init__(self, value: str, content: str):
        self._selected: int = 0
        self._i: int = 0
        self._result: List[Occurrence] = [
            Occurrence(*res.span()) for res in re.finditer(value, content)
        ]
        self.value: str = value

    def select_next(self) -> Occurrence:
        if self._selected < len(self._result) - 1:
            self._selected += 1
        else:
            self._selected = 0
        return self._result[self._selected]

    def all(self) -> List[Occurrence]:
        return self._result

    def selected(self) -> Occurrence:
        return self._result[self._selected]

    def __len__(self) -> int:
        return len(self._result)
