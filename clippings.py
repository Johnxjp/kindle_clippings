from collections import namedtuple, defaultdict
from datetime import datetime
import json
import pickle
import re
from typing import Mapping, Sequence, Tuple, Optional

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

        n_lines_per_clip = 5
        for line_number, info in enumerate(highlights):
            if line_number % n_lines_per_clip == 0:
                book, author = self._extract_title_and_author(info)
                if author is None:
                    author = "unknown"

            elif line_number % n_lines_per_clip == 1:
                location = self._extract_location_number(info)
                date = self._extract_date(info)

            elif line_number % n_lines_per_clip == 3:
                text = info

            elif line_number % n_lines_per_clip == 4:
                clip = Clip(book, author, location, date, text)
                clip_hash = hash(clip)
                self._clippings[clip_hash] = clip

                if not self._book_search.get(book, False):
                    self._book_search[book] = {author: [clip_hash]}
                elif not self._book_search[book].get(author, False):
                    self._book_search[book][author] = [clip_hash]
                else:
                    self._book_search[book][author].append(clip_hash)

                if author is not None:
                    self._author_search[author].append(clip)

    def _extract_title_and_author(
        self, line: str
    ) -> Tuple[str, Optional[str]]:
        """
        Returns the title and author from the first line
        of a clip.

        The format is generally 'book title
        (author last name, author first name)'
        e.g. Influence (Cialdini PhD, Robert B.)

        Sometimes, the publisher is added so that the format is
        'book title (publisher) (author last name, author first name)'
        Influence (Collins Business Essentials) (Cialdini PhD, Robert B.)
        """
        ind = line.find("(")
        if ind == -1:
            return line.strip(), None

        book = line[:ind].strip()
        author = self._extract_author_name(line[ind:])
        return book, author

    def _extract_date(self, date_line):
        """
        Extracts the date from a highlight in the 'My Clippings.txt'
        file using regular expressions.

        Dates are recorded on the second line of a
        highlight in the following format:
        '- Your Highlight on page 43 | location 973-974 |
        Added on Thursday, 28 January 2016 08:33:31'
        """
        p = re.compile("\d{2}\s\D+\s\d{4}\s\d{2}:\d{2}:\d{2}", re.IGNORECASE)
        match = re.search(p, date_line)

        if match is None:
            return datetime.min
        else:
            return datetime.strptime(match.group(0), "%d %B %Y %H:%M:%S")

    def _extract_author_name(self, line: str) -> Optional[str]:
        """
        Returns the authors name extracted as `<first name> <other names>`

        If there are multiple authors it returns "<author 1> & <author 2> .."
        """
        open_bracket = line.rfind("(")
        close_bracket = line.rfind(")")

        if open_bracket == -1:
            return None

        author = line[open_bracket + 1 : close_bracket]

        # Empty string
        if len(author) == 0:
            return None

        # Handle case with multiple authors
        # Author names are usually written as '<first name>, <last name>'
        authors = author.split(";")
        formatted_names = [self._swap_parts_of_name(name) for name in authors]
        return " & ".join(formatted_names)

    def _swap_parts_of_name(self, name: str) -> str:
        """
        Reformats the author name from `<last names>, <first name>`
        to `<first name> <last name>`
        """
        names = name.split(",")
        if len(names) == 1:
            return names[0]

        first_name = names[1].strip()
        last_names = names[0].strip()
        return f"{first_name} {last_names}"

    def get_booklist(self, author=None):
        """
        Returns a list of books. If author is specified, returns the books
        from that author.

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
        Saves the book clippings dict, library dict and last modified data
        to a json file

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
        Loads the book clippings dict, library dict and last modified data
        from a json file

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
        Saves the book clippings dict, library dict and last modified data to
        a pickle file

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
        Loads the book clippings dict, library dict and last modified data
        from a pickle file

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
