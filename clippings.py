from collections import namedtuple, defaultdict
from datetime import datetime
import json
import pickle
import re
from typing import Mapping, Sequence, Tuple, Optional

Clip = namedtuple(
    "Clip", "book_title, author, start_location, end_location, date, text"
)
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
            highlights = [line.strip().lower() for line in f]

        n_lines_per_clip = 5
        for line_number, info in enumerate(highlights):
            if line_number % n_lines_per_clip == 0:
                book = self._extract_book_title(info)
                author = self._extract_author(info)
                if author is None:
                    author = "unknown"

            elif line_number % n_lines_per_clip == 1:
                start_location, end_location = self._extract_location(info)
                date = self._extract_date(info)

            elif line_number % n_lines_per_clip == 3:
                text = info

            elif line_number % n_lines_per_clip == 4:
                clip = Clip(
                    book, author, start_location, end_location, date, text
                )

                # Warning: hash value is truncated to bit value of machine
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

        print(f"Extracted {len(self._clippings)} from file.")

    @staticmethod
    def _extract_book_title(line: str) -> str:
        """
        Returns the title from the first line
        of a clip.

        The format is often 'book title (author last name, author first name)'
        e.g. Influence (Cialdini PhD, Robert B.)

        Sometimes, the publisher is also added in brackets between the
        book title and the author names e.g.
        Influence (Collins Business Essentials) (Cialdini PhD, Robert B.)
        Publisher information is ignored.
        """
        ind = line.find("(")
        if ind == -1:
            return line.strip()

        title = line[:ind].strip()
        return title

    @staticmethod
    def _extract_author(line: str) -> Optional[str]:
        """
        Returns the author name extracted as `<first name> <other names>`

        If there are multiple author it returns "<author 1> & <author 2> .."
        """
        open_bracket = line.rfind("(")
        if open_bracket == -1:
            return None

        close_bracket = line.rfind(")")
        names = line[open_bracket + 1 : close_bracket]

        # Empty string
        if len(names) == 0:
            return None

        # Handle case with multiple author
        # Author names are usually written as '<first name>, <last name>'
        authors = names.split(";")
        formatted_names = [
            NoteKeeper._swap_parts_of_name(name) for name in authors
        ]
        return " & ".join(formatted_names)

    @staticmethod
    def _swap_parts_of_name(name: str) -> str:
        """
        Reformats the author name from `<last names>, <first name>`
        to `<first name> <last name>`

        Note: this will not handle cases like
        ("lincoln, abraham dr,", "dr, abraham lincoln") and
        ("Agriculture, urban and food hall"),
        """
        name_parts = name.split(",")
        if len(name_parts) == 1:
            return name_parts[0].strip()

        first_name = name_parts[1].strip()
        last_names = name_parts[0].strip()
        return f"{first_name} {last_names}"

    @staticmethod
    def _extract_location(info: str) -> Tuple[int, int]:
        """
        Extracts the location info from a highlight. Page is not taken as
        location is the standardised digital position.

        Locations are recorded on the second line of a
        highlight in the following format:
        '- Your Highlight on page 43 | location 973-974 |
        Added on Thursday, 28 January 2016 08:33:31'
        """

        # TODO: What if the location is only on one page?
        pattern = re.compile(r"location (\d+)(-\d+)?", re.IGNORECASE)
        match = re.search(pattern, info)
        if match is None:
            return 0, 0

        print(match.groups())
        start, end = match.groups()  # matches are strings
        if end is None:
            return int(start), int(start)

        # Index for end is 1: because the second group captures the dash
        return int(start), int(end[1:])

    @staticmethod
    def _extract_date(info: str) -> datetime:
        """
        Extracts the date from a highlight.

        Dates are recorded on the second line of a
        highlight in the following format:
        '- Your Highlight on page 43 | location 973-974 |
        Added on Thursday, 28 January 2016 08:33:31'
        """
        pattern = re.compile(
            r"\d{2}\s\w+\s\d{4}\s\d{2}:\d{2}:\d{2}", re.IGNORECASE
        )
        match = re.search(pattern, info)
        if match is None:
            return datetime.min
        return datetime.strptime(match.group(0), "%d %B %Y %H:%M:%S")

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
