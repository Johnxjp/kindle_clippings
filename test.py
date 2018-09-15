import unittest
from clippings_new import Clippings

testKD = Clippings()

class ClippingsTest(unittest.TestCase):

    def test_author_extract(self):
        author_string = "Forbes (Forbes)"
        assert testKD._extract_author_name(author_string) == "Forbes"

        author_string = "The Richest Man in Babylon (Clason, George S.)"
        assert testKD._extract_author_name(author_string) == "George S. Clason"

        author_string = "The 48 Laws Of Power"
        print(testKD._extract_author_name(author_string))
        assert testKD._extract_author_name(author_string) == ("unknown_" + str(testKD.num_unknowns - 1))

        author_string = "The 48 Laws Of Power ()"
        assert testKD._extract_author_name(author_string) == "unknown_" + str(testKD.num_unknowns - 1)

    def test_booktitle_extract(self):
        author_string = "Forbes (Forbes)"
        assert testKD._extract_book_title(author_string) == "Forbes"

        author_string = "The Richest Man in Babylon (Clason, George S.)"
        assert testKD._extract_book_title(author_string) == "The Richest Man in Babylon"

        author_string = "The 48 Laws Of Power (The Robert Greene Collection) (Greene, Robert)"
        assert testKD._extract_book_title(author_string) == "The 48 Laws Of Power"

        author_string = "The 48 Laws Of Power"
        assert testKD._extract_book_title(author_string) == "The 48 Laws Of Power"

    def test_extract_date(self):
        date_string = "- Your Highlight on page 43 | location 973-974 | Added on Thursday, 28 January 2016 08:33:31"
        print(testKD._extract_date(date_string))

        date_string = "28 february 2016 08:33:31"
        print(testKD._extract_date(date_string))

    def test_load_from_text(self):
        file = "test.txt"
        expected_library = {'Mi Kaku': {'book2'}, 'Kaku': {'book1'}}
        expected_clippings = {'book2': ['Mi Kaku', ['xxx2']], 'book1': ['Kaku', ['xxx3', 'xx1']]}

        testKD.load_from_text(file)
        assert testKD.library == expected_library
        assert testKD.book_clippings == expected_clippings

        booklist = testKD.get_booklist()
        assert booklist == ["book2", "book1"]

        booklist = testKD.get_booklist("Kaku")
        assert booklist == ["book1"]




