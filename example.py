from clippings import Clippings

if __name__ == "__main__":
    obj = Clippings()
    obj.load_from_text("test.txt")

    print(obj.get_booklist())

    obj.write_to_file(book="book1", file="saved_text.txt")
