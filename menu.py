"""Menu Tools and Primary Executable

This script forms both a collection of functions for
rendering the menu of the application, and the primary
executable script, which is to say that the program
as a whole should be run using this script.

The main dependency is tkinter, which is used for creating the GUI.
"""
from datetime import date
from tkinter import *
from tkinter import Tk
from tkinter.scrolledtext import ScrolledText
from typing import Literal

from database import get_logs, \
    get_book, \
    Book, \
    get_books_by_title, \
    get_books_by_author, \
    get_books_by_genre, \
    get_book_status, \
    book_id_is_valid
from bookSearch import search_by_query, levenshtein_sort
import logging

PALETTE: dict[str, str] = {
    'grey': '#333',
    'blue': '#4078c0',
    'purple': '#6e5494',
    'dark_grey': '#222',
    'selection_color': '#79667f'
}

# track specific books to be used in the In/Out window
total_selection: set[Book] = set()
specific_selection: Book | None = None

window_state: Literal['search', 'io', 'order'] = 'search'


def clear_widget(widget: Widget):
    """Destroys all the children of the given widget."""
    for child in widget.winfo_children():
        child.destroy()


def return_handler(event: Event):
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
    recent activity section."""
    text_box: ScrolledText = event.widget. \
        nametowidget(".log_frame.!frame.log_frame_content")
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
    """To be called when the *Search* button is pressed."""
    global window_state
    window_state = 'search'
    event.widget.event_generate("<<SearchClicked>>")


def update_search_results(event: Event) -> None:
    """Renders the appropriate search results into the search view."""
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
    elif option_var == 'nlp':
        books = search_by_query(query)

    if query == "":  # prevents results from appearing if there is no query
        books = []

    clear_widget(results_box)

    for book in books:
        # TODO: find a way to pass scrolling data from label to results_box
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
    """Renders the search window in the main viewport."""
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
                                'genre',
                                'nlp')
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
    """To be called when the *In/Out* button is pressed."""
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
    """Selects value from the entry box in the In/Out window."""
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
    event.widget.event_generate('<<SelectionUpdate>>')
    return None


def select_specific_book(event: Event):
    """Selects a specific book in the IO window. \\
    The event is always a child of the book in question."""
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


def update_selection_view(event: Event) -> None:
    """Renders the selection view in the In/Out menu."""
    selection_content: ScrolledText = event \
        .widget \
        .nametowidget('.viewport.selection_frame.!frame.selection_box')

    clear_widget(selection_content)

    # construct a UI element for each book in the selection
    for book in sorted(total_selection, key=lambda x: x[0]):
        # construct parent frame
        entry_frame: Frame = Frame(selection_content,
                                   name=f'{book[2]}')
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
    return None


def render_io_view(event: Event) -> None:
    """Renders the checkout/return window in the main viewport."""
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
                                 height=32)
    selection_box.grid(row=1, column=0, padx=5, pady=5)
    selection_box_label = Label(selection_frame,
                                text='Selection',
                                font=('helvetica', 20, 'bold'),
                                width=20)
    selection_box_label.grid(row=0, column=0)
    button_frame = Frame(viewport,
                         name='button_frame',
                         bg=PALETTE['blue'])
    button_frame.grid(row=0, column=1, padx=5)
    add_button = Button(button_frame,
                        width=1,
                        text='+',
                        font=('helvetica', 20, 'bold'))
    add_button.bind('<1>', add_to_selection_by_entry)
    add_button.grid(row=0, column=0, pady=5, padx=1)
    remove_button: Button = Button(button_frame,
                                   width=1,
                                   text='-',
                                   font=('helvetica', 20, 'bold'))
    remove_button.bind('<1>', remove_from_selection_by_entry)
    remove_button.grid(row=0, column=1, pady=5, padx=1)
    add_entry = Entry(button_frame,
                      width=11,
                      name='add_entry')
    add_entry.grid(row=0, column=2, pady=5, padx=7)
    upper_spacer_frame = Frame(button_frame,
                               height=25,
                               bg=PALETTE['blue'])
    upper_spacer_frame.grid(row=1, column=0, columnspan=3)
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
                               height=40,
                               bg=PALETTE['blue']
                               )
    lower_spacer_frame.grid(row=8, column=0, columnspan=3)
    results_box = Label(button_frame,
                        width=20,
                        height=7,
                        bg=PALETTE['grey'],
                        name='results_box',
                        wraplength=160,
                        font=('helvetica', 15, 'bold'),
                        textvariable=StringVar(
                            value='window init',
                            name='result_box_content'
                        )
                        )
    results_box.grid(row=9, column=0, columnspan=3, pady=5)
    viewport.event_generate('<<SelectionUpdate>>')
    return None


def on_order_clicked(event: Event) -> None:
    """To be called when the *Order* button is pressed."""
    global window_state
    window_state = 'order'
    event.widget.event_generate("<<OrderClicked>>")
    return None


def render_order_view(event: Event) -> None:
    """Renders the ordering window in the main viewport."""
    logging.debug("switched to order view")
    viewport: Frame = event.widget.nametowidget(".viewport")
    clear_widget(viewport)
    return None


def init_menu() -> Tk:
    """Initializes the core menu components, and
    then returns a reference to the window root"""
    # init window
    root: Tk = Tk()
    root.title("Library Tool: Oliver Wooding")
    root.configure(bg=PALETTE['dark_grey'])
    root.geometry("810x505")

    # top-level callbacks
    root.bind("<<SearchClicked>>", render_search_view)
    root.bind("<<IOClicked>>", render_io_view)
    root.bind("<<OrderClicked>>", render_order_view)
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
    logging.basicConfig(filename="DO_NOT_SUBMIT/general.log",
                        encoding="utf-8",
                        level=0)
    init_menu().mainloop()
