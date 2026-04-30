from rich.live import Live, Group
from rich.table import Table
from threading import Lock

from domain.model import buscalibre
from domain.model.buscalibre import BookPriceHistory


class TablePublisher:
    def __init__(self, refresh_per_second=1):
        self._lock = Lock()
        self._live = self._live = Live(Group(self._build_books_table(), self._build_price_history_table()), refresh_per_second=refresh_per_second)
        self._started = False
        self.published_price_history: dict[str, BookPriceHistory] = {}
        self.published_books: dict[str, buscalibre.Book] = {}

    @staticmethod
    def _build_price_history_table() -> Table:
        table = Table(title="📚 Ultimo precio consultado")

        table.add_column("Nombre")
        table.add_column("Autor")
        table.add_column("Precio Original", justify="right")
        table.add_column("Precio Descuento", justify="right")
        table.add_column("Descuento", justify="center")
        table.add_column("Fecha de consulta", justify="center")
        return table

    @staticmethod
    def _build_books_table() -> Table:
        table = Table(title="📚 Libros")

        table.add_column("Nombre")
        table.add_column("Autor")
        table.add_column("Precio Actual", justify="right")
        table.add_column("Precio Minimo", justify="right")
        table.add_column("Precio Maximo", justify="center")
        table.add_column("Precio promedio", justify="center")
        table.add_column("Fecha última actualizacion", justify="center")
        return table

    @staticmethod
    def add_row_to_price_history_table(table: Table, book_info: buscalibre.BookPriceHistory) -> None:
        table.add_row(
            book_info.title,
            book_info.author,
            f"${book_info.price:,.2f}",
            f"${book_info.discounted_price:,.2f}",
            str(book_info.discount),
            str(book_info.requested_at)
        )

    @staticmethod
    def add_row_to_books_table(table: Table, book: buscalibre.Book) -> None:
        table.add_row(
            book.title,
            book.author,
            f"${book.current_price:,.2f}",
            f"${book.min_price:,.2f}",
            f"${book.max_price:,.2f}",
            f"${book.average_price:,.2f}",
            str(book.last_updated_at)
        )

    def start(self):
        if not self._started:
            self._live.start()
            self._started = True

    def stop(self):
        if self._started:
            self._live.stop()
            self._started = False

    def publish(self, price_history: buscalibre.BookPriceHistory, book: buscalibre.Book) -> None:
        """
        Recibe nuevos datos y actualiza la tabla
        """
        with self._lock:
            price_history_table = self._build_price_history_table()
            self.published_price_history.update({price_history.id.value: price_history})
            for book_id, price_history in self.published_price_history.items():
                self.add_row_to_price_history_table(table=price_history_table, book_info=price_history)
            books_table = self._build_books_table()
            self.published_books.update({price_history.id.value: book})
            for book_id, book_published in self.published_books.items():
                self.add_row_to_books_table(table=books_table, book=book_published)
            self._live.update(Group(books_table, price_history_table))