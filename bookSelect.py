"""Book Recommendation and Data Manipulation Tools

This script provides functions to get data about the \\
application, to manipulate that data, and to produce \\
the required graphics for the application.

In particular, the get_order_menu_multiplot is an \\
important function to generate the matplotlib graphics \\
in the Order menu. The functions get_logfile_multiplot \\
and get_database_multiplot are just wrappers of this \\
function, and are the actual functions being called in \\
menu.py.

The algorithm for generating a purchasing recommendation \\
is relatively simple. I simply take the current popular \\
books from the logfile, and then compute what proportion \\
of them is taken up by any given author or genre. Then, \\
with a budget and average price I can calculate \\
the number of books to be purchased, and just multiply \\
every proportion value in the data.
"""
from math import floor

import matplotlib.pyplot as plt
from matplotlib.container import BarContainer
from database import get_book, \
    get_logs, \
    Log, \
    Book
from pprint import pformat
from typing import Callable


def get_genre_prevalence_in_database() -> dict[str, int]:
    """Returns a sorted dataset corresponding to the prevalence \\
    of genres in the entire database."""
    out: dict[str, int] = {}
    i = 1

    while True:
        book = get_book(i)
        if book is None:
            return dict(sorted(out.items(), key=lambda item: 1 / item[1]))
        elif book[1] in out.keys():
            out[book[1]] += 1
        else:
            out[book[1]] = 1
        i += 1


def get_author_prevalence_in_database() -> dict[str, int]:
    """Returns a sorted dataset corresponding to the prevalence \\
    of authors in the entire database."""
    out: dict[str, int] = {}
    i = 1

    while True:
        book = get_book(i)
        if book is None:
            return dict(sorted(out.items(), key=lambda item: 1 / item[1]))
        elif book[3] in out.keys():
            out[book[3]] += 1
        else:
            out[book[3]] = 1
        i += 1


def get_book_prevalence_in_logfile() -> dict[Book, int]:
    """Returns a sorted dataset corresponding to the prevalence \\
    of particular books in the logfile. Books with a prevalence \\
    of 0 are not included in this dataset."""
    logs: list[Log] = get_logs()
    out: dict[Book, int] = {}

    for log in logs:
        book = get_book(log[1])
        if book in out.keys():
            out[book] += 1
        else:
            out[book] = 1

    return dict(sorted(out.items(), key=lambda item: 1 / item[1]))


def get_genre_prevalence_in_logfile() -> dict[str, int]:
    """Returns a sorted dataset corresponding to the prevalence \\
    of genres in the logfile. Genres with a prevalence \\
    of 0 are not included in this dataset."""
    book_prevalence = get_book_prevalence_in_logfile()
    out: dict[str, int] = {}

    for book in book_prevalence.keys():
        if book[1] in out.keys():
            out[book[1]] += book_prevalence[book]
        else:
            out[book[1]] = book_prevalence[book]

    return dict(sorted(out.items(), key=lambda item: 1 / item[1]))


def get_author_prevalence_in_logfile() -> dict[str, int]:
    """Returns a sorted dataset corresponding to the prevalence \\
    of authors in the logfile. Authors with a prevalence \\
    of 0 are not included in this dataset."""
    book_prevalence: dict[Book, int] = get_book_prevalence_in_logfile()
    out: dict[str, int] = {}

    for book in book_prevalence.keys():
        if book[3] in out.keys():
            out[book[3]] += book_prevalence[book]
        else:
            out[book[3]] = book_prevalence[book]

    return dict(sorted(out.items(), key=lambda item: 1 / item[1]))


def get_average_book_price_in_logfile() -> float:
    """Returns the average price of all the books \\
    in the logfile."""

    book_weights = get_book_prevalence_in_logfile()
    out = 0

    # compute weighted sum
    for book in book_weights.keys():
        price: int = get_book(book[0])[4]
        out += price * book_weights[book]

    return out / sum(book_weights.values())


def get_recommendation_data(budget: int) -> dict[str, dict[str, int]]:
    """Returns a nested dictionary containing recommendation data."""
    # get relevant data
    author_prevalence = get_author_prevalence_in_logfile()
    genre_prevalence = get_genre_prevalence_in_logfile()
    count: int = floor(budget / get_average_book_price_in_logfile())

    # compute proportions with dictionary comprehensions
    author_recommendations = {k: round(count*v/sum(author_prevalence.values()))
                              for k, v in author_prevalence.items()}
    genre_recommendations = {k: round(count*v/sum(genre_prevalence.values()))
                             for k, v in genre_prevalence.items()}

    # construct output
    out = {'author_recommendation': author_recommendations,
           'genre_recommendation': genre_recommendations}

    return out


def get_recommendation_string(budget: int) -> str:
    """Returns a string describing the given recommendations, \\
    which is then displayed on the **Order** view."""
    # get data
    average_price = get_average_book_price_in_logfile()
    data = get_recommendation_data(budget)

    # get most significant data points
    max_author = '', 0
    max_genre = '', 0
    for author in data['author_recommendation'].keys():
        if data['author_recommendation'][author] > max_author[1]:
            max_author = author, data['author_recommendation'][author]

    for genre in data['genre_recommendation'].keys():
        if data['genre_recommendation'][genre] > max_genre[1]:
            max_genre = genre, data['genre_recommendation'][genre]

    out: str = f"Reading from the logfile, we observe that the " \
               f"average price of a popular book is ${average_price:.2f}." \
               f"\n\n With a budget of ${budget}, this yields " \
               f"~{round(budget/average_price)} books. This decision " \
               f"should be allocated according to the chart. \n" \
               f"In particular, this recommendation picks " \
               f"{max_author[0].title()} as the most important, with " \
               f"{max_author[1]} books allocated. To focus on genre, " \
               f"however, it picks {max_genre[0].title()} as the most " \
               f"important, with {max_genre[1]} books allocated."
    return out


def get_recommendation_multiplot(author_data: dict[str, int],
                                 genre_data: dict[str, int],
                                 just_authors: bool = False,
                                 just_genres: bool = False,
                                 rough_budget: bool = False) -> plt.Figure:
    """Constructs and returns a plot to be used in the \\
    **Recommendation** menu."""
    # initial setup and configurations
    font = {'family': 'helvetica',
            'weight': 'bold',
            'size': 3}

    plt.rc('font', **font)

    figure, (plots) = plt.subplots(1, 2,
                                   constrained_layout=True,
                                   sharey='all')
    figure.set_size_inches(4, 5)
    figure.set_dpi(300)

    plots[0].xaxis.set_visible(False)
    plots[1].xaxis.set_visible(False)
    plots[1].yaxis.set_visible(False)

    for edge in ['top', 'bottom', 'right']:
        plots[0].spines[edge].set_visible(False)
        plots[1].spines[edge].set_visible(False)

    plots[1].spines['left'].set_visible(False)

    # check whether options are valid
    if just_authors and just_genres:
        raise ValueError({"just_authors": just_authors,
                          "just_genres": just_genres})
    elif just_authors and len(author_data) == 0:
        raise ValueError({"just_authors": just_authors,
                          "author_data": author_data})
    elif just_genres and len(genre_data) == 0:
        raise ValueError({"just_genres": just_genres,
                          "genre_data": genre_data})

    left_plot: plt.Axes = plots[0]
    right_plot: plt.Axes = plots[1]

    left_plot.title.set_text('Authors')
    right_plot.title.set_text('Genres')

    # construct author plot
    if not just_genres:
        last_height = 0
        for key, value in zip(list(author_data.keys()),
                              list(author_data.values())):
            if value == 0:
                continue
            bar: BarContainer = left_plot.bar('a', value,
                                              bottom=last_height,
                                              yerr=0.1*value,
                                              width=0.5)
            pos = bar.patches[0].get_patch_transform().transform((0, 0.5))
            left_plot.annotate(key.title(), pos)
            last_height += value
            if not rough_budget:
                bar.errorbar.remove()
    else:
        left_data_total = sum(author_data.values())
        left_plot.bar('a', left_data_total, color='grey')

    # construct genre plot
    if not just_authors:
        last_height = 0
        for key, value in zip(list(genre_data.keys()),
                              list(genre_data.values())):
            if value == 0:
                continue
            bar: BarContainer = right_plot.bar('g', value,
                                               bottom=last_height,
                                               yerr=0.05*value)
            pos = bar.patches[0].get_patch_transform().transform((0.2, 0.5))
            right_plot.annotate(key.title(), pos)
            last_height += value
            if not rough_budget:
                bar.errorbar.remove()
    else:
        right_data_total = sum(genre_data.values())
        right_plot.bar('a', right_data_total, color='grey')

    return figure


def get_order_menu_multiplot(author_data_function: Callable[[], dict[str, int]],
                             genre_data_function: Callable[[], dict[str, int]],
                             titles: tuple[str, str]) -> plt.Figure:
    """Constructs and returns a plot to be used \\
    in the `Order` menu."""

    # configure visual settings
    font = {'family': 'helvetica',
            'weight': 'bold',
            'size': 4}

    plt.rc('font', **font)

    figure, (plots) = plt.subplots(2, 1, constrained_layout=True)
    figure.set_size_inches(3.6, 4.7)
    figure.set_dpi(240)
    # figure.set_facecolor(None)
    # figure.set_alpha(0.0)

    # get relevant datasets from arguments
    author_data: dict[str, int] = author_data_function()
    genre_data: dict[str, int] = genre_data_function()

    # construct upper plot
    upper_plot: plt.Axes = plots[0]
    upper_plot_labels, upper_plot_data = list(
        zip(*reversed(list(author_data.items())[:7]))
    )
    upper_plot_bars = upper_plot.barh([label.title()
                                       for label in upper_plot_labels],
                                      upper_plot_data)
    upper_plot.xaxis.set_visible(False)
    upper_plot.spines['top'].set_visible(False)
    upper_plot.spines['bottom'].set_visible(False)
    upper_plot.spines['left'].set_visible(False)
    upper_plot.spines['right'].set_visible(False)
    upper_plot.title.set_text(titles[0])
    upper_plot.title.set_horizontalalignment('right')
    upper_plot.bar_label(upper_plot_bars)

    # construct lower plot
    lower_plot: plt.Axes = plots[1]
    lower_plot_labels, lower_plot_data = list(
        zip(*reversed(genre_data.items()))
    )
    normalized_lower_plot_data = [100*d/sum(lower_plot_data)
                                  for d in lower_plot_data]
    lower_plot.pie(normalized_lower_plot_data,
                   labels=[label.title() for label in lower_plot_labels],
                   autopct='%.2f')
    lower_plot.title.set_text(titles[1])
    lower_plot.title.set_horizontalalignment('right')
    lower_plot.autoscale()

    return figure


def get_logfile_multiplot() -> plt.Figure:
    """Wraps `get_order_menu_multiplot` to \\
    return a matplotlib figure containing data \\
    about the logfile."""
    return get_order_menu_multiplot(get_author_prevalence_in_logfile,
                                    get_genre_prevalence_in_logfile,
                                    ('Most Popular Authors',
                                     'Most Popular Genres'))


def get_database_multiplot() -> plt.Figure:
    """Wraps `get_order_menu_multiplot` to \\
    return a matplotlib figure containing data \\
    about the database in its entirety."""
    return get_order_menu_multiplot(get_author_prevalence_in_database,
                                    get_genre_prevalence_in_database,
                                    ('Top Authors in Database',
                                     'Genres in Database'))


if __name__ == "__main__":
    # these functions have no parameters, so they're only tested once each

    # get_genre_prevalence_in_database
    print('get_genre_prevalence_in_database test')
    print(pformat(get_genre_prevalence_in_database()))
    print('\n')

    # get_author_prevalence_in_database
    print('get_author_prevalence_in_database test')
    print(pformat(get_author_prevalence_in_database()))
    print('\n')

    # get_book_prevalence_logfile
    print('get_book_prevalence_in_logfile test')
    print(pformat(get_book_prevalence_in_logfile()))
    print('\n')

    # get_genre_prevalence_logfile
    print('get_genre_prevalence_in_logfile test')
    print(pformat(get_genre_prevalence_in_logfile()))
    print('\n')

    # get_author_prevalence_logfile
    print('get_author_prevalence_in_logfile test')
    print(pformat(get_author_prevalence_in_logfile()))
    print('\n')

    # get_recommendation_data
    print('get_recommendation_data test')
    print(pformat(get_recommendation_data(500)))
    print('\n')

    # get_recommendation_string
    print('get_recommendation_string test')
    print(pformat(get_recommendation_string(500)))
    print('\n')

    # multiplots
    get_logfile_multiplot().show()
    get_database_multiplot().show()
    get_recommendation_multiplot(
        get_recommendation_data(500)['author_recommendation'],
        get_recommendation_data(500)['genre_recommendation'],
        False,
        False,
        False
    ).show()
