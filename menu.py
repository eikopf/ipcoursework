"""Menu Tools and Primary Executable

This script forms both a collection of functions for
rendering the menu of the application, and the primary
executable script, which is to say that the program
as a whole should be run using this script.

The main dependency is tkinter, which is used for creating the GUI.
"""
import logging
from time import perf_counter
from tkinter import *
from tkinter import Tk
from tkinter.scrolledtext import ScrolledText
from typing import Literal, Optional, Callable

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from bookCheckout import member_id_is_valid, \
    checkout_book, \
    checkout_books, \
    reserve_book, \
    reserve_books
from bookReturn import return_book, return_books
from bookSearch import levenshtein_sort
from bookSelect import get_logfile_multiplot, \
    get_database_multiplot, \
    get_recommendation_multiplot, get_recommendation_data, get_recommendation_string
from database import get_logs, \
    get_book, \
    Book, \
    get_books_by_title, \
    get_books_by_author, \
    get_books_by_genre, \
    get_book_status, \
    book_id_is_valid

PALETTE: dict[str, str] = {
    'grey': '#333',
    'blue': '#4078c0',
    'purple': '#6e5494',
    'dark_grey': '#222',
    'selection_color': '#79667f'
}

# track specific books to be used in the In/Out window
total_selection: set[Book] = set()
specific_selection: Optional[Book] = None

# track global state
window_state: Literal['search', 'io', 'order'] = 'search'
canvas_function: Callable[[], plt.Figure] = get_database_multiplot

# track recommendation options
recommendation_options: dict[str, bool] = {
    'just_authors': False,
    'just_genres': False,
    'rough_budget': False
}


def clear_widget(widget: Widget) -> None:
    """Destroys all the children of the given widget."""
    for child in widget.winfo_children():
        child.destroy()


def return_handler(event: Event) -> None:
    """Handles all <Return> events."""
    global window_state
    match window_state:
        case 'search':
            pass
        case 'io':
            # get references to objects in the io window
            entry_text: str = event \
                .widget \
                .nametowidget('.viewport.button_frame.add_entry') \
                .get()

            results_box: Label = event. \
                widget. \
                nametowidget('.viewport.button_frame.results_box')

            # check that the ID in the entry is valid
            try:
                assert book_id_is_valid(int(entry_text))
            except (ValueError, AssertionError):
                results_box.setvar('result_box_content',
                                   f"Tried to add or remove a book with ID: "
                                   f"\'{entry_text}\'.\n\n This ID is invalid.")
                return

            # add or remove the book, based on its status
            if get_book(int(entry_text)) in total_selection:
                remove_from_selection(int(entry_text))
                results_box.setvar('result_box_content',
                                   f"Removed a book with the ID: "
                                   f"\'{entry_text}\'.\n\n "
                                   f"This process was successful.")
                results_box.event_generate('<<SelectionUpdate>>')
                return
            else:
                add_to_selection(int(entry_text))
                results_box.setvar('result_box_content',
                                   f"Added a book with the ID: "
                                   f"\'{entry_text}\'.\n\n "
                                   f"This process was successful.")
                results_box.event_generate('<<SelectionUpdate>>')
                return

        case 'order':
            pass
    return


def update_activity_list(event: Event) -> None:
    """Renders the appropriate lines in the
    **Recent Activity** section."""
    text_box: ScrolledText = event.widget. \
        nametowidget(".log_frame.!frame.log_frame_content")
    text_box.delete('1.0', END)
    logs = get_logs()
    for log in reversed(logs):
        line: str = f"Member {log[2]} "
        if log[0] == 'OUT':
            line += f"checked out the book \"{get_book(log[1])[2].title()}\""
        elif log[0] == "RESERVE":
            line += f"reserved the book \"{get_book(log[1])[2].title()}\""
        elif log[0] == "RETURN":
            line += f"returned the book \"{get_book(log[1])[2].title()}\""
        else:  # handle DERESERVE
            line += f"revoked their reservation " \
                    f"on the book \"{get_book(log[1])[2].title()}\""
        line += f' on {log[3]}.\n\n'
        text_box.insert(END, line)
    return None


def on_search_clicked(event: Event) -> None:
    """To be called when the **Search** button is pressed."""
    global window_state
    window_state = 'search'
    event.widget.event_generate("<<SearchClicked>>")


def update_search_results(event: Event) -> None:
    """Renders the appropriate search results \\
    into the **Search** view."""
    entry: Entry = event.widget.nametowidget('.viewport.search_bar')
    vc: Frame = entry.nametowidget('.viewport')

    frame_name: str = list(
        filter(
            lambda key: key.startswith('!frame'),
            vc.children.keys()))[0]
    option_menu_name: str = list(
        filter(
            lambda key: key.startswith('!optionmenu'),
            vc.children.keys()))[0]

    results_box: ScrolledText = entry \
        .nametowidget(f'.viewport.{frame_name}.search_results')
    option_var: str = entry \
        .nametowidget(f'.viewport.{option_menu_name}') \
        .getvar('option')
    query: str = entry.get().lower()

    books: list[Book] = []
    if option_var == 'title':
        books = get_books_by_title(query)
        books.sort(key=lambda x: levenshtein_sort(query, x[2]))
    elif option_var == 'author':
        books = get_books_by_author(query)
        books.sort(key=lambda x: levenshtein_sort(query, x[3]))
    elif option_var == 'genre':
        books = get_books_by_genre(query)

    if query == "":  # prevents results from appearing if there is no query
        books = []

    clear_widget(results_box)

    for book in books:
        major_text = f'{book[2].title()} by {book[3].title()}'
        minor_text = f'ID: {book[0]}\n' \
                     f'Genre: {book[1].capitalize()}\n' \
                     f'Purchase Price: £{book[4]}\n' \
                     f'Purchase Date: {book[5]}'
        status = get_book_status(book[0])
        status_char = status[0]

        result_frame: Frame = Frame(results_box,
                                    width=75,
                                    height=30,
                                    bg='#333')
        major_label: Label = Label(result_frame,
                                   text=major_text,
                                   wraplength=300,
                                   font=('helvetica', 20, 'bold'),
                                   width=26)
        major_label.grid(row=0, column=1, padx=5, pady=3)
        minor_label: Label = Label(result_frame,
                                   text=minor_text,
                                   wraplength=500,
                                   font=('helvetica', 12, 'italic'),
                                   justify='left')
        minor_label.grid(row=0, column=2, padx=5, pady=2)
        status_label: Label = Label(result_frame,
                                    text=status_char,
                                    font=('helvetica', 25, 'bold'),
                                    height=int(
                                        (minor_label.winfo_height() +
                                         major_label.winfo_height()
                                         ) / 2
                                    ),
                                    width=3)
        match status:
            case 'OUT':
                status_label.config(bg='red')
            case 'RESERVED':
                status_label.config(bg='orange')
            case 'AVAILABLE':
                status_label.config(bg='green')

        status_label.grid(row=0, column=0)

        results_box.window_create(END, window=result_frame)
    return None


def render_search_view(event: Event) -> None:
    """Renders the **Search** window in the main viewport."""
    logging.debug("switched to search view")
    viewport: Frame = event.widget.nametowidget(".viewport")
    clear_widget(viewport)
    search_bar = Entry(viewport,
                       width=49,
                       name='search_bar',
                       bg='#222')
    search_bar.grid(row=0, column=1, padx=5, pady=5)
    search_bar.bind('<KeyRelease>', update_search_results)
    search_options = OptionMenu(viewport,
                                StringVar(name='option'),
                                'title',
                                'author',
                                'genre')
    search_options.grid(row=0, column=0)
    search_options.configure(highlightbackground='#6e5494',
                             font=('helvetica', 13, 'bold'))
    search_options.config(width=4)
    search_options.setvar('option', 'title')
    search_options.bind('<Leave>', update_search_results)
    search_options.bind('<Enter>', update_search_results)
    results_list = ScrolledText(viewport,
                                width=75,
                                height=32,
                                name='search_results',
                                bg='#222')
    results_list.grid(row=1, column=0, columnspan=2, pady=5, padx=5)

    return None


def on_io_clicked(event: Event) -> None:
    """To be called when the **In/Out** \\
    button is pressed."""
    global window_state
    window_state = 'io'
    event.widget.event_generate("<<IOClicked>>")
    return None


def add_to_selection(book_id: int) -> None:
    """Assumes that the input is valid, and adds a book to the selection."""
    total_selection.add(get_book(book_id))
    return None


def remove_from_selection(book_id: int) -> None:
    """Assumes that the input is valid, and removes a book from the selection."""
    total_selection.remove(get_book(book_id))
    return None


def add_to_selection_by_entry(event: Event) -> None:
    """Selects the value from the \\
    entry box in the **In/Out** window."""
    entry_text: str = event \
        .widget \
        .nametowidget('.viewport.button_frame.add_entry') \
        .get()

    results_box: Label = event. \
        widget. \
        nametowidget('.viewport.button_frame.results_box')

    try:
        assert book_id_is_valid(int(entry_text))
    except (ValueError, AssertionError):
        results_box.setvar('result_box_content',
                           f"Tried to add a book with ID: "
                           f"\'{entry_text}\'.\n\n This process failed.")
        return None

    if get_book(int(entry_text)) in total_selection:
        results_box.setvar('result_box_content', f"Tried to add a book with the ID: "
                                                 f"\'{entry_text}\'.\n\n "
                                                 f"This book is already in the selection.")
        return None

    add_to_selection(int(entry_text))
    results_box.setvar('result_box_content', f"Added a book with the ID: "
                                             f"\'{entry_text}\'.\n\n This process was successful.")
    event.widget.event_generate('<<SelectionUpdate>>')
    return None


def remove_from_selection_by_entry(event: Event) -> None:
    """Removes a book from the selection window based on its ID."""
    entry_text: str = event \
        .widget \
        .nametowidget('.viewport.button_frame.add_entry') \
        .get()

    results_box: Label = event. \
        widget. \
        nametowidget('.viewport.button_frame.results_box')

    try:
        assert book_id_is_valid(int(entry_text))
    except (ValueError, AssertionError):
        results_box.setvar('result_box_content',
                           f"Tried to remove a book with ID: "
                           f"\'{entry_text}\'.\n\n This process failed.")
        return None

    if get_book(int(entry_text)) not in total_selection:
        results_box.setvar('result_box_content', f"Tried to remove a book with the ID: "
                                                 f"\'{entry_text}\'.\n\n "
                                                 f"This book is not in the selection.")
        return None

    remove_from_selection(int(entry_text))
    results_box.setvar('result_box_content', f"Removed a book with the ID: "
                                             f"\'{entry_text}\'.\n\n "
                                             "This process was successful.")

    global specific_selection
    if get_book(int(entry_text)) == specific_selection:
        specific_selection = None

    event.widget.event_generate('<<SelectionUpdate>>')
    return None


def select_specific_book(event: Event):
    """Selects a specific book in the **In/Out** window. \\
    The widget which generates the event is always \\
    a child of the book in question."""
    global specific_selection
    new_id = event.widget.master.children['id_buffer'].get()

    results_box: Label = event. \
        widget. \
        nametowidget('.viewport.button_frame.results_box')

    # clear selection color from ui
    for frame in event.widget.master.master.children.values():
        frame['background'] = 'systemWindowBackgroundColor'
        for child in frame.children.values():
            child['background'] = 'systemWindowBackgroundColor'

    new_selection = get_book(int(new_id))

    # if the user clicks on the selected book, deselect it
    if new_selection == specific_selection:
        results_box.setvar('result_box_content',
                           f"Deselected book with ID {new_id}")
        specific_selection = None
        return

    # otherwise, select the new book and update the ui
    specific_selection = new_selection
    selected_ui_component: Frame = event.widget.master
    selected_ui_component['background'] = PALETTE['selection_color']
    for child in selected_ui_component.children.values():
        child['background'] = PALETTE['selection_color']

    results_box.setvar('result_box_content',
                       f"Selected book with ID {new_id}")
    return


def select_specific_book_no_callback(book_container: Frame):
    """An explicit variant of `select_specific_book` to ensure that \\
    the selected book is always rendered appropriately."""
    global specific_selection

    new_id = book_container.children['id_buffer'].get()

    results_box: Label = book_container.nametowidget(
        '.viewport.button_frame.results_box'
    )

    # clear selection color from ui
    for frame in book_container.master.children.values():
        frame['background'] = 'systemWindowBackgroundColor'
        for child in frame.children.values():
            child['background'] = 'systemWindowBackgroundColor'

    new_selection = get_book(int(new_id))

    specific_selection = new_selection
    selected_ui_component: Frame = book_container
    selected_ui_component['background'] = PALETTE['selection_color']
    for child in selected_ui_component.children.values():
        child['background'] = PALETTE['selection_color']

    results_box.setvar('result_box_content',
                       f"Selected book with ID {new_id}")
    return


def update_selection_view(event: Event) -> None:
    """Renders the selection view in the **In/Out** menu."""
    selection_content: ScrolledText = event \
        .widget \
        .nametowidget('.viewport.selection_frame.!frame.selection_box')

    clear_widget(selection_content)

    # construct a UI element for each book in the selection
    for book in sorted(total_selection, key=lambda x: x[0]):
        # construct parent frame
        entry_frame: Frame = Frame(selection_content,
                                   name=f'{book[2]}',
                                   cursor='arrow')
        # this entry is never rendered, it only contains data
        id_buffer = Entry(entry_frame, name='id_buffer')
        id_buffer.config(textvariable=IntVar(id_buffer, book[0]))

        id_label: Label = Label(entry_frame,
                                text=f'ID: {book[0]}',
                                font=('helvetica', 20, 'bold'),
                                width=4,
                                name='id_label')
        id_label.grid(column=0, row=0)
        id_label.bind('<1>', select_specific_book)
        title_label: Label = Label(entry_frame,
                                   text=book[2].title(),
                                   font=('helvetica', 14, 'bold'),
                                   wraplength=200,
                                   width=28,
                                   name='title_label')
        title_label.grid(column=1, row=0)
        title_label.bind('<1>', select_specific_book)
        selection_content.window_create(END, window=entry_frame)

        global specific_selection
        if specific_selection is not None and specific_selection[0] == book[0]:
            select_specific_book_no_callback(entry_frame)
    return None


def on_reserve_clicked(event: Event) -> None:
    """Reserves the book stored in `specific_selection`."""
    global specific_selection, total_selection

    member_id: str = event.widget.nametowidget(
        '.viewport.button_frame.!frame.member_id_entry'
    ).get()

    results_box: Label = event.widget.nametowidget(
        '.viewport.button_frame.results_box'
    )

    if specific_selection is None:
        results_box.setvar('result_box_content',
                           f"Process failed; "
                           f"no book was "
                           f"selected.")
        return

    if not member_id_is_valid(member_id):
        results_box.setvar('result_box_content',
                           f"Process failed; "
                           f"member ID \"{member_id}\" "
                           f"is invalid.")
        return

    try:
        reserve_book(specific_selection[0], member_id)
    except (IOError, IndexError):
        results_box.setvar('result_box_content',
                           f"Process failed; "
                           f"{specific_selection[2].title()} "
                           f"is not available "
                           f"to reserve. ")
        return

    total_selection.remove(specific_selection)

    results_box.setvar('result_box_content',
                       f"Process successful; "
                       f"{specific_selection[2].title()} "
                       f"was reserved.")

    specific_selection = None

    # inject updating events
    event.widget.event_generate(
        '<<SelectionUpdate>>'
    )
    event.widget.event_generate(
        '<<LogUpdate>>'
    )
    return


def on_reserve_all_clicked(event: Event) -> None:
    """Reserves all the books stored in `total_selection`."""
    global specific_selection, total_selection

    member_id: str = event.widget.nametowidget(
        '.viewport.button_frame.!frame.member_id_entry'
    ).get()

    results_box: Label = event.widget.nametowidget(
        '.viewport.button_frame.results_box'
    )

    books = total_selection.copy()

    if not member_id_is_valid(member_id):
        results_box.setvar('result_box_content',
                           f"Process failed; "
                           f"member ID \"{member_id}\" "
                           f"is invalid.")
        return

    try:
        reserve_books([book[0] for book in books], member_id)
    except (IOError, IndexError):
        results_box.setvar('result_box_content',
                           f"Process failed; "
                           f"one or more books "
                           f"was not available "
                           f"to reserve.")
        return

    total_selection = set()
    specific_selection = None

    results_box.setvar('result_box_content',
                       f"Process successful; "
                       f"all books have been "
                       f"reserved.")

    # inject updating events
    event.widget.event_generate(
        '<<SelectionUpdate>>'
    )
    event.widget.event_generate(
        '<<LogUpdate>>'
    )
    return


def on_checkout_clicked(event: Event) -> None:
    """Checks out the book stored in `specific_selection`"""
    global specific_selection, total_selection

    member_id: str = event.widget.nametowidget(
        '.viewport.button_frame.!frame.member_id_entry'
    ).get()

    results_box: Label = event.widget.nametowidget(
        '.viewport.button_frame.results_box'
    )

    if specific_selection is None:
        results_box.setvar('result_box_content',
                           f"Process failed; "
                           f"no book was "
                           f"selected.")
        return

    if not member_id_is_valid(member_id):
        results_box.setvar('result_box_content',
                           f"Process failed; "
                           f"member ID \"{member_id}\" "
                           f"is invalid.")
        return

    try:
        checkout_book(specific_selection[0], member_id)
    except (IOError, IndexError):
        results_box.setvar('result_box_content',
                           f"Process failed; "
                           f"{specific_selection[2].title()} "
                           f"is not available "
                           f"to check out. ")
        return

    total_selection.remove(specific_selection)

    results_box.setvar('result_box_content',
                       f"Process successful; "
                       f"{specific_selection[2].title()} "
                       f"was checked out.")

    specific_selection = None

    # inject updating events
    event.widget.event_generate(
        '<<SelectionUpdate>>'
    )
    event.widget.event_generate(
        '<<LogUpdate>>'
    )
    return


def on_checkout_all_clicked(event: Event) -> None:
    """Checks out all the books stored in `total_selection`"""
    global specific_selection, total_selection

    member_id: str = event.widget.nametowidget(
        '.viewport.button_frame.!frame.member_id_entry'
    ).get()

    results_box: Label = event.widget.nametowidget(
        '.viewport.button_frame.results_box'
    )

    if not member_id_is_valid(member_id):
        results_box.setvar('result_box_content',
                           f"Process failed; "
                           f"member ID \"{member_id}\" "
                           f"is invalid.")
        return

    books = total_selection.copy()

    try:
        checkout_books([book[0] for book in books], member_id)
    except (IOError, IndexError):
        results_box.setvar('result_box_content',
                           f"Process failed; at "
                           f"least one of the "
                           f"selected books is "
                           f"not available to "
                           f"be checked out.")
        return

    # reset selection
    total_selection = set()
    specific_selection = None

    results_box.setvar('result_box_content',
                       f"Process successful; "
                       f"all books have "
                       f"been checked out.")

    # inject updating events
    event.widget.event_generate(
        '<<SelectionUpdate>>'
    )
    event.widget.event_generate(
        '<<LogUpdate>>'
    )
    return


def on_return_clicked(event: Event) -> None:
    """Returns the book stored in `specific_selection`."""
    global specific_selection, total_selection

    results_box: Label = event.widget.nametowidget(
        '.viewport.button_frame.results_box'
    )

    book: Book | None = specific_selection

    if book is None:
        results_box.setvar('result_box_content',
                           f"Process failed; no book"
                           f" was selected.")
        return

    try:
        return_book(book[0])
    except (TypeError, IOError):
        results_box.setvar('result_box_content',
                           f"Process failed; the "
                           f"selected book is "
                           f"not out.")
        return

    results_box.setvar('result_box_content',
                       f"Process successful; "
                       f"{book[2].title()} "
                       f"was returned.")

    # remove the book from the selection
    total_selection.remove(book)
    specific_selection = None

    # inject updating events
    event.widget.event_generate(
        '<<SelectionUpdate>>'
    )
    event.widget.event_generate(
        '<<LogUpdate>>'
    )
    return


def on_return_all_clicked(event: Event) -> None:
    """Returns all the books stored in `total_selection`."""
    global total_selection, specific_selection

    results_box: Label = event.widget.nametowidget(
        '.viewport.button_frame.results_box'
    )

    books = total_selection.copy()

    try:
        return_books([book[0] for book in books])
    except (IOError, IndexError):
        results_box.setvar('result_box_content',
                           f"Process failed; at "
                           f"least one of the "
                           f"selected books is "
                           f"not out.")
        return

    total_selection = set()
    specific_selection = None

    results_box.setvar('result_box_content',
                       f"Process successful; "
                       f"all books have "
                       f"been returned.")

    # inject updating events
    event.widget.event_generate(
        '<<SelectionUpdate>>'
    )
    event.widget.event_generate(
        '<<LogUpdate>>'
    )
    return


def render_io_view(event: Event) -> None:
    """Renders the **In/Out** window in the main viewport."""
    logging.debug("switched to io view")
    viewport: Frame = event.widget.nametowidget(".viewport")
    clear_widget(viewport)

    selection_frame = Frame(viewport,
                            name='selection_frame',
                            bg=PALETTE['blue'])
    selection_frame.bind('<<SelectionUpdate>>', update_selection_view)
    selection_frame.grid(row=0, column=0, pady=5, padx=5)
    selection_box = ScrolledText(selection_frame,
                                 name='selection_box',
                                 bg='#222',
                                 width=40,
                                 height=32,
                                 cursor='arrow')
    selection_box.grid(row=1, column=0, padx=5, pady=5)
    selection_box_label = Label(selection_frame,
                                text='Selection',
                                font=('helvetica', 20, 'bold'),
                                width=20,
                                bg=PALETTE['blue'])
    selection_box_label.grid(row=0, column=0)
    button_frame = Frame(viewport,
                         name='button_frame',
                         bg=PALETTE['blue'])

    # construct right-side container
    button_frame.grid(row=0, column=1, padx=5)

    # construct the button called '+'
    add_button = Button(button_frame,
                        width=1,
                        text='+',
                        font=('helvetica', 20, 'bold'))
    add_button.bind('<1>', add_to_selection_by_entry)
    add_button.grid(row=0, column=0, pady=5, padx=1)

    # construct the button called '-'
    remove_button: Button = Button(button_frame,
                                   width=1,
                                   text='-',
                                   font=('helvetica', 20, 'bold'))
    remove_button.bind('<1>', remove_from_selection_by_entry)
    remove_button.grid(row=0, column=1, pady=5, padx=1)

    # construct the uppermost entry, for IDs
    add_entry = Entry(button_frame,
                      width=11,
                      name='add_entry')
    add_entry.grid(row=0, column=2, pady=5, padx=7)

    # construct the lower entry, for member IDs
    member_entry_frame = Frame(button_frame,
                               height=25,
                               bg=PALETTE['blue'])
    member_entry_frame.grid(row=1, column=0, columnspan=3)
    member_label: Label = Label(member_entry_frame,
                                name='member_id_label',
                                font=('helvetica', 15, 'bold'),
                                bg=PALETTE['blue'])
    member_label.config(textvariable=StringVar(member_label, 'Member ID: '))
    member_label.grid(row=0, column=0, padx=5, pady=5)
    member_entry: Entry = Entry(member_entry_frame,
                                name='member_id_entry',
                                width=11)
    member_entry.grid(row=0, column=1, pady=5)
    member_frame_lower_spacer: Frame = Frame(member_entry_frame,
                                             height=35,
                                             bg=PALETTE['blue'])
    member_frame_lower_spacer.grid(row=1, columnspan=2)

    # construct action buttons
    reserve_button = Button(button_frame,
                            text='Reserve',
                            font=('helvetica', 15, 'bold'),
                            width=15)
    reserve_button.grid(row=2, column=0, columnspan=3)
    reserve_all_button = Button(button_frame,
                                text='Reserve All',
                                font=('helvetica', 15, 'bold'),
                                width=15)
    reserve_all_button.grid(row=3, column=0, columnspan=3)
    checkout_button = Button(button_frame,
                             text='Checkout',
                             font=('helvetica', 15, 'bold'),
                             width=15)
    checkout_button.grid(row=4, column=0, columnspan=3)
    checkout_all_button = Button(button_frame,
                                 text='Checkout All',
                                 font=('helvetica', 15, 'bold'),
                                 width=15)
    checkout_all_button.grid(row=5, column=0, columnspan=3)
    return_button = Button(button_frame,
                           text='Return',
                           font=('helvetica', 15, 'bold'),
                           width=15)
    return_button.grid(row=6, column=0, columnspan=3)
    return_all_button = Button(button_frame,
                               text='Return All',
                               font=('helvetica', 15, 'bold'),
                               width=15)
    return_all_button.grid(row=7, column=0, columnspan=3)
    lower_spacer_frame = Frame(button_frame,
                               height=35,
                               bg=PALETTE['blue']
                               )
    lower_spacer_frame.grid(row=8, column=0, columnspan=3)

    # construct results box for success/failure messages
    results_box = Label(button_frame,
                        width=20,
                        height=7,
                        bg=PALETTE['grey'],
                        name='results_box',
                        wraplength=160,
                        font=('helvetica', 15, 'italic'),
                        textvariable=StringVar(
                            value='',
                            name='result_box_content'
                        )
                        )
    results_box.grid(row=9, column=0, columnspan=3, pady=5)

    # side button bindings
    reserve_button.bind('<1>', on_reserve_clicked)
    reserve_all_button.bind('<1>', on_reserve_all_clicked)
    checkout_button.bind('<1>', on_checkout_clicked)
    checkout_all_button.bind('<1>', on_checkout_all_clicked)
    return_button.bind('<1>', on_return_clicked)
    return_all_button.bind('<1>', on_return_all_clicked)

    viewport.event_generate('<<SelectionUpdate>>')
    return


def on_order_clicked(event: Event) -> None:
    """To be called when the *Order* button is pressed."""
    global window_state
    window_state = 'order'
    event.widget.event_generate('<<OrderClicked>>')
    return


def change_canvas_function_to_db(event: Event) -> None:
    """Changes the matplotlib graphic in the **Order** \\
    view to the version that contains data about the entire \\
    database."""
    global canvas_function
    canvas_function = get_database_multiplot
    event.widget.event_generate('<<OrderClicked>>')
    results_box = event.widget.nametowidget('.viewport.menu_frame.results_box')
    results_box.config(text='Switched to database view.')


def change_canvas_function_to_lf(event: Event) -> None:
    """Changes the matplotlib graphic in the **Order**\\
    view to the version that contains data about activity \\
    in the logfile."""
    global canvas_function
    canvas_function = get_logfile_multiplot
    event.widget.event_generate('<<OrderClicked>>')
    results_box = event.widget.nametowidget('.viewport.menu_frame.results_box')
    results_box.config(text='Switched to activity view.')


def on_get_recommendations_clicked(event: Event) -> None:
    """A callback function triggered by the \\
    **Get Recommendations** button in the **Order** view."""
    global window_state
    window_state = 'recommendations'
    event.widget.event_generate('<<GetRecommendationsClicked>>')


def render_recommendation_view(event: Event) -> None:
    """Renders the recommendation view in the main \\
    viewport. This function is always preceded by a call \\
    to `render_order_view`."""
    logging.debug("switched to recommendation view")
    viewport: Frame = event.widget.nametowidget(".viewport")
    global recommendation_options

    # get budget info, return to previous view if this fails
    try:
        budget: int = int(
            event.widget.nametowidget(".viewport.menu_frame.budget_entry").get()
        )
    except (ValueError, TypeError):
        root = event.widget.nametowidget('.')
        event.widget.event_generate('<<OrderClicked>>')
        results_box: Label = root.nametowidget('.viewport'
                                               '.menu_frame'
                                               '.results_box')
        results_box.config(text='Failed to retrieve recommendations; '
                                'the provided budget could not be '
                                'converted to an integer.')
        return

    clear_widget(viewport)

    # initialize top-level containers
    left_frame: Frame = Frame(viewport,
                              name='left_frame')
    left_frame.grid(row=0, column=0)
    recommendation_title: Label = Label(left_frame,
                                        text='Order Recommendations',
                                        font=('helvetica', 20, 'bold'))
    recommendation_title.grid(row=0, column=0)
    text_body: Label = Label(left_frame,
                             text=get_recommendation_string(budget),
                             font=('helvetica', 14),
                             wraplength=200)
    text_body.grid(row=1, column=0, padx=7)
    canvas_frame: Frame = Frame(viewport,
                                name='canvas_frame')
    canvas_frame.grid(row=0, column=1)

    # get and draw matplotlib graphic
    recommendations = get_recommendation_data(budget)
    try:
        canvas = FigureCanvasTkAgg(
            get_recommendation_multiplot(recommendations['author_recommendation'],
                                         recommendations['genre_recommendation'],
                                         just_authors=
                                         recommendation_options['just_authors'],
                                         just_genres=
                                         recommendation_options['just_genres'],
                                         rough_budget=
                                         recommendation_options['rough_budget']),
            master=canvas_frame)
    except ValueError:
        root = event.widget.nametowidget('.')
        event.widget.event_generate('<<OrderClicked>>')
        results_box: Label = root.nametowidget('.viewport'
                                               '.menu_frame'
                                               '.results_box')
        results_box.config(text='Failed to retrieve recommendations; '
                                'the selected options are '
                                'incompatible')
        return
    canvas.get_tk_widget().config(width=320, height=470)
    canvas.get_tk_widget().grid(row=0, column=0)
    return


def flip_option(option: str):
    """A utility function for handling the state of \\
    the options on the **Order** menu."""
    global recommendation_options
    recommendation_options[option] = not recommendation_options[option]


def render_order_view(event: Event) -> None:
    """Renders the ordering window in the main viewport."""
    logging.debug("switched to order view")
    viewport: Frame = event.widget.nametowidget(".viewport")
    clear_widget(viewport)

    # initialize top-level frames
    canvas_frame: Frame = Frame(viewport,
                                name="canvas_frame",
                                bg=PALETTE['blue'])
    canvas_frame.grid(row=0, column=0)
    menu_frame: Frame = Frame(viewport,
                              name="menu_frame",
                              bg=PALETTE['blue'])
    menu_frame.grid(row=0, column=1)

    # initializing results box
    results_box: Label = Label(menu_frame,
                               text='',
                               height=8,
                               width=20,
                               font=('helvetica', 15, 'italic'),
                               name='results_box',
                               wraplength=180)
    results_box.grid(row=8, column=0, columnspan=2, padx=3, pady=2)

    # initialize budget entry components in menu_frame
    budget_label: Label = Label(menu_frame,
                                text='Budget:',
                                font=('helvetica', 18, 'bold'),
                                bg=PALETTE['blue'])
    budget_label.grid(row=0, column=0, padx=3)
    budget_label.bind('<Enter>',
                      lambda _: results_box
                      .config(
                          text='Enter a budget here, '
                               'and then click "Get Recommendations" '
                               'to receive recommendations!'
                      ))
    budget_label.bind('<Leave>', lambda _: results_box.config(text=""))
    budget_entry: Entry = Entry(menu_frame,
                                width=10,
                                name='budget_entry')
    budget_entry.grid(row=0, column=1, pady=5, padx=3)

    # initialize option components in menu_frame
    just_authors_option: Checkbutton = Checkbutton(menu_frame,
                                                   text='Just Authors',
                                                   font=('helvetica', 10),
                                                   bg=PALETTE['blue'],
                                                   name='just_authors_option',
                                                   command=lambda:
                                                   flip_option('just_authors'))
    just_authors_option.grid(row=1, column=1, pady=3, sticky=W)
    just_authors_option.bind('<Enter>',
                             lambda _: results_box
                             .config(
                                 text='Select this option '
                                      'to restrict the recommendation '
                                      'to just authors, rather than '
                                      'both authors and genres.'
                             ))
    just_authors_option.bind('<Leave>', lambda _: results_box.config(text=''))
    just_genres_option: Checkbutton = Checkbutton(menu_frame,
                                                  text='Just Genres',
                                                  font=('helvetica', 10),
                                                  bg=PALETTE['blue'],
                                                  name='just_genres_option',
                                                  command=lambda:
                                                  flip_option('just_genres'))
    just_genres_option.grid(row=2, column=1, pady=3, sticky=W)
    just_genres_option.bind('<Enter>',
                            lambda _: results_box
                            .config(
                                text='Select this option '
                                     'to restrict the recommendation '
                                     'to just genres, rather than '
                                     'both authors and genres.'
                            ))
    just_genres_option.bind('<Leave>', lambda _: results_box.config(text=''))
    rough_budget_option: Checkbutton = Checkbutton(menu_frame,
                                                   text='Rough Budget',
                                                   font=('helvetica', 10),
                                                   bg=PALETTE['blue'],
                                                   name='rough_budget_option',
                                                   command=lambda:
                                                   flip_option('rough_budget'))
    rough_budget_option.grid(row=3, column=1, pady=3, sticky=W)
    rough_budget_option.bind('<Enter>',
                             lambda _: results_box
                             .config(
                                 text='Select this option '
                                      'to receive a recommendation '
                                      'which may not strictly adhere to '
                                      'the budget.'
                             ))
    rough_budget_option.bind('<Leave>', lambda _: results_box.config(text=''))
    lower_spacer: Frame = Frame(menu_frame,
                                height=100,
                                bg=PALETTE['blue'])
    lower_spacer.grid(row=4, column=0, columnspan=2)

    # adding data-switch buttons
    database_button: Button = Button(menu_frame,
                                     text='Switch to Database View',
                                     width=18,
                                     font=('helvetica', 15, 'bold'))
    database_button.bind('<1>', change_canvas_function_to_db)
    database_button.grid(row=5, column=0, columnspan=2, pady=2)
    logfile_button: Button = Button(menu_frame,
                                    text='Switch to Activity View',
                                    width=18,
                                    font=('helvetica', 15, 'bold'))
    logfile_button.bind('<1>', change_canvas_function_to_lf)
    logfile_button.grid(row=6, column=0, columnspan=2, pady=2)

    # initializing the confirm button
    confirm_button: Button = Button(menu_frame,
                                    text='Get Recommendations',
                                    font=('helvetica', 15, 'bold'),
                                    width=18)
    confirm_button.bind('<1>', on_get_recommendations_clicked)
    confirm_button.grid(row=7, column=0, columnspan=2, padx=3, pady=2)

    # initializing the canvas section
    canvas = FigureCanvasTkAgg(canvas_function(),
                               master=canvas_frame)
    e = Event()
    e.width = 360
    e.height = 470
    canvas.draw()
    canvas.resize(e)
    canvas.get_tk_widget().config(width=360, height=470)
    canvas.get_tk_widget().grid(row=0, column=0)
    return


def init_menu() -> Tk:
    """Initializes the core menu components, and
    then returns a reference to the window root."""
    # init window
    root: Tk = Tk()
    root.title("Library Tool: Oliver Wooding")
    root.configure(bg=PALETTE['dark_grey'])
    root.geometry("810x505")

    # top-level callbacks
    root.bind("<<SearchClicked>>", render_search_view)
    root.bind("<<IOClicked>>", render_io_view)
    root.bind("<<OrderClicked>>", render_order_view)
    root.bind("<<GetRecommendationsClicked>>", render_recommendation_view)
    root.bind("<<LogUpdate>>", update_activity_list)
    root.bind("<<SelectionUpdate>>", update_selection_view)
    root.bind('<Return>', return_handler)

    # init button frame
    button_frame = Frame(root,
                         width=180,
                         height=60,
                         name="button_frame",
                         bg='#fff')
    button_frame.grid(row=0, column=0, padx=10, pady=5)

    # init log frame
    log_frame = Frame(root, width=180, height=430, name="log_frame")
    log_frame.grid(row=1, column=0, rowspan=7, padx=10, pady=5)
    log_frame.configure(bg=PALETTE['purple'])
    log_frame_label = Label(log_frame,
                            name='log_frame_label',
                            text="Recent Activity",
                            font=("helvetica", 20, 'bold'),
                            bg='#6e5494')
    log_frame_label.grid(row=0, column=0, padx=20, pady=5)
    log_entries = ScrolledText(log_frame,
                               name='log_frame_content',
                               wrap='word',
                               width=25,
                               height=28,
                               bg='#222')
    log_entries.grid(row=1, column=0, pady=5, padx=5)
    root.event_generate("<<LogUpdate>>")

    # init buttons
    search_button = Button(button_frame,
                           text="Search",
                           width=4,
                           height=2,
                           font=('helvetica', 15, 'bold'))
    search_button.grid(row=0, column=0)
    search_button.bind('<Button-1>', on_search_clicked)
    io_button = Button(button_frame,
                       text='In/Out',
                       width=4,
                       height=2,
                       font=('helvetica', 15, 'bold'))
    io_button.grid(row=0, column=1)
    io_button.bind('<Button-1>', on_io_clicked)
    order_button = Button(button_frame,
                          text='Order',
                          width=4,
                          height=2,
                          font=('helvetica', 15, 'bold'))
    order_button.grid(row=0, column=2)
    order_button.bind('<Button-1>', on_order_clicked)

    # init viewport
    viewport = Frame(root,
                     width=560,
                     height=490,
                     name="viewport",
                     bg=PALETTE['blue'])
    viewport.grid(row=0,
                  column=1,
                  columnspan=4,
                  rowspan=8,
                  padx=5,
                  pady=5)

    # set initial viewport to search
    root.event_generate("<<SearchClicked>>")
    return root


if __name__ == "__main__":
    # measuring start-up time and total runtime
    start_time = perf_counter()
    print('Initializing window...')
    window = init_menu()
    print(f'Window initialized in {perf_counter() - start_time:.4f}s')
    window.mainloop()
    print(f'Application ran for {perf_counter() - start_time:.4f}s')
