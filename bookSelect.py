"""Book Recommendation and Data Manipulation Tools

This script provides functions to get data about the \\
application, to manipulate that data, and to produce \\
the required graphics for the application.
"""

import matplotlib.pyplot as plt
from database import get_book, \
    get_logs, \
    Log, \
    Book
from pprint import pformat


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
            out[book[1]] += 1
        else:
            out[book[1]] = 1

    return dict(sorted(out.items(), key=lambda item: 1 / item[1]))


def get_author_prevalence_in_logfile() -> dict[str, int]:
    """Returns a sorted dataset corresponding to the prevalence \\
    of authors in the logfile. Authors with a prevalence \\
    of 0 are not included in this dataset."""
    book_prevalence: dict[Book, int] = get_book_prevalence_in_logfile()
    out: dict[str, int] = {}

    for book in book_prevalence.keys():
        if book[3] in out.keys():
            out[book[3]] += 1
        else:
            out[book[3]] = 1

    return dict(sorted(out.items(), key=lambda item: 1 / item[1]))


def get_order_menu_multiplot() -> tuple[plt.Figure, plt.Figure]:
    """Constructs and returns a plot to be used \\
    in the `Order` menu."""
    font = {'family': 'helvetica',
            'weight': 'bold',
            'size': 4}

    plt.rc('font', **font)

    figure, (plots) = plt.subplots(2, 2, constrained_layout=True)
    figure.set_size_inches(3.6, 4.7)
    figure.set_dpi(240)
    # figure.set_facecolor(None)
    # figure.set_alpha(0.0)

    top_left_data: dict[str, int] = get_author_prevalence_in_database()
    top_right_data: dict[str, int] = get_author_prevalence_in_logfile()
    bottom_left_data: dict[str, int] = get_genre_prevalence_in_database()
    bottom_right_data: dict[str, int] = get_genre_prevalence_in_logfile()

    # construct the top-left subplot
    top_left_plot: plt.Axes = plots[0][0]
    tl_labels, tl_data = list(zip(*reversed(list(top_left_data.items())[:5])))
    top_left_bars = top_left_plot.barh(range(len(tl_data)),
                                       tl_data)

    top_left_plot.spines['top'].set_visible(False)
    top_left_plot.spines['left'].set_visible(False)
    top_left_plot.spines['right'].set_visible(False)
    top_left_plot.spines['bottom'].set_visible(False)
    top_left_plot.get_xaxis().set_visible(False)
    top_left_plot.get_yaxis().set_visible(False)
    top_left_plot.bar_label(top_left_bars,
                            padding=2,
                            labels=[label.title() for label in tl_labels],
                            label_type='center')
    top_left_plot.title.set_text('Most Common Authors')
    top_left_plot.title.set_wrap(True)

    # construct the top-right subplot
    top_right_plot: plt.Axes = plots[0][1]
    top_right_plot.invert_xaxis()
    tr_labels, tr_data = list(zip(*reversed(list(top_right_data.items())[:5])))
    top_right_bars = top_right_plot.barh(range(len(tr_data)),
                                         tr_data)

    top_right_plot.spines['top'].set_visible(False)
    top_right_plot.spines['left'].set_visible(False)
    top_right_plot.spines['right'].set_visible(False)
    top_right_plot.spines['bottom'].set_visible(False)
    top_right_plot.get_xaxis().set_visible(False)
    top_right_plot.get_yaxis().set_visible(False)
    top_right_plot.bar_label(top_right_bars,
                             padding=2,
                             labels=[label.title() for label in tr_labels],
                             label_type='center')
    top_right_plot.title.set_text('Most Active Authors')

    # construct the bottom-left subplot
    bottom_left_plot: plt.Axes = plots[1][0]
    bl_labels, bl_data = list(zip(*reversed(list(bottom_left_data.items()))))
    normalized_bl_data = [100 * (d / sum(bl_data)) for d in bl_data]
    bottom_left_plot.pie(normalized_bl_data,
                         labels=[label.title() for label in bl_labels],
                         textprops={'size': 'smaller'},
                         startangle=190)
    bottom_left_plot.axis('equal')
    bottom_left_plot.title.set_text('Genres in Database')

    # construct the bottom-right subplot
    bottom_right_plot: plt.Axes = plots[1][1]
    br_labels, br_data = list(zip(*reversed(list(bottom_right_data.items()))))
    normalized_br_data = [100 * (d / sum(br_data)) for d in br_data]
    bottom_right_plot.pie(normalized_br_data,
                          labels=[label.title() for label in br_labels],
                          textprops={'size': 'smaller'})
    bottom_right_plot.axis('equal')
    bottom_right_plot.title.set_text('Genres in Logfile')

    return figure


if __name__ == "__main__":
    # these functions have no parameters, so they're only tested once each
    print(
        pformat(get_author_prevalence_in_database(), sort_dicts=False) + '\n'
    )
    print(
        pformat(get_genre_prevalence_in_database(), sort_dicts=False) + '\n'
    )
    print(
        pformat(get_book_prevalence_in_logfile(), sort_dicts=False) + '\n'
    )
    print(
        pformat(get_genre_prevalence_in_logfile(), sort_dicts=False) + '\n'
    )
    print(
        pformat(get_author_prevalence_in_logfile(), sort_dicts=False) + '\n'
    )
    get_order_menu_multiplot().show()
