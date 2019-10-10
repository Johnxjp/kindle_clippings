from __future__ import annotations

from collections import namedtuple
from operator import attrgetter
from typing import Sequence, Optional

Clip = namedtuple(
    "Clip", "book, author, start_location, end_location, date, text"
)


class ClipList(list):
    def __init__(self, clips: Sequence[Clip] = []) -> None:
        super().__init__(clips)

    def sortby(self, attribute: str, inplace=True) -> Optional[None]:
        if inplace:
            self.sort(key=attrgetter(attribute))
        else:
            return sorted(self, key=attrgetter(attribute))

    def filterby(self, attribute: str, value: str) -> ClipList:
        newlist = ClipList()
        for clip in self:
            if getattr(clip, attribute) == value:
                newlist.append(clip)

        return newlist
