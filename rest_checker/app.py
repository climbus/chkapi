import sys
import timeit

from textual import events
from textual.app import App

from rest_checker.api_reader import URL, APIReader, AsyncAPIReader
from rest_checker.exceptions import BadUrlException, HttpError
from rest_checker.views import ContentView, URLView
from rest_checker.widgets import ApiFooter, CommandPrompt, MessageWidget


class RestChecker(App):
    api_reader: APIReader

    footer: ApiFooter
    url_view: URLView
    body: ContentView
    command_prompt: CommandPrompt
    message: MessageWidget

    def __init__(self, url: str = "", **kwargs):
        super().__init__(**kwargs)
        self.url = url
        self.api_reader = AsyncAPIReader()

    @classmethod
    def run(cls, url=None):
        super().run(title="Rest Checker", log="textual.log", url=url)

    async def on_mount(self):
        self.body = ContentView()
        self.url_view = URLView(self.url)
        self.footer = ApiFooter()
        self.command_prompt = CommandPrompt()
        self.message = MessageWidget()
        await self.view.dock(self.url_view, size=3, edge="top")
        await self.view.dock(self.message, size=3, edge="top", z=1)
        await self.view.dock(self.footer, edge="bottom")
        await self.view.dock(self.body, edge="top")
        await self.view.dock(self.command_prompt, size=3, edge="bottom", z=1)

    async def load_url(self, url):
        try:
            content, response_time = await self._get_content_with_time(url)
        except (HttpError, BadUrlException) as e:
            return self.message.show_message(str(e))
        await self.body.set_content(content)
        await self.bind("/", "search")
        self.footer.response_time = response_time
        await self.body.focus()

    async def _get_content_with_time(self, url):
        start = timeit.default_timer()
        content = await self._get_url_content(url)
        response_time = timeit.default_timer() - start
        return (content, response_time)

    async def on_load(self):
        await self.bind("q", "quit")

    async def handle_url_changed(self):
        await self.load_url(self.url_view.url)

    async def handle_cancel_search(self):
        await self.body.clear_search_results()

    async def handle_finish_search(self):
        await self.body.focus()
        await self.bind("n", "next_result")

    async def on_search(self, event):
        await self.body.search(event.value)

    async def on_key(self, event: events.Key) -> None:
        if event.key == "ctrl+l":
            await self.url_view.focus()
        if event.key == "escape":
            await self.body.focus()
        return await super().on_key(event)

    async def action_search(self):
        await self.command_prompt.show()

    async def _get_url_content(self, url):
        return await self.api_reader.read_url(URL(url))


if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else None
    RestChecker.run(url)
