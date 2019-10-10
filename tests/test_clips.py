import random
import string

import pytest
import datetime
from datetime import datetime as dt
from clips import Clip, ClipList


def random_string(n_chars) -> str:
    letters = string.ascii_letters
    return "".join([random.choice(letters) for _ in range(n_chars)])


def random_data() -> Clip:
    book = random_string(random.randint(0, 10))
    author = random_string(random.randint(0, 10))
    start_location = random.randint(0, 1000)
    end_location = random.randint(0, 1000)
    date = dt.min + datetime.timedelta(days=random.randint(0, 1000))
    text = random_string(random.randint(0, 10))
    return Clip(book, author, start_location, end_location, date, text)


@pytest.fixture
def data():
    return ClipList([random_data() for _ in range(5)])


@pytest.mark.parametrize(
    "attribute",
    [
        ("book"),
        ("author"),
        ("start_location"),
        ("end_location"),
        ("date"),
        ("text"),
    ],
)
def test_cliplist_sort_inplace(data, attribute):
    data.sortby(attribute)
    for i in range(1, len(data)):
        assert getattr(data[i], attribute) >= getattr(data[i - 1], attribute)


@pytest.mark.parametrize(
    "attribute",
    [
        ("book"),
        ("author"),
        ("start_location"),
        ("end_location"),
        ("date"),
        ("text"),
    ],
)
def test_cliplist_sort_not_inplace(data, attribute):
    new_data = data.sortby(attribute, inplace=False)
    for i in range(1, len(data)):
        assert getattr(new_data[i], attribute) >= getattr(
            new_data[i - 1], attribute
        )


@pytest.mark.parametrize(
    "attribute",
    [
        ("book"),
        ("author"),
        ("start_location"),
        ("end_location"),
        ("date"),
        ("text"),
    ],
)
def test_filterby(data, attribute):
    filter_value = getattr(random.choice(data), attribute)
    new_data = data.filterby(attribute, filter_value)

    assert len(new_data) <= len(data)
    for clip in new_data:
        assert getattr(clip, attribute) == filter_value
