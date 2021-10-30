from copy import deepcopy

from rich.json import JSON
from textual.views import GridView
from textual.widgets import Button, ScrollView

import chkapi.widgets
from chkapi.search import EmptySearchResults, SearchResults


class URLView(GridView):
    url_field: chkapi.widgets.URLField
    button: Button

    def __init__(self, url: str) -> None:
        super().__init__()
        self.url_field = chkapi.widgets.URLField(url)
        self.button = chkapi.widgets.URLButton()

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
    search_results = EmptySearchResults()

    async def set_content(self, content):
        self.content = JSON(content)
        self.raw_content = content
        await self.update(self.content)

    async def search(self, value):
        if self.content:
            self.search_results = SearchResults(value, self.content.text.plain)
            content = self._highlight_found_phrases()
            await self.update(content, home=False)
            self._scroll_to_selected(content)

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
        await self.update(content, home=False)
        self._scroll_to_selected(content)

    def _scroll_to_selected(self, content):
        if len(self.search_results) > 0:
            start = self.search_results.selected().start
            self.scroll_to_center(self._lineno_from_offset(start, content))

    async def on_key(self, event):
        if event.key == "n":
            if len(self.search_results) > 0:
                await self.jump_to_next_search_result()
        if event.key == "escape":
            if self.search_results:
                self.search_results.clear()
                await self.update(self.content)
                await self.app.unbind("n")

    def _lineno_from_offset(self, offset, content):
        return len(content.text[:offset].split("\n"))
