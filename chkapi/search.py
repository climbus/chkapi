import re
from collections import namedtuple
from typing import List, Optional

Occurrence = namedtuple("Occurrence", "start stop")

class EmptySearchResults:
    def select_next(self) -> Optional[Occurrence]:
        return None

    def all(self) -> List[Occurrence]:
        return []

    def selected(self) -> Optional[Occurrence]:
        return None

    def __len__(self) -> int:
        return 0

    def clear(self):
        pass

class SearchResults:
    """
    >>> result = SearchResults("Ala", "Ala ma kota. Ala nie ma psa")
    >>> len(result) == 2
    True
    >>> result.all()
    [Occurrence(start=0, stop=3), Occurrence(start=13, stop=16)]
    >>> result.selected()
    Occurrence(start=0, stop=3)
    >>> result.select_next()
    Occurrence(start=13, stop=16)
    >>> result.selected()
    Occurrence(start=13, stop=16)
    >>> result.select_next()
    Occurrence(start=0, stop=3)
    >>> result.selected()
    Occurrence(start=0, stop=3)
    >>> result = SearchResults("Lump", "Ala ma kota")
    >>> len(result) == 0
    True
    >>> result.selected()
    >>> result.select_next()
    """

    def __init__(self, value: str, content: str):
        self._selected: int = 0
        self._i: int = 0
        self._result: List[Occurrence] = [
            Occurrence(*res.span()) for res in re.finditer(value, content)
        ]
        self.value: str = value

    def select_next(self) -> Optional[Occurrence]:
        if len(self) == 0:
            return
        if self._selected < len(self._result) - 1:
            self._selected += 1
        else:
            self._selected = 0
        return self._result[self._selected]

    def all(self) -> List[Occurrence]:
        return self._result

    def selected(self) -> Optional[Occurrence]:
        if len(self) == 0:
            return
        return self._result[self._selected]

    def __len__(self) -> int:
        return len(self._result)

    def clear(self):
        self._result = []
