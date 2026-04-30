import datetime
import decimal

from commons import base_types

class BookAlreadyExistsError(Exception):
    ...

class BookPriceHistory(base_types.Aggregate):
    id: base_types.HumanFriendlyId
    book_id: str
    title: str
    author: str
    price: decimal.Decimal
    discounted_price: decimal.Decimal
    discount: int
    requested_at: datetime.datetime


class Book(base_types.Aggregate):
    id: base_types.HumanFriendlyId
    title: str
    author: str
    link: str
    min_price: decimal.Decimal
    max_price: decimal.Decimal
    average_price: decimal.Decimal
    current_price: decimal.Decimal
    price_history_items: int
    last_updated_at: datetime.datetime
    created_at: datetime.datetime
    book_with_error: bool = False
    error_detail: str = ""

    @classmethod
    def create(cls, title: str, author: str, link: str) -> "Book":
        return Book(
            id=base_types.HumanFriendlyId(),
            title=title,
            author=author,
            link=link,
            min_price=decimal.Decimal(0),
            max_price=decimal.Decimal(0),
            average_price=decimal.Decimal(0),
            current_price=decimal.Decimal(0),
            price_history_items=0,
            last_updated_at=datetime.datetime.now(),
            created_at=datetime.datetime.now()
        )

    def save_book_error(self, error: str) -> None:
        self.book_with_error = True
        self.error_detail = error
        self.last_updated_at = datetime.datetime.now()

    def calculate_price_by_price_history(self, price_history_item: BookPriceHistory) -> None:
        if self.price_history_items == 0:
            self.min_price = price_history_item.discounted_price
            self.max_price = price_history_item.discounted_price
            self.average_price = price_history_item.discounted_price
            self.current_price = price_history_item.discounted_price
            self.price_history_items = 1
            self.last_updated_at = datetime.datetime.now()
            self.error_detail = ""
        else:
            if price_history_item.discounted_price > self.max_price:
                self.max_price = price_history_item.discounted_price
            if price_history_item.discounted_price < self.min_price:
                self.min_price = price_history_item.discounted_price
            self.current_price = price_history_item.discounted_price
            self.price_history_items = self.price_history_items + 1
            self.last_updated_at = datetime.datetime.now()
            self.average_price = self._calculate_new_average(current_price=price_history_item.discounted_price)

        self.book_with_error = False
        self.error_detail = ""

    def _calculate_new_average(self, current_price: decimal.Decimal) -> decimal.Decimal:
        return self.average_price + ((current_price-self.average_price)/self.price_history_items)