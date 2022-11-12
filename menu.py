from tkinter import *


def on_search_clicked(event):
    """To be called when the *Search* button is pressed."""
    print("search")


def on_io_clicked(event):
    """To be called when the *In/Out* button is pressed."""
    print("io")


def on_order_clicked(event):
    """To be called when the *Order* button is pressed."""
    print("order")


def init_menu() -> Tk:
    """Initializes the core menu components, and then returns a reference to the window root"""
    # init window
    root = Tk()
    root.title("Library Tool: Oliver Wooding")
    root.configure(bg='black')
    root.geometry("780x500")

    # init button frame
    button_frame = Frame(root, width=180, height=60)
    button_frame.grid(row=0, column=0, padx=10, pady=5)

    # init log frame
    log_frame = Frame(root, width=180, height=430)
    log_frame.grid(row=1, column=0, rowspan=7, padx=10, pady=5)
    log_frame.configure(bg='purple')

    # init viewport
    viewport = Frame(root, width=560, height=490)
    viewport.grid(row=0, column=1, columnspan=4, rowspan=8, padx=5, pady=5)
    viewport.configure(bg='red')

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

    return root


if __name__ == "__main__":
    init_menu().mainloop()
