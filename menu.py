"""Menu Tools and Primary Executable

This script forms both a collection of functions for rendering the menu of the application,
and the primary executable script, which is to say that the program as a whole should be
run using this script.

The main dependency is tkinter, which is used for creating the GUI.
"""

from tkinter import *
from tkinter import ttk
import logging


def clear_widget(widget: Widget):
    for child in widget.winfo_children():
        child.destroy()


def on_search_clicked(event: Event) -> None:
    """To be called when the *Search* button is pressed."""
    event.widget.event_generate("<<SearchClicked>>")


def get_search_results(event: Event) -> None:
    # TODO: write get_search_results
    # get search results into list
    # get reference to results_list
    # dump results into results_list
    return None


def render_search_view(event: Event) -> None:
    """Renders the search window in the main viewport."""
    logging.debug("switched to search view")
    viewport: Frame = event.widget.nametowidget(".viewport")
    clear_widget(viewport)
    search_bar = ttk.Entry(viewport, width=59)
    search_bar.grid(row=0, column=0, padx=5, pady=5)
    search_bar.bind("<Key>", get_search_results)
    results_list = Listbox(viewport, width=60, height=26)
    results_list.grid(row=1, column=0, padx=5, pady=5)

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
    """Initializes the core menu components, and then returns a reference to the window root"""
    # init window
    root = Tk()
    root.title("Library Tool: Oliver Wooding")
    root.configure(bg='black')
    root.geometry("780x505")
    root.bind("<<SearchClicked>>", render_search_view, "+")
    root.bind("<<IOClicked>>", render_io_view, "+")
    root.bind("<<OrderClicked>>", render_order_view, "+")

    # init button frame
    button_frame = Frame(root, width=180, height=60, name="button_frame")
    button_frame.grid(row=0, column=0, padx=10, pady=5)

    # init log frame
    log_frame = Frame(root, width=180, height=430, name="log_frame")
    log_frame.grid(row=1, column=0, rowspan=7, padx=10, pady=5)
    log_frame.configure(bg='purple')

    # init buttons
    search_button = Button(button_frame, text="Search", width=3, height=2)
    search_button.grid(row=0, column=0)
    search_button.bind('<Button-1>', on_search_clicked)
    io_button = Button(button_frame, text='In/Out', width=3, height=2)
    io_button.grid(row=0, column=1)
    io_button.bind('<Button-1>', on_io_clicked)
    purchase_button = Button(button_frame, text='Order', width=3, height=2)
    purchase_button.grid(row=0, column=2)
    purchase_button.bind('<Button-1>', on_order_clicked)

    # init viewport
    viewport = Frame(root, width=560, height=490, name="viewport")
    viewport.grid(row=0, column=1, columnspan=4, rowspan=8, padx=5, pady=5)
    viewport.configure(bg='darkblue')

    return root


if __name__ == "__main__":
    logging.basicConfig(filename="DO_NOT_SUBMIT/general.log", encoding="utf-8", level=0)
    init_menu().mainloop()
