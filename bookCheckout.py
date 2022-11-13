"""Checkout and Reservation Tools

This script provides functions to deal with checking out and reserving
books by members with valid IDs.

This script also handles much of the detail of writing to the logfile, where
each line (aside from the header) takes the form of ACTION BOOK_ID MEMBER_ID.

- ACTION: can be OUT, RETURN, RESERVE, or DERESERVE
- BOOK_ID: an integer corresponding to the ID of a particular book
- MEMBER_ID: a 4-digit string denoting a particular member
"""

import logging
from database import get_book, get_logs, write_log, \
    Log, filter_logs_with_id, get_open_logs
from re import fullmatch


def member_id_is_valid(member_id: str) -> bool:
    """Determines whether the given member id is valid using a regular expression."""
    if fullmatch(r'\d\d\d\d', member_id):
        return True
    else:
        return False


def book_id_is_valid(book_id: int) -> bool:
    """Determines whether a book exists in `book_info.txt` and returns a bool accordingly."""
    if get_book(book_id) is None:
        return False
    else:
        return True


def get_loaned_book_ids(logs: list[Log]) -> set[int]:
    """Returns the set of book IDs for all the books that are currently loaned out."""
    out = set()
    for log in logs:
        if log[0] == 'OUT':
            out.add(log[1])
        elif log[0] == 'RETURN':
            out.remove(log[1])
    return out


def get_reserved_book_ids(logs: list[Log]) -> set[int]:
    """Returns the set of book IDs for all the books that are currently reserved."""
    out = set()
    for log in logs:
        if log[0] == 'RESERVE':
            out.add(log[1])
        elif log[0] == 'UNRESERVE':
            out.remove(log[1])
    return out


def check_out(book_id: int, member_id: str):  # TODO: reconfigure this function to deal with reservations correctly
    """Checks a book out and writes the relevant data to the logfile; will
    raise `IOError` if this fails."""
    logging.debug(f'checkout called with book_id: {book_id}, '
                  f'member_id: {member_id}')

    checkout_allowed = member_id_is_valid(member_id) and \
                       book_id_is_valid(book_id) and \
                       book_id not in get_loaned_book_ids(get_logs()) and \
                       book_id not in get_reserved_book_ids(get_logs())

    if checkout_allowed:
        write_log(f"OUT {str(book_id)} {member_id}")
    else:
        raise IOError({"book_id": book_id,
                       "member_id": member_id,
                       "checkout_allowed": checkout_allowed})


def reserve(book_id: int, member_id: str):
    """Reserves a book for the given member and writes the
    relevant data to the logfile; raises `IOError` if
    this fails."""
    logging.debug(f'reserve called with book_id: {book_id}, '
                  f'member_id: {member_id}')

    reservation_allowed = member_id_is_valid(member_id) and \
                          book_id_is_valid(book_id) and \
                          book_id in get_loaned_book_ids(get_logs()) and \
                          book_id not in get_reserved_book_ids(get_logs())

    if reservation_allowed:
        write_log(f"RESERVE {str(book_id)} {member_id}")
    else:
        raise IOError({"book_id": book_id,
                       "member_id": member_id,
                       "reservation_allowed": reservation_allowed})


def dereserve(book_id: int):
    """Dereserves a book based on its ID, and writes the relevant
    data to the logfile; raises `IOError` if this fails."""
    logging.debug(f'dereserve called with book_id: {book_id}')
    open_logs_for_id = filter_logs_with_id(get_open_logs(), book_id)

    for log in open_logs_for_id:
        if log[0] == "RESERVE":
            write_log(f"DERESERVE {book_id} {log[2]}")
            return

    raise IOError({"open_logs_for_id": open_logs_for_id,
                   "book_id": book_id})


if __name__ == '__main__':
    logging.basicConfig(filename="DO_NOT_SUBMIT/general.log", encoding="utf-8", level=0)

    print("tests for member_id_is_valid:")
    print(f"0000: {member_id_is_valid('0000')}")
    print(f'9999: {member_id_is_valid("9999")}')
    print(f'70001: {member_id_is_valid("70001")}')
    print(f'1234: {member_id_is_valid("1234")}')
    print(f'372: {member_id_is_valid("372")}', "\n")

    print("tests for book_id_is_valid:")
    print(f"-1: {book_id_is_valid(-1)}")
    print(f"45: {book_id_is_valid(45)}")
    print(f"1: {book_id_is_valid(1)}")
    print(f"4: {book_id_is_valid(4)}", "\n")

    print(f"set of loaned book IDs: {get_loaned_book_ids(get_logs())}")
    print(f"set of reserved book IDs: {get_reserved_book_ids(get_logs())}")

    try:
        check_out(17, "1976")
        print(f'checkout book_id: 17, member_id: "1976", : success')
    except IOError as e:
        print(f'checkout book_id: 17, member_id: "1976", : failure -> {e}')
