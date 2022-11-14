"""Menu Tools and Primary Executable

This script forms both a collection of functions for
rendering the menu of the application, and the primary
executable script, which is to say that the program
as a whole should be run using this script.

The main dependency is tkinter, which is used for creating the GUI.
"""

from tkinter import *
from tkinter import ttk, Tk
from tkinter.scrolledtext import ScrolledText
from database import get_logs, \
    get_book, \
    Book, \
    get_books_by_title, \
    get_books_by_author, \
    get_books_by_genre
from bookSearch import search_by_query
import logging


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
    # TODO: write get_search_results
    entry: Entry = event.widget.nametowidget('.viewport.search_bar')
    vc: Frame = entry.nametowidget('.viewport')

    frame_name: str = list(filter(lambda key: key.startswith('!frame'), vc.children.keys()))[0]
    option_menu_name: str = list(filter(lambda key: key.startswith('!optionmenu'), vc.children.keys()))[0]

    results_box: ScrolledText = entry\
        .nametowidget(f'.viewport.{frame_name}.search_results')
    option_var: str = entry\
        .nametowidget(f'.viewport.{option_menu_name}')\
        .getvar('option')
    query: str = entry.get().lower()

    books: list[Book] = []
    if option_var == 'title':
        books = get_books_by_title(query)
    elif option_var == 'author':
        books = get_books_by_author(query)
    elif option_var == 'genre':
        books = get_books_by_genre(query)
    elif option_var == 'nlp':
        books = search_by_query(query)

    clear_widget(results_box)

    for book in books:
        # TODO: find a way to pass scrolling data from label to results_box
        # TODO: cleanly render the labels in a more appealing way
        result: Label = Label(results_box,
                              text=str(book),
                              wraplength=500,
                              font=('helvetica', 20, 'bold'))
        results_box.window_create(END, window=result)
        pass
    # dump results into results_list
    return None


def render_search_view(event: Event) -> None:
    """Renders the search window in the main viewport."""
    logging.debug("switched to search view")
    viewport: Frame = event.widget.nametowidget(".viewport")
    clear_widget(viewport)
    search_bar = Entry(viewport,
                       width=49,
                       name='search_bar')
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
                                name='search_results')
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
    root.configure(bg='#333')
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
                               height=28)
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
