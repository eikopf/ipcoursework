"""Menu Tools and Primary Executable

This script forms both a collection of functions for
rendering the menu of the application, and the primary
executable script, which is to say that the program
as a whole should be run using this script.

The main dependency is tkinter, which is used for creating the GUI.
"""

from tkinter import *
from tkinter import Tk
from tkinter.scrolledtext import ScrolledText
from database import get_logs, \
    get_book, \
    Book, \
    get_books_by_title, \
    get_books_by_author, \
    get_books_by_genre, \
    get_book_status
from bookSearch import search_by_query, levenshtein_sort
import logging

PALETTE: dict[str, str] = {
    'grey': '#333',
    'blue': '#4078c0',
    'purple': '#6e5494',
    'dark_grey': '#222'
}

# track specific books to be used in the In/Out window
book_selection: list[Book] = []
user_selection: list[Book] = []


def clear_widget(widget: Widget):
    """Destroys all the children of the given widget."""
    for child in widget.winfo_children():
        child.destroy()


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
                                    height=int((minor_label.winfo_height() + major_label.winfo_height()) / 2),
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
    event.widget.event_generate("<<IOClicked>>")
    return None


def render_io_view(event: Event) -> None:
    """Renders the checkout/return window in the main viewport."""
    logging.debug("switched to io view")
    viewport: Frame = event.widget.nametowidget(".viewport")
    clear_widget(viewport)

    selection_frame = Frame(viewport,
                            name='selection_frame',
                            bg=PALETTE['blue'])
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
                        width=2,
                        text='Add',
                        font=('helvetica', 15, 'bold'))
    add_button.grid(row=0, column=0, pady=5, padx=5)
    add_entry = Entry(button_frame, width=15)
    add_entry.grid(row=0, column=1, pady=5, padx=7)
    upper_spacer_frame = Frame(button_frame,
                               height=25,
                               bg=PALETTE['blue'])
    upper_spacer_frame.grid(row=1, column=0, columnspan=2)
    reserve_button = Button(button_frame,
                            text='Reserve',
                            font=('helvetica', 15, 'bold'),
                            width=15)
    reserve_button.grid(row=2, column=0, columnspan=2)
    reserve_all_button = Button(button_frame,
                                text='Reserve All',
                                font=('helvetica', 15, 'bold'),
                                width=15)
    reserve_all_button.grid(row=3, column=0, columnspan=2)
    checkout_button = Button(button_frame,
                             text='Checkout',
                             font=('helvetica', 15, 'bold'),
                             width=15)
    checkout_button.grid(row=4, column=0, columnspan=2)
    checkout_all_button = Button(button_frame,
                                 text='Checkout All',
                                 font=('helvetica', 15, 'bold'),
                                 width=15)
    checkout_all_button.grid(row=5, column=0, columnspan=2)
    return_button = Button(button_frame,
                           text='Return',
                           font=('helvetica', 15, 'bold'),
                           width=15)
    return_button.grid(row=6, column=0, columnspan=2)
    return_all_button = Button(button_frame,
                               text='Return All',
                               font=('helvetica', 15, 'bold'),
                               width=15)
    return_all_button.grid(row=7, column=0, columnspan=2)
    lower_spacer_frame = Frame(button_frame,
                               height=40,
                               bg=PALETTE['blue'])
    lower_spacer_frame.grid(row=8, column=0, columnspan=2)
    results_box = Label(button_frame,
                        width=20,
                        height=7,
                        bg=PALETTE['grey'])
    results_box.grid(row=9, column=0, columnspan=2, pady=5)
    return None


def on_order_clicked(event: Event) -> None:
    """To be called when the *Order* button is pressed."""
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
    root.bind("<<SearchClicked>>", render_search_view)
    root.bind("<<IOClicked>>", render_io_view)
    root.bind("<<OrderClicked>>", render_order_view)
    root.bind("<<LogUpdate>>", update_activity_list)

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
    log_frame.configure(bg='#6e5494')
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
    purchase_button = Button(button_frame,
                             text='Order',
                             width=4,
                             height=2,
                             font=('helvetica', 15, 'bold'))
    purchase_button.grid(row=0, column=2)
    purchase_button.bind('<Button-1>', on_order_clicked)

    # init viewport
    viewport = Frame(root,
                     width=560,
                     height=490,
                     name="viewport",
                     bg='#4078c0')
    viewport.grid(row=0, column=1, columnspan=4, rowspan=8, padx=5, pady=5)

    # set initial viewport to search
    root.event_generate("<<SearchClicked>>")
    return root


if __name__ == "__main__":
    logging.basicConfig(filename="DO_NOT_SUBMIT/general.log",
                        encoding="utf-8",
                        level=0)
    init_menu().mainloop()
