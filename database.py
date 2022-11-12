"""Database Interaction Tools

This script provides functions to interact with the database stored in the `book_info.txt` file,
and also provides a `book` type to facilitate better error messages.

Aside from the initial header line, each line of `book_info.txt` corresponds to a particular book,
and the particular fields of each book are separated by semicolons (;). These fields are, in order, as follows:

- ID: A unique numeric identifier
- Genre: A string describing the general genre of a book
- Title: The title of the book as a string
- Author: The name of the author, in forename-surname order
- Purchase Price: The price of the book in GBP
- Purchase Date: The date on which the book was purchased, in the datetime.date format
"""

from datetime import date
from typing import Union, Optional

# book type: ID, Genre, Title, Author, Purchase Price, Purchase Date
book = tuple[int, str, str, str, int, date]


def initialize():
    """Clears the `book_info.txt` file and prepares it so that data can be written to it."""
    with open("data_files/book_info.txt", 'w') as db:
        db.write("ID; Genre; Title; Author; Purchase Price; Purchase Date")


def book_to_string(b: book) -> str:
    """Converts a `book` tuple into a string that can be written to the `book_info.txt` file."""
    s = [str(a) for a in b]
    return ';'.join(s)


#  TODO: handle duplicate IDs
def write_book(b: book):
    """Writes a book to the `book_info.txt` file as a new line at the end of the file."""
    with open("data_files/book_info.txt", 'a') as db:
        db.write("\n")
        db.write(book_to_string(b))


def write_books(books: list[book]):
    """Writes all the books in the provided list to `book_info.txt`"""
    for b in books:
        write_book(b)


def get_book(book_id: int) -> Optional[book]:
    """Retrieves a book from the `book_info.txt` file and returns it as a tuple with the correct data types.
    If the provided `book_id` does not exist, then this function returns `None`.
    """
    with open("data_files/book_info.txt", "r") as db:
        entries = db.readlines()[1:]

    out: Union[list[str], None] = None
    for entry in entries:
        if int(entry.split(";")[0]) == book_id:
            out = entry.split(";")

    if out is None:
        return None
    else:
        out[0] = int(out[0])
        out[4] = int(out[4])
        out[5] = date(*[int(d) for d in out[5].split("-")])
        return tuple(out)


def get_books_by_genre(genre: str) -> list[book]:
    """Retrieves all books which are in the provided genre."""
    if genre is None:
        return []

    with open("data_files/book_info.txt", 'r') as db:
        entries = db.readlines()[1:]

    books = []
    for entry in entries:
        data = entry.split(';')
        if data[1] == genre:
            books.append(get_book(int(data[0])))

    return books


def get_books_by_author(author: str) -> list[book]:
    """Retrieves all books which are by the provided author."""
    if author is None:
        return []

    with open("data_files/book_info.txt", 'r') as db:
        entries = db.readlines()[1:]

    books = []
    for entry in entries:
        data = entry.split(';')
        if data[3] == author:
            books.append(get_book(int(data[0])))

    return books


def get_books_by_title(title: str) -> list[book]:
    """Retrieves all books with the provided title."""
    if title is None:
        return []

    with open("data_files/book_info.txt", 'r') as db:
        entries = db.readlines()[1:]

    books = []
    for entry in entries:
        data = entry.split(';')
        if data[2] == title:
            books.append(get_book(int(data[0])))

    return books


def get_books_by_price(price: int) -> list[book]:
    """Retrieves all books with the given purchase price."""
    if price is None:
        return []

    with open("data_files/book_info.txt", 'r') as db:
        entries = db.readlines()[1:]

    books = []
    for entry in entries:
        data = entry.split(';')
        if data[4] == price:
            books.append(get_book(int(data[0])))

    return books


def get_books_before_date(d: date) -> list[book]:
    """Retrieves all books purchased before the provided date."""
    if d is None:
        return []

    with open("data_files/book_info.txt", 'r') as db:
        entries = db.readlines()[1:]

    books = []
    for entry in entries:
        data = entry.split(';')
        if date(*[int(i) for i in data[-1].split('-')]) < d:
            books.append(get_book(int(data[0])))

    return books


def get_books_after_date(d: date) -> list[book]:
    """Retrieves all books purchased after the provided date."""
    if d is None:
        return []

    with open("data_files/book_info.txt", 'r') as db:
        entries = db.readlines()[1:]

    books = []
    for entry in entries:
        data = entry.split(';')
        if date(*[int(i) for i in data[-1].split('-')]) > d:
            books.append(get_book(int(data[0])))

    return books


if __name__ == "__main__":
    pass  # TODO: write test (read: example) cases for every function in this file