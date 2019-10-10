import random

from faker import Faker

import pytest
from clips import Clip, ClipList

DATA_CREATOR = Faker()


def random_data() -> Clip:
    book = DATA_CREATOR.sentence(nb_words=2)
    author = DATA_CREATOR.name()
    start_location = DATA_CREATOR.random_number()
    end_location = DATA_CREATOR.random_number()
    date = DATA_CREATOR.date_object()
    text = DATA_CREATOR.text()
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
