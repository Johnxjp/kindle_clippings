import re

regex = re.compile('(?<=\().*?(?=\))') #Defines regular expression pattern for getting author's name
regex2 = re.compile('\(.*\)?') #Defines regular expression pattern for removing publisher and author's name from book string
clippingsDict = {}

def check_book(book):
    """
    This function checks to see if the book found in the clipping is already in the dictionary or not
    :param book: the title of the book
    :return: Bool, if the book already exists in the dictionary or not
    """
    try:
        clippingsDict[book]
        return True
    except KeyError:
        return False

def add_books(unstrippedBook):
    """
    This function adds the book to the dictionary if it is not already in it
    :param unstrippedBook: book name inc. publisher and author
    :return: String, name of the book after it has been stripped and publisher + author's name has been removed
    """
    book = regex2.sub("",unstrippedBook).strip()
    if not check_book(book):
        if regex.findall(unstrippedBook) != []:
            clippingsDict[book] = {"Author": regex.findall(unstrippedBook)[-1], "Clippings": []}
        else:
            clippingsDict[book] = {"Author": "Unknown", "Clippings": []}
    return book

def addClippings(clippings):
    """
    This function adds the clippings and the associated date to each book.
    :return: None
    """

    for index, i in enumerate(clippings):
        if index % 5 == 0:
            book = add_books(i)
        elif index % 5 == 1:
            datePage = i
        elif index % 5 == 3:
            description = i
        elif index % 5 == 4:
            clippingsDict[book]["Clippings"].append({"Date/Page" : datePage, "clipping": description})
        else:
            continue


def writeClippingsToFileWithoutDates(book):
    """
    This function writes all the clippings in the book specified to a text file with the title <book_name + _clippings>
    :param book: name of the book to search in the dictionary
    :return: None
    """
    if check_book(book):
        file = open(book + "_clippings.txt", 'w')
        for i in clippingsDict[book]["Clippings"]:
            file.write(i["clipping"] +'\n\n')
        file.close()
    else:
        return "That book doesn't exist. Check spelling!"

def stripClippings(clippings):
    """
    Strips the clippings of new lines and white spaces
    :param clippings: kindle clippings
    :return:
    """

    for index, i in enumerate(clippings):
        clippings[index] = i.strip()

def bookList():
    """
    returns the list of books on the kindle
    :return: book list
    """

    if clippingsDict == {}:
        return "Please call the addClippings function first"
    else:
        return clippingsDict.keys()

if __name__ == "__main__":
    """
    The next piece of code opens a file and reads every single line one by one and stores each
    line as an element in a list
    """

    f = open("AmazonClippings.txt", 'r', encoding="utf-8") #Need to change "AmazonClipping.txt" to your amazon kindle
    # highlights text file, which should be in the same folder
    clippings = f.readlines()
    f.close()

    stripClippings(clippings)
    addClippings(clippings)
    my_bookList = bookList()

    writeClippingsToFileWithoutDates("Letters to a CEO") #change the book title in here