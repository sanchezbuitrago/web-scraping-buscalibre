from commons import base_types
from domain.model.buscalibre import Book


class GetBooksCommand(base_types.ValueObject):
    order_by: str | None = None

class CreateBookRequestBody(base_types.ValueObject):
    link: str