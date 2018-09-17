# Kindle Clippings
Kindle Clippings is a Python package that helps you extract your notes and highlights from the Amazon Kindle device. It does this by processing the 'My Clippings.txt' which is where the Kindle stores all notes and highlights made for your books.

### How to use
A simple example of how to use this package can be found in `example.py`. The 'My Clippings.txt' is processed with the `load_from_text` function. This stores all notes by book in a dictionary. Each book note can then be saved to a separate text file with the `write_to_file` function. You can view all books and authors using the other utility functions provided.

Finally, the state of the dictionary can be saved into a JSON or Pickle file and reloaded for use next time. 

### Requirements
- Python 3

### Todo
Allow saving to Evernote.  

