from datetime import timedelta

from domain.model import buscalibre, commands
from domain.services import provider, scraper as scraper_service
from commons import unit_of_work

_DEFAULT_RETENTION_TIME_LINKS = timedelta(minutes=30)


books_provider = provider.BookProvider(retention_time=_DEFAULT_RETENTION_TIME_LINKS)

def create_book(uow: unit_of_work.AbstractUnitOfWork, scraper: scraper_service.BuscaLibreScraper, cmd: commands.CreateBookRequestBody) -> commands.Book:
    _BOOKS_REPOSITORY = uow.get_repo(entity_type=buscalibre.Book)
    book = next(_BOOKS_REPOSITORY.find_by(find={"link": cmd.link}, sort_by="created_at", descending=True), None)
    if book is None:
        book = scraper.scrape_book(url=cmd.link)
        _BOOKS_REPOSITORY.save(new_item=book)
        return book

    raise buscalibre.BookAlreadyExistsError()


def buscalibre_price_tracker(
        uow: unit_of_work.AbstractUnitOfWork,
        scraper: scraper_service.BuscaLibreScraper
) -> None:
    print("Running buscalibre price tracker")
    _BOOK_HISTORY_REPOSITORY = uow.get_repo(entity_type=buscalibre.BookPriceHistory)
    _BOOKS_REPOSITORY = uow.get_repo(entity_type=buscalibre.Book)

    books = list(_BOOKS_REPOSITORY.get_all(descending=True, limit=100, sort_by="created_at"))
    print("Books number: ", len(books))
    pending_book = next(books_provider.get_next_book(books=books))
    if pending_book is not None:
        print("Running scraper for book: ", pending_book.id, pending_book.title)
        try:
            book_info = scraper.scrape_book_price_history(url=pending_book.link, book_id=pending_book.id.value)
        except Exception as e:
            print(f"Error obteniedo datos de buscalibre: Book ID : [{pending_book.id.value}], Titulo: [{pending_book.title}], Link:[{pending_book.link}]")
            print(e)
            pending_book.save_book_error(error="Error running scraper")
            _BOOKS_REPOSITORY.save(new_item=pending_book)
            return

        if book_last_price := next(_BOOK_HISTORY_REPOSITORY.find_by(find={"book_id": pending_book.id.value}, sort_by="requested_at", descending=True), None):
            if book_last_price.price != book_info.price or book_last_price.discounted_price != book_info.discounted_price or book_last_price.discount != book_info.discount:
                pending_book.calculate_price_by_price_history(price_history_item=book_last_price)
                print("Saving price for book: ", pending_book.id)
                _BOOKS_REPOSITORY.save(new_item=pending_book)
                _BOOK_HISTORY_REPOSITORY.save(new_item=book_info)
            else:
                print("Price information already exist")
        else:
            pending_book.calculate_price_by_price_history(price_history_item=book_info)
            print("Saving price for book: ", pending_book.id)
            _BOOKS_REPOSITORY.save(new_item=pending_book)
            _BOOK_HISTORY_REPOSITORY.save(new_item=book_info)

        # for book in books:
        #     books_history = _BOOK_HISTORY_REPOSITORY.find_by(find={"book_id": book.id.value},
        #                                                      sort_by="requested_at", descending=True)
        #     if item := next(books_history, None):
        #         print(f"Se consulto nueva informacion sobre el libro: {book.id.value}")
        #         print(item.model_dump())

def get_books(uow: unit_of_work.AbstractUnitOfWork) -> commands.GetBooksResponse:
    _BOOKS_REPOSITORY = uow.get_repo(entity_type=buscalibre.Book)
    books = list(_BOOKS_REPOSITORY.get_all(descending=True, limit=100, sort_by="last_updated_date"))

    return commands.GetBooksResponse(books=books, count=len(books))
