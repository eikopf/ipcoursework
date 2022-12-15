"""Database Interaction Tools

This script provides functions to interact with the database stored in the `book_info.txt` file,
and also provides a `Book` type to facilitate better error messages. Similarly, a Log type is
provided to deal with actions on the database, which are recorded in 'logfile.txt'

Aside from the initial header line, each line of `book_info.txt` corresponds to a particular book,
and the particular fields of each book are separated by semicolons (;). These fields are, in order, as follows:

- ID: A unique numeric identifier
- Genre: A string describing the general genre of a book
- Title: The title of the book as a string
- Author: The name of the author, in forename-surname order
- Purchase Price: The price of the book in GBP
- Purchase Date: The date on which the book was purchased, in the datetime.date format

In much the same way, each line of 'logfile.txt' corresponds to an action on the database,
and each 'word' in the action is separated with a space. Each action is made of four words, and
in order these are:

- Action: A string corresponding to the kind of action taken
- Book ID: An integer corresponding to a particular book
- Member ID: A string corresponding to a four digit member ID
- Date: The date on which the action was taken
"""

from datetime import date
from pprint import pformat
from typing import Union, Optional, Literal
from re import fullmatch
import logging

Book = tuple[
    int,  # ID
    str,  # Genre
    str,  # Title
    str,  # Author
    int,  # Purchase Price
    date  # Purchase Date
]

Log = tuple[
    str,  # action
    int,  # book ID
    str,  # member ID
    date  # date
]


def initialize():
    """Clears the `book_info.txt` and `logfile.txt` files so that they can be written to."""
    with open("data_files/book_info.txt", 'w') as db:
        db.write("ID; Genre; Title; Author; Purchase Price; Purchase Date")

    with open("data_files/logfile.txt", 'w') as log:
        log.write("ACTION BOOK_ID MEMBER_ID")

    logging.debug("initialized data files")


def book_to_string(book: Book) -> str:
    """Converts a `book` tuple into a string \\
    that can be written to the `book_info.txt` file."""
    s = [str(a) for a in book]
    return ';'.join(s)


def book_entry_is_valid(entry: str) -> bool:
    """Validates that a particular entry in the database is valid."""
    return bool(fullmatch(r'\d+;.+;.+;\d+;\d+-\d+-\d+', entry))


def write_book(book: Book) -> None:
    """Writes a book to the `book_info.txt` \\
    file as a new line at the end of the file."""
    with open("data_files/book_info.txt", 'r') as db:
        lines = db.readlines()
        ids = set([int(line.split(';')[0]) for line in lines])

    with open("data_files/book_info.txt", 'a') as db:
        if book[0] in ids:
            raise IOError({'book': book, 'lines': lines, 'ids': ids})
        db.write("\n")
        db.write(book_to_string(book))


def write_log(s: str) -> None:
    """Writes a log to the logfile and assumes that it is valid."""
    with open("data_files/logfile.txt", 'a') as log:
        log.write(s)


def get_logs() -> list[Log]:
    """Returns a list of the logs in the logfile in
    sequential order."""
    with open("data_files/logfile.txt", 'r') as log:
        logs = log.readlines()[1:]

    return [(log.split(" ")[0],
             int(log.split(" ")[1]),
             log.split(" ")[2],
             date(
                 *[int(i) for i in log.split(" ")[3].split('-')])
             ) for log in logs]


def get_open_logs() -> list[Log]:
    """Returns a list of logs which have not been closed \\
    by a subsequent log. OUT logs are closed by a RETURN log, and \\
    RESERVE logs are closed by a DERESERVE log or OUT log."""
    out: list[Log] = []
    for log in get_logs():
        if log[0] == "RESERVE":
            out.append(log)
        elif log[0] == "OUT":
            out.append(log)
            try:
                out.remove(("RESERVE", log[1], log[2], log[3]))
            except ValueError:
                pass
        elif log[0] == "RETURN":
            try:
                out.remove(("RESERVE", log[1], log[2], log[3]))
            except ValueError:
                pass
        else:  # handles DERESERVE
            try:
                out.remove(("RESERVE", log[1], log[2], log[3]))
            except ValueError:
                pass
    return out


def book_id_is_valid(book_id: int) -> bool:
    """Determines whether a book exists in \\
    `book_info.txt` and returns a bool accordingly."""
    if get_book(book_id) is None:
        return False
    else:
        return True


def get_book_status(book_id: int) -> Literal['RESERVED', 'OUT', 'AVAILABLE']:
    """Returns the status of the given book according to the logfile."""
    if not book_id_is_valid(book_id):
        raise IOError

    status = filter_logs_with_id(get_logs(), book_id)

    if len(status) == 0:
        return 'AVAILABLE'

    status = status[-1][0]

    if status == 'OUT':
        return 'OUT'
    elif status == 'RESERVE':
        return 'RESERVED'
    elif status == 'RETURN':
        return 'AVAILABLE'
    else:
        return 'AVAILABLE'
    pass


def filter_logs_with_id(logs: list[Log], book_id: int) -> list[Log]:
    """Iterates over a list of logs and returns only the logs
    with the given ID."""
    return list(filter(lambda x: x[1] == book_id, logs))


def write_books(books: list[Book]):
    """Writes all the books in the provided list to `book_info.txt`"""
    for b in books:
        write_book(b)


def get_book(book_id: int) -> Optional[Book]:
    """Retrieves a book from the `book_info.txt` file and \\
    returns it as a tuple with the correct data types. \\
    If the provided `book_id` does not exist, then this \\
    function returns `None`.
    """
    with open("data_files/book_info.txt", "r") as db:
        entries = db.readlines()[1:]

    out: Book | None = None
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


def get_books_by_genre(genre: str) -> list[Book]:
    """Retrieves all books which are in the provided genre."""
    if genre is None:
        return []

    with open("data_files/book_info.txt", 'r') as db:
        entries = db.readlines()[1:]

    books = []
    for entry in entries:
        data = entry.split(';')
        if genre in data[1]:
            books.append(get_book(int(data[0])))

    return books


def get_books_by_author(author: str) -> list[Book]:
    """Retrieves all books which are by the provided author."""
    if author is None:
        return []

    with open("data_files/book_info.txt", 'r') as db:
        entries = db.readlines()[1:]

    books = []
    for entry in entries:
        data = entry.split(';')
        if author in data[3]:
            books.append(get_book(int(data[0])))

    return books


def get_books_by_title(title: str) -> list[Book]:
    """Retrieves all books with the provided title."""
    if title is None:
        return []

    with open("data_files/book_info.txt", 'r') as db:
        entries = db.readlines()[1:]

    books = []
    for entry in entries:
        data = entry.split(';')
        if title in data[2]:
            books.append(get_book(int(data[0])))

    return books


def get_books_by_price(price: int) -> list[Book]:
    """Retrieves all books with the given purchase price."""
    if price is None:
        return []

    with open("data_files/book_info.txt", 'r') as db:
        entries = db.readlines()[1:]

    books = []
    for entry in entries:
        data = entry.split(';')
        if int(data[4]) <= price:
            books.append(get_book(int(data[0])))

    return books


def get_books_before_date(d: date) -> list[Book]:
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


def get_books_after_date(d: date) -> list[Book]:
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
    # initialize() is not tested here; it has side effects

    # book_to_string
    print('book_to_string tests')
    print(book_to_string(get_book(1)))
    print(book_to_string(get_book(7)))
    print(book_to_string(get_book(17)))
    print(book_to_string(get_book(27)))
    print('\n')

    # book_entry_is_valid
    print('book_entry_is_valid tests')
    print(book_entry_is_valid(book_to_string(get_book(1))))
    print(book_entry_is_valid(book_to_string(get_book(9))))
    print(book_entry_is_valid(book_to_string(get_book(90))))
    print(book_entry_is_valid('hello' + book_to_string(get_book(1))))
    print('\n')

    # write_book() is not tested here; it has side effects
    # write_log() is also not tested for the same reason

    # get_logs
    print('get_logs test')
    print(pformat(get_logs()))
    print('\n')

    # get_open_logs
    print('get_open_logs test')
    print(pformat(get_open_logs()))
    print('\n')

    # book_id_is_valid
    print('book_id_is_valid tests')
    print(book_id_is_valid(1))
    print(book_id_is_valid(7))
    print(book_id_is_valid('eqeq'))
    print(book_id_is_valid(-1))
    print(book_id_is_valid(4.7))
    print('\n')

    # get_book_status
    print('get_book_status tests')
    print(get_book_status(1))
    print(get_book_status(92))
    print(get_book_status(54))
    print(get_book_status(32))
    print('\n')

    # filter_logs_with_id
    print('filter_logs_with_id tests')
    print(pformat(filter_logs_with_id(get_logs(), 13)))
    print(pformat(filter_logs_with_id(get_logs(), 2)))
    print('\n')

    # write_books() is not tested here; it has side effects

    # get_book
    print('get_book tests')
    print(get_book(1))
    print(get_book(2))
    print(get_book(16))
    print(get_book(31))
    print(get_book(27))
    print('\n')

    # get_books_by_genre
    print('get_books_by_genre tests')
    print(pformat(get_books_by_genre('fantasy')))
    print(pformat(get_books_by_genre('maths')))
    print('\n')

    # get_books_by_author
    print('get_books_by_author tests')
    print(pformat(get_books_by_author('becky chambers')))
    print('\n')

    # get_books_by_title
    print('get_books_by_title tests')
    print(pformat(get_books_by_title('the way of kings')))
    print(pformat(get_books_by_title('immune')))
    print(pformat(get_books_by_title('linear algebra')))
    print('\n')

    # get_books_by_price
    print('get_books_by_price tests')
    print(pformat(get_books_by_price(23)))
    print(pformat(get_books_by_price(14)))
    print('\n')

    # get_books_before_date
    print('get_books_before_date test')
    print(pformat(get_books_before_date(date(2015, 10, 12))))
    print('\n')

    # get_books_after_date
    print('get_books_after_date test')
    print(pformat(get_books_after_date(date(2022, 10, 12))))
    print('\n')
