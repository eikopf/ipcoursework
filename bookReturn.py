from datetime import date
from database import get_logs, \
    write_log, \
    filter_logs_with_id, \
    book_id_is_valid, \
    Log


def return_book(book_id: int):
    last_log: Log = filter_logs_with_id(get_logs(), book_id)[-1]

    if book_id_is_valid(book_id) and last_log[0] == 'OUT':
        write_log(f'RETURN {book_id} {last_log[2]} {date.today()}')
    else:
        raise IOError({'last_log': last_log, 'book_id': book_id})
