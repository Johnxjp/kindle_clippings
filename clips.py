from __future__ import annotations

from collections import namedtuple
from operator import attrgetter
from typing import Sequence

Clip = namedtuple(
    "Clip", "book, author, start_location, end_location, date, text"
)

# TODO: Create List of clips class that is a template of list.
# Properties incude things like sort by attribute, filter etc.


class ClipList(list):
    def __init__(self, clips: Sequence[Clip] = []) -> None:
        super().__init__(clips)

    def sortby(self, attribute: str) -> None:
        sorted(self, key=attrgetter(attribute))

    def filterby(self, attribute: str, value: str) -> ClipList:
        newlist = ClipList()
        for clip in self:
            if clip.__getattribute__(attribute) == value:
                newlist.append(clip)

        return newlist