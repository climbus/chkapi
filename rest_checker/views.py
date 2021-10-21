from textual.views import GridView
from textual.widgets import Button

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
