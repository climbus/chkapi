from typing import Optional

import rich.repr
from textual.events import InputEvent
from textual.message import Message, MessageTarget


class Search(InputEvent):

    __slots__ = ["key"]

    def __init__(self, sender: MessageTarget, value: Optional[str]) -> None:
        super().__init__(sender)
        self.value = value

    def __rich_repr__(self) -> rich.repr.Result:
        yield "value", self.value


class CancelSearch(Message):
    pass


class FinishSearch(Message):
    pass


class UrlChanged(Message, bubble=True):
    pass
