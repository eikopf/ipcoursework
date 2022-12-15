"""Checkout and Reservation Tools

This script provides functions to deal with checking out and reserving \\
books by members with valid IDs. A number of functions are provided to \\
filter through data to yield particular information, rather than \\
having to reimplement the algorithm for something each time.

This script also handles much of the detail of writing to the logfile, where \\
each line (aside from the header) takes the form of ACTION BOOK_ID MEMBER_ID.

- ACTION: can be OUT, RETURN, RESERVE, or DERESERVE
- BOOK_ID: an integer corresponding to the ID of a particular book
- MEMBER_ID: a 4-digit string denoting a particular member
- DATE: a datetime.date object corresponding to when the action occurred
"""

import logging
from pprint import pformat

from database import get_book, get_logs, write_log, \
    Log, filter_logs_with_id, get_open_logs, book_id_is_valid, \
    get_book_status
from re import fullmatch
from datetime import date


def member_id_is_valid(member_id: str) -> bool:
    """Determines whether the given member ID is \\
    valid using a regular expression."""
    if fullmatch(r'\d\d\d\d', member_id):
        return True
    else:
        return False


def get_loaned_book_ids(logs: list[Log]) -> set[int]:
    """Returns the set of book IDs for all the \\
    books that are currently loaned out."""
    out = set()
    for log in logs:
        if log[0] == 'OUT':
            out.add(log[1])
        elif log[0] == 'RETURN':
            out.remove(log[1])
    return out


def get_reserved_book_ids(logs: list[Log]) -> set[int]:
    """Returns the set of book IDs for all the \\
    books that are currently reserved."""
    out = set()
    for log in logs:
        if log[0] == 'RESERVE':
            out.add(log[1])
        elif log[0] == 'UNRESERVE':
            out.remove(log[1])
    return out


def checkout_book(book_id: int, member_id: str):
    """Checks a book out and writes the relevant data to the logfile; will \\
    raise `IOError` if this fails."""
    logging.debug(f'checkout called with book_id: {book_id}, '
                  f'member_id: {member_id}')

    checkout_allowed = (member_id_is_valid(member_id) and
                        book_id_is_valid(book_id) and
                        book_id not in get_loaned_book_ids(get_logs())) and \
                       (book_id not in get_reserved_book_ids(get_logs()) or
                        filter_logs_with_id(get_logs(),
                                            book_id)[-1][2] == member_id
                        )

    if checkout_allowed:
        write_log(f"\nOUT {str(book_id)} {member_id} {date.today()}")
    else:
        raise IOError({"book_id": book_id,
                       "member_id": member_id,
                       "checkout_allowed": checkout_allowed})


def checkout_books(book_ids: list[int], member_id: str):
    """Checks a list of books out with repeated calls to `checkout_book`."""
    for id in book_ids:
        checkout_book(id, member_id)


def reserve_book(book_id: int, member_id: str):
    """Reserves a book for the given member and writes the
    relevant data to the logfile; raises `IOError` if
    this fails."""
    logging.debug(f'reserve called with book_id: {book_id}, '
                  f'member_id: {member_id}')

    reservation_allowed = member_id_is_valid(member_id) and \
                          book_id_is_valid(book_id) and \
                          book_id not in get_loaned_book_ids(get_logs()) and \
                          book_id not in get_reserved_book_ids(get_logs())

    if reservation_allowed:
        write_log(f"\nRESERVE {str(book_id)} {member_id} {date.today()}")
    else:
        raise IOError({"book_id": book_id,
                       "member_id": member_id,
                       "reservation_allowed": reservation_allowed})


def reserve_books(book_ids: list[int], member_id: str):
    """Reserves a list of book with repeated calls to `reserve_book`."""
    for id in book_ids:
        reserve_book(id, member_id)
    pass


def dereserve(book_id: int):
    """Dereserves a book based on its ID, and writes the relevant
    data to the logfile; raises `IOError` if this fails."""
    logging.debug(f'dereserve called with book_id: {book_id}')
    open_logs_for_id = filter_logs_with_id(get_open_logs(), book_id)

    for log in open_logs_for_id:
        if log[0] == "RESERVE":
            write_log(f"\nDERESERVE {book_id} {log[2]} {date.today()}")
            return

    raise IOError({"open_logs_for_id": open_logs_for_id,
                   "book_id": book_id})


if __name__ == '__main__':
    # member_id_is_valid
    print('member_id_is_valid tests')
    print(member_id_is_valid('1111'))
    print(member_id_is_valid('adc'))
    print(member_id_is_valid('9829999'))
    print(member_id_is_valid('dhjkdha'))
    print(member_id_is_valid('1919'))
    print('\n')

    # get_loaned_book_ids
    print('get_loaned_book_ids tests')
    print(pformat(get_loaned_book_ids(get_logs())))
    print('\n')

    # get_reserved_book_ids
    print('get_reserved_book_ids tests')
    print(pformat(get_reserved_book_ids(get_logs())))
    print('\n')

    # checkout_book and checkout_books will not be tested here.
    # they have side effects that make them difficult to test well
    # the same goes for reserve_book, reserve_books, and dereserve
