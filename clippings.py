import os
import datetime
import json

class Clippings:

    def __init__(self, clippings_file=None):
        """
        Constructor for the Clippings object.

        Highlights from the Amazon Kindle are stored in a dictionary. The format is as follows:
        {"date_of_last_highlight": datetime_object, "author": {"book_1": [clippings], "book_2":[clippings]}, ...}

        :param clippings_file: The raw text file obtained from the Amazon Kindle device.
        :return: None
        """

        if clippings_file == "":
            raise Exception("This file is empty")

        self.highlights_dictionary = {"date_of_last_highlight": datetime.datetime.strptime("1900 1 1", "%Y %M %d")}
        self.highlights = clippings_file
        self.booklist = []
        self.authorlist = []
        self.last_modified_date = 0

        # This processes the text file
        self._add_highlights(clippings_file, self.highlights_dictionary["date_of_last_highlight"])

    def load_clippings(self, dictionary_filepath_to_load=""):
        if not dictionary_filepath_to_load.lower().endswith(".txt"):
            raise Exception("Please make sure your file is a .txt file")
        elif os.stat(dictionary_filepath_to_load).st_size == 0:
            raise Exception("This file is empty")
        else:
            with open(dictionary_filepath_to_load, 'r') as infile:
                self.highlights_dictionary = json.load(infile)
                self.highlights_dictionary["date_of_last_highlight"] = \
                    datetime.datetime.strptime(self.highlights_dictionary["date_of_last_highlight"],
                                               "%Y-%m-%d %H:%M:%S")

        self._add_highlights(highlights, self.highlights_dictionary["date_of_last_highlight"])
        self.booklist = self._get_book_list()
        self.authorlist = self._get_author_list()
        self.last_modified_date = self._get_last_modified_date()


    def get_book_list_by_author(self, author_name):
        """
        :param author_name: the name of the author
        :return: the books belonging to that author
        """
        return self.highlights_dictionary[author_name]

    def get_highlights_by_book(self, book_name):
        """
        :param book_name: the name of the book
        :return: all the highlights in that book
        """
        for author in self.authorlist:
            if book_name in self.highlights_dictionary[author]:
                return self.highlights_dictionary[author][book_name]

        return "This book was not found. Please check the spelling."

    def save_dict(self, dictionary_file_to_save_full_path):
        """
        :param dictionary_file_to_save_full_path: file path to save dictionary
        :return: None
        """
        if not dictionary_file_to_save_full_path.lower().endswith(".txt"):
            raise Exception("Please make sure your file is a .txt file")

        if os.path.isfile(dictionary_file_to_save_full_path):
            if os.stat(dictionary_file_to_save_full_path).st_size == 0:
                raise Exception("This file is empty")

        with open(dictionary_file_to_save_full_path, 'w') as outfile:
            self.highlights_dictionary["date_of_last_highlight"] = str(self.highlights_dictionary["date_of_last_highlight"])
            json.dump(self.highlights_dictionary, outfile)

    def _get_last_modified_date(self):
        """
        :return: the last time the dictionary was modified
        """
        return self.highlights_dictionary["date_of_last_highlight"]

    def _get_author_list(self):
        """
        :return: the list of authors in the dictionary
        """
        author_list = list(self.highlights_dictionary.keys())
        author_list.remove("date_of_last_highlight")
        return author_list

    def _get_book_list(self):
        """
        :return: all the books from all the authors in the dictionary
        """
        all_books = []
        author_list = self._get_author_list()
        for author in author_list:
            all_books.extend((list(self.highlights_dictionary[author].keys())))

        return all_books

    def _extract_author_name(self, book_and_author_string):
        """
        :param book_and_author_string: string that contains the book and the author's name
        :return: the author's name
        """
        open_bracket = book_and_author_string.rfind("(")
        close_bracket = book_and_author_string.rfind(")")

        if open_bracket == -1:
            return "unknown"

        author_full_name = book_and_author_string[open_bracket+1:close_bracket].split(',')
        if len(author_full_name) == 1:
            return author_full_name[0]
        else:
            first_name = author_full_name[1].strip()
            last_name = author_full_name[0].strip()
            return " ".join([first_name, last_name])

    def _extract_date(self, date_line):
        """
        :param date_line: the string that contains the date of the highlight in the kindle file
        :return: date the highlight was made
        """
        index_pos = len("day, ") + date_line.find('day, ')
        return datetime.datetime.strptime(date_line[index_pos:], "%d %B %Y %H:%M:%S")

    def _extract_book_title(self, book_and_author_string):
        """
        :param book_and_author_string: string that contains the book and the author's name
        :return: title of the book
        """
        open_bracket = book_and_author_string.rfind("(")

        if open_bracket == -1:
            return book_and_author_string.strip()
        else:
            return book_and_author_string[:open_bracket]

    def _test_author_empty(self, author_name):
        try:
            self.highlights_dictionary[author_name]
        except KeyError:
            self.highlights_dictionary[author_name] = {}

    def _test_book_empty(self, book_name, author_name):
        try:
            self.highlights_dictionary[author_name][book_name]
        except KeyError:
            self.highlights_dictionary[author_name][book_name] = []

    def _add_highlights(self, highlights, start_date):
        """
        This function adds the clippings and the associated date to each book.
        It also updates the KindleDictionary object's attributes
        :param highlights: The highlights from the kindle file
        :param start_date: The date from which to start updating the highlights
        :return: None
        """
        reset_line = "=========="
        line_number = 1
        book_and_author = ""
        clip = []
        date = start_date
        start_index = 0

        date_element_indexes = [index-1 for index, line in enumerate(highlights) if line == ""]
        for index in date_element_indexes:
            if self._extract_date(highlights[index]) > date:
                start_index = index
                break

        highlights = highlights[start_index-1:]
        for line in highlights:
            if line == reset_line:
                line_number = 0

                if not clip == []:
                    book = self._extract_book_title(book_and_author).strip()
                    author = self._extract_author_name(book_and_author).strip()
                    self._test_author_empty(author)
                    self._test_book_empty(book, author)
                    self.highlights_dictionary[author][book].append(" ".join(clip))
                    clip = []

                    if self.highlights_dictionary["date_of_last_highlight"] < date:
                        self.highlights_dictionary["date_of_last_highlight"] = date

            if line_number == 1:
                book_and_author = line
            elif line_number == 2:
                date = self._extract_date(line)
            elif line_number >= 4:
                clip.append(line)
            else:
                pass

            line_number += 1

        self.booklist = self._get_book_list()
        self.authorlist = self._get_author_list()
        self.last_modified_date = self._get_last_modified_date()

    def __str__(self):
        return str(self.highlights_dictionary)

    def write_clippings_to_file(self, book_name, file_path=""):
        """
        This function writes all the clippings in the book specified to a text file with the title
        <book_name + _clippings>
        :param book_name: name of the book to search in the dictionary
        :param file_path: the location where the file will be saved excluding file name
        :return: None
        """

        if file_path == "":
            directory = os.getcwd()
            file_name = book_name + "_clippings.txt"
        elif os.path.isdir(file_path):
            directory = file_path
            file_name = file_path + book_name + "_clippings.txt"
        else:
            raise Exception("{} is not a valid file path".format(file_path))

        for author in self.authorlist:
            if book_name in self.highlights_dictionary[author]:
                file = open(file_name, 'w')
                for clip in self.highlights_dictionary[author][book_name]:
                    file.write(clip + '\n\n')
                file.close()
                return "Highlights saved to '{0}' with the file name '{1}'".format(directory, file_name)
        else:
            return "This book was not found. Please check the spelling."


def extract_highlights(file_name):
    """
    This function extracts all the highlights you have made from the text file where the Amazon Kindle book highlights
     are kept
    :param file_name: text file with highlight
    :return: highlights
    """
    if not file_name.lower().endswith(".txt"):
        raise Exception("Please make sure your file is a .txt file")
    elif os.stat(file_name).st_size == 0:
        raise Exception("This file is empty")
    else:
        file_contents = open(file_name, 'r', encoding="utf-8")
        highlights = file_contents.readlines()
        file_contents.close()
        highlights = list(map(str.strip, highlights))
        return highlights
