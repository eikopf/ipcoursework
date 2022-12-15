"""Book Searching Tools

This script provides functions and constants for both rudimentary field \\
querying, as in any database, and more complex natural language \\
querying wherein strings are parsed for relevant data.

This natural language processing is used, by-and-large, to ensure that \\
queries to the search section are interpreted correctly, and not just \\
simply rejected.

Also, the Levenshtein distance is a string metric used to quantify the \\
"distance" between two strings; this is then used to sort the search \\
results in the main application with the levenshtein_sort function.
"""
from pprint import pformat

import database as db
from database import Book
from datetime import date

# constants used for the language processing functions
INVALID_SEARCH_TERMS: list[str] = ["the",
                                   "book",
                                   "books",
                                   ",",
                                   ".",
                                   "a",
                                   "it",
                                   "with",
                                   "which"]
RESERVED_SEARCH_TERMS: list[str] = ["by",
                                    "in",
                                    "about",
                                    "purchased",
                                    "before",
                                    "after"]
LOW_IMPORTANCE_WORDS: list[str] = ["book",
                                   "books",
                                   "novel",
                                   "novels",
                                   "works",
                                   'called',
                                   'named',
                                   'is']


def key_search_terms(s: str) -> list[str]:
    """Parses a search string to gather key terms, \\
    and then returns them as a list."""
    out = s.lower().split(" ")
    for i in out:
        if i in INVALID_SEARCH_TERMS:
            out.remove(i)

    return out


def parse_title(s: str) -> str:
    """Parses a given search string to find a title being searched for."""
    title_terms: list[str] = s.split(" ").copy()
    for term in s.split(" "):
        if term in RESERVED_SEARCH_TERMS or term in LOW_IMPORTANCE_WORDS:
            title_terms.remove(term)

    return " ".join(title_terms)


def field_queries(s: str) -> dict:
    """Parses key search terms to find \\
    appropriate values to search for in database."""
    out: dict = {"genre": None,
                 "title": None,
                 "author": None,
                 "purchase price": None,
                 "purchase date": None,
                 "time direction": None}
    terms = key_search_terms(s)

    for i in range(len(terms)):
        if terms[i] == "in" or terms[i] == "about":
            try:
                out["genre"] = terms[i+1] \
                    if terms[i + 1] not in RESERVED_SEARCH_TERMS else None
            except IndexError:
                pass

        elif terms[i] == "by":
            try:
                first_name = terms[i + 1]
                last_name = terms[i + 2]
                out["author"] = first_name + " " + last_name
            except IndexError:
                pass

        elif terms[i] == "purchased":
            try:
                time_direction = terms[i + 1]
                if time_direction == "after":
                    out["time direction"] = "after"
                elif time_direction == "before":
                    out["time direction"] = "before"

                d = terms[i + 2]
                split_char = d[4]
                out["purchase date"] = date(*[int(i) for i
                                              in d.split(split_char)])
            except IndexError:
                pass

    out["title"] = parse_title(s) if len(parse_title(s)) != 0 else None
    return out


def search_by_field(field: str, value: str) -> list[Book]:
    """Returns a list of the books which have the \\
    specified value in the specified field."""
    if field == "id":
        return [db.get_book(int(value))]
    elif field == "genre":
        return db.get_books_by_genre(value)
    elif field == "title":
        return db.get_books_by_title(value)
    elif field == "author":
        return db.get_books_by_author(value)
    elif field == "purchase price":
        return db.get_books_by_price(int(value))
    elif field == "before purchase date":
        return db.get_books_before_date(date(value))
    elif field == "after purchase date":
        return db.get_books_after_date(date(value))
    else:
        return []


def search_by_query(query: str) -> list[Book]:
    """Returns a list of the books which match the given query, \\
    based on simple natural language processing."""
    subqueries = field_queries(query)

    # fetch sets of books matching each component of the query
    genre_books = set(db.get_books_by_genre(subqueries["genre"]))
    title_books = set(db.get_books_by_title(subqueries["title"]))
    author_books = set(db.get_books_by_author(subqueries["author"]))
    price_books = set(db.get_books_by_price(subqueries["purchase price"]))

    if subqueries["time direction"] is not None:
        if subqueries["time direction"] == "before":
            date_books = set(
                db.get_books_before_date(subqueries["purchase date"])
            )
        else:
            date_books = set(
                db.get_books_after_date(subqueries["purchase date"])
            )

    # creates a list of all the book sets with at least one element
    book_sets = list(filter(lambda x: len(x) > 0, [genre_books,
                                                   title_books,
                                                   author_books,
                                                   price_books]))

    if len(book_sets) == 1:
        return list(*book_sets)
    elif len(book_sets) == 0:
        return []
    # returns a list of all the books which are in every non-zero set
    return list(book_sets[0].intersection(book_sets[1:]))


def levenshtein_distance(a: str, b: str) -> int:
    """Computes the Levenshtein distance between two strings."""
    if len(b) == 0:
        return len(a)
    elif len(a) == 0:
        return len(b)
    elif a[0] == b[0]:
        return levenshtein_distance(a[1:], b[1:])
    else:
        return 1 + min(levenshtein_distance(a[1:], b),
                       levenshtein_distance(a, b[1:]),
                       levenshtein_distance(a[1:], b[1:]))


def levenshtein_sort(query: str, results: list[str]) -> list[str]:
    """Sorts the given strings using the Levenshtein string metric."""
    terms = {}
    for result in results:
        terms[result] = -levenshtein_distance(query, result)

    return list(reversed(sorted(terms.keys(), key=terms.get)))


if __name__ == "__main__":
    # key_search_terms
    print('key_search_terms tests')
    print(pformat(key_search_terms('books by eugenia cheng')))
    print(pformat(key_search_terms('books about maths')))
    print(pformat(key_search_terms('books by brand')))
    print('\n')

    # parse_title
    print('parse_title tests')
    print(pformat(parse_title('the way of kings')))
    print(pformat(parse_title('book called the way of kings')))
    print(pformat(parse_title('the way of kings by brandon sanderson')))
    print('\n')

    # field_queries
    print('field_queries tests')
    print(pformat(field_queries('books by eugenia cheng in maths')))
    print(pformat(field_queries('books by eugenia cheng')))
    print(pformat(field_queries('books in fantasy')))
    print('\n')

    # search_by_field
    print('search_by_field tests')
    print(pformat(search_by_field('title', 'the way of kings')))
    print(pformat(search_by_field('title', 'x + y')))
    print(pformat(search_by_field('title', 'eugenia cheng')))
    print(pformat(search_by_field('author', 'eugenia cheng')))
    print('\n')

    # search_by_query
    print('search_by_query tests')
    print(pformat(search_by_query('books by eugenia cheng')))
    print(pformat(search_by_query('books by brandon sanderson')))
    print('\n')

    # levenshtein_distance
    print('levenshtein_distance tests')
    print(levenshtein_distance('hello, world', 'hello, moon'))
    print(levenshtein_distance('hello, world', 'hello, world'))
    print(levenshtein_distance('hello, world', 'hello, world!'))
    print('\n')

    # levenshtein_sort
    print('levenshtein_sort tests')
    print(pformat(levenshtein_sort('hello', ['h', 'hell', 'hello', 'quaint'])))
    print(pformat(levenshtein_sort('quallo', ['h', 'hell', 'hello', 'quaint'])))
    print('\n')


