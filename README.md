# Kindle Note Clipper

Kindle note clipper is provides a simple API to help extract your clippings from the Amazon Kindle "My Clippings.txt".

### Usage

The module provides a class `NoteKeeper` which loads the clippings from
"My Clippings.txt" and extract all notes.

```
nk = NoteKeeper()
nk.update_from_list("My Clippings.txt")
```

Multiple calls to `update_from_list` will not recreate the list of extracted
clippings but update the internal storage by appending any new clippings found.

Once loaded, clippings can be searched by book

```
nk.get_clippings(book="arthur")
```

which will return all clippings from the book "arthur".

Finally, clippings can be exported to csv with `nk.export_csv(file)`. By default,
this writes all clippings in chronological order. A book title may be specified
to filter clippings.

### Requirements

- Python 3.7

For testing

```
pip3 install -r test_requirements.txt
```
