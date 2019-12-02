import pytest
from datetime import datetime
from notekeeper import NoteKeeper
from clips import Clip, ClipList


@pytest.fixture
def notekeeper():
    return NoteKeeper()


@pytest.mark.parametrize(
    "input, expected",
    [
        ("lincoln, abraham", "abraham lincoln"),
        ("lincoln abraham", "lincoln abraham"),
        ("lincoln", "lincoln"),
        ("kennedy, john f.", "john f. kennedy"),
        ("f. kennedy, john", "john f. kennedy"),
        ("", ""),
    ],
)
def test_swap_parts_of_name(input, expected):
    names = NoteKeeper._swap_parts_of_name(input)
    assert names == expected


@pytest.mark.parametrize(
    "input, expected",
    [
        ("lincoln, abraham", None),
        ("(lincoln, abraham)", "abraham lincoln"),
        (
            "Autobiography of abraham lincoln (lincoln, abraham)",
            "abraham lincoln",
        ),
        (
            "Autobiography of abraham lincoln (Redhouse) (lincoln, abraham)",
            "abraham lincoln",
        ),
        ("Autobiography of abraham lincoln (Redhouse)", "Redhouse"),
        (
            "Autobiography of abraham lincoln (Redhouse; lincoln)",
            "Redhouse & lincoln",
        ),
    ],
)
def test_extract_author(input, expected):
    names = NoteKeeper._extract_author(input)
    assert names == expected


@pytest.mark.parametrize(
    "input, expected",
    [
        (
            "Autobiography of abraham lincoln",
            "Autobiography of abraham lincoln",
        ),
        (
            "Autobiography of abraham lincoln()",
            "Autobiography of abraham lincoln",
        ),
        ("(lincoln, abraham)", ""),
        (
            "Autobiography of abraham lincoln (lincoln, abraham)",
            "Autobiography of abraham lincoln",
        ),
        (
            "Autobiography of abraham lincoln (Redhouse) (lincoln, abraham)",
            "Autobiography of abraham lincoln",
        ),
        (
            "Autobiography of, abraham lincoln (Redhouse)",
            "Autobiography of, abraham lincoln",
        ),
    ],
)
def test_extract_book_title(input, expected):
    names = NoteKeeper._extract_book_title(input)
    assert names == expected


@pytest.mark.parametrize(
    "input, expected_start, expected_end",
    [
        ("location 12-12", 12, 12),
        ("location 12", 12, 12),
        ("location 12-56", 12, 56),
        ("location", 0, 0),
        ("Added at location 24", 24, 24),
        ("Added at location 24 today", 24, 24),
        ("Added at location 12-56 today", 12, 56),
        ("Added at location 12-56today", 12, 56),
    ],
)
def test_extract_location(input, expected_start, expected_end):
    start, end = NoteKeeper._extract_location(input)
    assert start == expected_start
    assert end == expected_end


@pytest.mark.parametrize(
    "input, expected_date",
    [
        (
            "Added on Thursday, 28 January 2016 08:33:31",
            datetime(2016, 1, 28, 8, 33, 31),
        ),
        (
            "Added on 28 January 2016 08:33:31",
            datetime(2016, 1, 28, 8, 33, 31),
        ),
        (
            "Added on 31 December 2018 13:33:33",
            datetime(2018, 12, 31, 13, 33, 33),
        ),
        ("", datetime.min),
    ],
)
def test_extract_date(input, expected_date):
    date = NoteKeeper._extract_date(input)
    assert date == expected_date


@pytest.mark.parametrize(
    "input, expected",
    [
        (
            [
                "Autobiography of Lincoln (lincoln, abraham)",
                "- Your Highlight location 1085-1086 | Added on Monday, 29 May 2016 10:00:31",
                "",
                "some text",
            ],
            Clip(
                "Autobiography of Lincoln",
                "abraham lincoln",
                1085,
                1086,
                datetime(2016, 5, 29, 10, 0, 31),
                "some text",
            ),
        )
    ],
)
def test_extract_clip(notekeeper, input, expected):
    clip = notekeeper._extract_clip(input)
    assert clip == expected


@pytest.mark.parametrize(
    "input, expected",
    [
        (
            [
                ("book1", 123),
                ("book1", 123),
                ("book2", 123),
                ("book3", 123),
                ("book2", 432),
            ],
            {"book1": {123}, "book2": {123, 432}, "book3": {123}},
        )
    ],
)
def test_update_book_map(notekeeper, input, expected):
    for book, clip_hash in input:
        notekeeper.update_book_search(book, clip_hash)

    assert notekeeper._bookclip_map == expected
