from commons import base_types
from domain.model.buscalibre import Book


class GetBooksResponse(base_types.ValueObject):
    count: int
    books: list[Book]


class CreateBookRequestBody(base_types.ValueObject):
    link: str