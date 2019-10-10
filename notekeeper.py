from collections import defaultdict
from datetime import datetime
import re
from typing import Mapping, Sequence, Tuple, Optional

from clips import Clip, ClipList

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
        self._bookclip_map: Mapping[str, Sequence[Hash]] = defaultdict(set)

    def update_from_file(self, clippings_filepath: str) -> None:
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
            highlights = [line.strip().lower() for line in f]
            if highlights[0] == "==========":
                # Skip first line if line break as the code was built
                # on file versions without this.
                highlights = highlights[1:]
        self.update_from_list(highlights)

    def update_from_list(self, raw_clips: Sequence[str]) -> None:
        """
        Loads the clips from a list of the raw clippings taken from the
        kindle file
        """
        n_lines_per_highlight = 5
        for line_number in range(0, len(raw_clips), n_lines_per_highlight):
            highlight_block = raw_clips[
                line_number : line_number + n_lines_per_highlight
            ]
            clip = self._extract_clip(highlight_block)
            # Warning: hash value is truncated to bit value of machine
            # This may result in different behaviour on different machines
            clip_hash = hash(clip)
            self._clippings[clip_hash] = clip
            self.update_book_search(clip.book, clip_hash)

    def update_book_search(self, book: str, clip_hash: Hash) -> None:
        """
        Updates the hash map containing clips belonging to books
        """
        self._bookclip_map[book].add(clip_hash)

    @staticmethod
    def _extract_clip(highlight_block: Sequence[str]) -> Clip:
        """
        Takes a highlight block and returns a Clip object. An example of a
        highlight block is
        """
        book_author_line = highlight_block[0]
        location_date_line = highlight_block[1]
        text = highlight_block[3]

        book = NoteKeeper._extract_book_title(book_author_line)
        author = NoteKeeper._extract_author(book_author_line)
        start_location, end_location = NoteKeeper._extract_location(
            location_date_line
        )
        date = NoteKeeper._extract_date(location_date_line)

        return Clip(book, author, start_location, end_location, date, text)

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
        pattern = re.compile(r"location (\d+)(-\d+)?", re.IGNORECASE)
        match = re.search(pattern, info)
        if match is None:
            return 0, 0

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

    def _get_book_clippings(self, book: str) -> ClipList:
        """
        Returns all the clippings for a book.
        """
        clip_hashes = {}
        try:
            clip_hashes = self._bookclip_map[book]
        except KeyError:
            print(f"{book!r} does not exist.")

        clips = [self._clippings[h] for h in clip_hashes]
        return ClipList(clips)

    def get_clippings(self, book: Optional[str] = None) -> ClipList:
        """
        Return a list of clippings. If A book is provided get the list by
        book.
        """
        if book is None:
            return ClipList(self._clippings.values())
        return self._get_book_clippings(book)

    def export_csv(
        self, file: str, book: Optional[str] = None, sep="\t"
    ) -> None:
        """
        Saves all clippings to a csv. By default these are sorted
        chronologically.

        If book is specified then all clippings for a book are taken

        Separator is tab by default.
        """
        clippings = self.get_clippings(book)
        clippings.sortby(attribute="date")
        with open(file, "w") as f:
            f.write(sep.join(Clip._fields) + "\n")  # Header
            for clip in clippings:
                f.write(sep.join(map(repr, clip)) + "\n")
