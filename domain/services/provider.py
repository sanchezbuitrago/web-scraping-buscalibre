from typing import Iterator
from datetime import datetime, timedelta
from domain.model import buscalibre
from domain.model.buscalibre import Book

_LINKS = [
    "https://www.buscalibre.com.co/libro-ikigai/9786289591743/p/55757997",
    "https://www.buscalibre.com.co/libro-deja-de-ser-tu/9786289680317/p/64535281"
]


class BookProvider:
    def __init__(self, retention_time: timedelta) -> None:
        self.state = {}
        self.retention_time = retention_time

    def get_next_book(self, books: list[buscalibre.Book]) -> Iterator[Book | None]:
        for book in books:
            last_book_query = self.state.get(book.id.value, None)
            if last_book_query:
                time_difference = datetime.now() - last_book_query
                if time_difference > self.retention_time:
                    self.state.update({book.id.value: datetime.now()})
                    yield book
            else:
                self.state.update({book.id.value: datetime.now()})
                yield book

        yield None