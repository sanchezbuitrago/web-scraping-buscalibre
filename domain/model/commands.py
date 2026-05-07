from commons import base_types


class GetBooksCommand(base_types.ValueObject):
    order_by: str | None = None
    descending: bool | None = True

class CreateBookRequestBody(base_types.ValueObject):
    link: str