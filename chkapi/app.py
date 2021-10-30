import sys
import timeit

from textual import events
from textual.app import App

from chkapi.api_reader import URL, APIReader, AsyncAPIReader
from chkapi.exceptions import BadUrlException, HttpError
from chkapi.views import ContentView, URLView
from chkapi.widgets import ApiFooter, CommandPrompt, HeadersWidget, MessageWidget


class CheckApiApp(App):
    api_reader: APIReader

    footer: ApiFooter
    url_view: URLView
    body: ContentView
    command_prompt: CommandPrompt
    message: MessageWidget
    headers: HeadersWidget

    def __init__(self, url: str = "", api_reader=None, **kwargs):
        super().__init__(**kwargs)
        self.url = url
        self.api_reader = api_reader or AsyncAPIReader()

    @classmethod
    def run(cls, url=None):
        super().run(title="Rest Checker", log="textual.log", url=url)

    async def on_mount(self):
        self.body = ContentView()
        self.url_view = URLView(self.url)
        self.footer = ApiFooter()
        self.command_prompt = CommandPrompt()
        self.message = MessageWidget()
        self.headers = HeadersWidget()
        await self.view.dock(self.url_view, size=3, edge="top")
        await self.view.dock(self.message, size=3, edge="top", z=1)
        await self.view.dock(self.headers, edge="top", z=1)
        await self.view.dock(self.footer, edge="bottom")
        await self.view.dock(self.body, edge="top")
        await self.view.dock(self.command_prompt, size=3, edge="bottom", z=1)

    async def load_url(self, url):
        if not url:
            return self.message.show("Url is required")
        try:
            content, response_time = await self._get_content_with_time(url)
        except (HttpError, BadUrlException) as e:
            self.message.show(str(e))
            return False
        await self.body.set_content(content)
        self.footer.response_time = response_time
        await self.body.focus()
        return True

    async def _get_content_with_time(self, url):
        start = timeit.default_timer()
        self.response = await self._get_url_content(url)
        response_time = timeit.default_timer() - start
        return (self.response.body, response_time)

    async def bind(self, keys: str, action: str, description: str = "") -> None:
        await super().bind(keys, action, description=description)
        if hasattr(self, "footer"):
            self.footer.update_keys()
            self.footer.refresh()

    async def unbind(self, key):
        self.bindings.keys.pop(key)
        self.footer.update_keys()

    async def on_load(self):
        await self.bind("q", "quit", "Quit")

    async def handle_url_changed(self):
        loaded = await self.load_url(self.url_view.url)
        if loaded:
            await self.bind("/", "search", "Search")
            await self.bind("h", "show_headers", "Headers")

    async def handle_cancel_search(self):
        await self.body.clear_search_results()

    async def handle_finish_search(self):
        await self.body.focus()
        await self.bind("n", "next_result", "Next")

    async def on_search(self, event):
        await self.body.search(event.value)

    async def on_key(self, event: events.Key) -> None:
        if event.key == "ctrl+l":
            await self.url_view.focus()
        if event.key == "escape":
            self.message.hide()
            await self.body.focus()
        return await super().on_key(event)

    async def action_search(self):
        await self.command_prompt.show()

    async def action_show_headers(self):
        self.headers.show(self.response.headers)
        await self.headers.focus()

    async def _get_url_content(self, url):
        return await self.api_reader.read_url(URL(url))



def main():
    url = sys.argv[1] if len(sys.argv) > 1 else ""
    CheckApiApp.run(url)

if __name__ == "__main__":
    main()
