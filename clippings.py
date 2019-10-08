from collections import namedtuple, defaultdict
from datetime import datetime
import json
import pickle
import re
from typing import Mapping, Sequence

Clip = namedtuple("Clip", "book_title, author, location, date, text")
Hash = int


class NoteKeeper:
    def __init__(self) -> None:
        """
        The clippings objects stores all the notes and highlights found in
        the Amazon clippings text file usually named 'My Clippings.txt'.

        Information is stored in a format that allows for quick search by
        book and by author, where known.

        In addition, we can easily export and read from CSV.
        """
        self._clippings: Mapping[Hash, Clip] = {}
        self._book_search: Mapping[str, Mapping[str, Sequence[Hash]]] = {}
        self._author_search: Mapping[str, Sequence[Hash]] = defaultdict(list)

    def load_from_file(self, clippings_filepath: str) -> None:
        """
        Loads the clippings from the Amazon Kindle 'My Clippings.txt' file.

        Works off the assumption that every highlight or note contains
        5 lines of information:
            Line 1: book & author
            Line 2: Page location, date added
            Line 3: Blank line
            Line 4: The highlight / note
            Line 5: Note Break
        """
        with open(clippings_filepath) as f:
            f.readline(1)  # Skip first line
            highlights = [line.strip() for line in f]

        highlight_length = 5
        for line_number, info in enumerate(highlights):
            if line_number % highlight_length == 0:
                book = self._extract_book_title(info)
                author = self._extract_author_name(info)

            elif line_number % highlight_length == 1:
                location = self._extract_location_number(info)
                date = self._extract_date(info)

            elif line_number % highlight_length == 3:
                text = info

            elif line_number % highlight_length == 4:
                clip = Clip(book, author, location, date, text)
                clip_hash = hash(clip)
                self._clippings[clip_hash] = clip

                # TODO: Fix this so it adds a default list. What happens if
                # author is unknown? Make this compatible with multiple authors
                self._book_search[book][author] = clip_hash

                if author != "unknown":
                    self._author_search[author].append(clip)

    def _extract_date(self, date_line):
        """
        Extracts the date from a highlight in the 'My Clippings.txt' file using regular expressions.

        Dates are recorded on the second line of a highlight in the following format:
        '- Your Highlight on page 43 | location 973-974 | Added on Thursday, 28 January 2016 08:33:31'

        :param date_line: the string that contains the date of the highlight in the kindle file
        :return: datetime object. Min if can't find a match
        """
        p = re.compile("\d{2}\s\D+\s\d{4}\s\d{2}:\d{2}:\d{2}", re.IGNORECASE)
        match = re.search(p, date_line)

        if match is None:
            return datetime.min
        else:
            return datetime.strptime(match.group(0), "%d %B %Y %H:%M:%S")

    def _extract_book_title(self, book_and_author_string):
        """
        Returns the book title from the book and author line in the Kindle 'My Clippings.txt' file.

        The format is generally 'book title (author last name, author first name)'
        e.g. Influence (Cialdini PhD, Robert B.)

        Sometimes, the publisher is added so that the format is 'book title (publisher) (author last name, author first name)'
        Influence (Collins Business Essentials) (Cialdini PhD, Robert B.)

        :param book_and_author_string: string that contains the book and the author's name
        :return: string, title of the book
        """

        ind = book_and_author_string.find("(")
        if ind == -1:
            return book_and_author_string.strip()

        else:
            return book_and_author_string[:ind].strip()

    def _extract_author_name(self, book_and_author_string):
        """
        Returns the author name from the book and author line in the Kindle 'My Clippings.txt' file.

        The format is generally 'book title (author last name, author first name)'
        e.g. Influence (Cialdini PhD, Robert B.)

        Sometimes, the publisher is added so that the format is 'book title (publisher) (author last name, author first name)'
        Influence (Collins Business Essentials) (Cialdini PhD, Robert B.)

        If the author has no last name, then the name as is is returned

        :param book_and_author_string: string that contains the book and the author's name
        :return: string, '<first name> <last name>' as presented in the file
        """
        open_bracket = book_and_author_string.rfind("(")
        close_bracket = book_and_author_string.rfind(")")

        if open_bracket == -1:
            name = "unknown_" + str(self.num_unknowns)
            self.num_unknowns += 1
            return name

        author_full_name = book_and_author_string[
            open_bracket + 1 : close_bracket
        ]

        # Empty string
        if not author_full_name:
            name = "unknown_" + str(self.num_unknowns)
            self.num_unknowns += 1
            return name

        author_full_name = author_full_name.split(";")[0]  # Get first author
        author_full_name = author_full_name.split(
            ","
        )  # Author names are usually written as '<first name>, <last name>'

        if len(author_full_name) == 1:
            return author_full_name[0]
        else:
            first_name = author_full_name[1].strip()
            last_name = author_full_name[0].strip()
            return " ".join([first_name, last_name])

    def get_booklist(self, author=None):
        """
        Returns a list of books. If author is specified, returns the books from that author.

        :param author: string, the name of the author
        :return: list of strings
        """

        if author is None:
            return list(self.book_clippings.keys())

        if self.library.get(author) is None:
            raise Exception("{} is not a valid author name.".format(author))

        return list(self.library[author])

    def get_book_clippings(self, book):
        """
        Returns all the clippings for a book

        :param book: string, the name of the book
        :return: array of strings
        """

        if self.book_clippings.get(book) is None:
            raise Exception("{} is not a valid book.".format(book))

        return self.book_clippings[book][1]

    def get_book_author(self, book):
        """
        Returns the author of a book

        :param book: string, the name of the book
        :return: string, author
        """

        if self.library.get(book) is None:
            raise Exception("{} is not a valid book.".format(book))

        return self.book_clippings[book][0]

    def save_json(self, file):
        """
        Saves the book clippings dict, library dict and last modified data to a json file

        :param file: path to json file
        :return: None
        """

        data = {
            "book_clippings": self.book_clippings,
            "library": self.library,
            "last_modified_date": self.last_modified_date,
        }

        with open(file, "w") as f:
            print("Saving data to", file)
            json.dump(data, f)

    def load_json(self, file):
        """
        Loads the book clippings dict, library dict and last modified data from a json file

        :param file: path to pickle file
        :return: None
        """

        with open(file, "rb") as f:
            print("Loading data history from", file)
            data = json.load(f)

        self.last_modified_date = data["last_modified_date"]
        self.library = data["library"]
        self.book_clippings = data["book_clippings"]

    def save_pickle(self, file):
        """
        Saves the book clippings dict, library dict and last modified data to a pickle file

        :param file: path to pickle file
        :return: None
        """

        data = {
            "book_clippings": self.book_clippings,
            "library": self.library,
            "last_modified_date": self.last_modified_date,
        }

        with open(file, "wb") as f:
            print("Saving data to", file)
            pickle.dump(data, f)

    def load_pickle(self, file):
        """
        Loads the book clippings dict, library dict and last modified data from a pickle file

        :param file: path to pickle file
        :return: None
        """

        with open(file, "rb") as f:
            print("Loading data history from", file)
            data = pickle.load(f)

        self.last_modified_date = data["last_modified_date"]
        self.library = data["library"]
        self.book_clippings = data["book_clippings"]

    def write_to_file(self, book, file):
        """
        Writes all the clippings in the book specified to a text file

        :param book: string, name of the book
        :param file: string, full file path
        :return: None
        """

        clippings = self.get_book_clippings(book)

        with open(file, "w") as f:
            for line in clippings:
                f.write(line + "\n")

    def write_to_evernote(self, book):
        pass
