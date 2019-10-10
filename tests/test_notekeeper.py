import pytest
from datetime import datetime

from notekeeper import NoteKeeper
from clips import Clip, ClipList


@pytest.fixture
def notekeeper():
    nk = NoteKeeper()
    nk._clippings = {
        1: Clip("book1", "author1", 1, 1, datetime.min, ""),
        2: Clip("book2", "author2", 1, 1, datetime.min, ""),
    }
    nk._bookclip_map = {"book1": {1}, "book2": {2}}
    return nk


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
                "=========",
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
def test_extract_clip(input, expected):
    clip = NoteKeeper._extract_clip(input)
    assert clip == expected


@pytest.mark.parametrize("book", [("book1"), ("book2")])
def test_get_book_clippings_book_exists(notekeeper, book):
    cl = notekeeper._get_book_clippings(book)
    assert len(cl) > 0
    assert all([item.book == book for item in cl])


@pytest.mark.parametrize("book", [(None)])
def test_get_book_clippings_book_doesnt_exist(notekeeper, book):
    cl = notekeeper._get_book_clippings(book)
    assert len(cl) == 0


def test_get_clippings_nobook(notekeeper):
    cl = notekeeper.get_clippings()
    assert len(cl) == len(notekeeper._clippings)
    assert isinstance(cl, ClipList)


@pytest.mark.parametrize("book", [("book1"), ("book2")])
def test_get_clippings_book(notekeeper, book):
    cl = notekeeper.get_clippings(book)
    assert isinstance(cl, ClipList)
    assert all([item.book == book for item in cl])


@pytest.mark.parametrize(
    "book, clips_in_file", [(None, 2), ("book1", 1), ("book2", 1)]
)
def test_export_csv(tmp_path, notekeeper, book, clips_in_file):
    file = f"{tmp_path}/tmpfile.csv"
    notekeeper.export_csv(file, book)
    assert len(list(tmp_path.iterdir())) == 1
    with open(file) as f:
        content = f.readlines()

    assert len(content) == clips_in_file + 1
