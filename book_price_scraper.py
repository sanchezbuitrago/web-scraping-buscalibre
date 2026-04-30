import time
import schedule

from domain.services import buscalibre as  buscalibre_services
from domain.services import scraper
from commons import unit_of_work
from commons.adapters import mongo_uow

_DEFAULT_TIME_TO_RUN_SCRIPT_IN_SECONDS = 10
_DEFAULT_TIME_TO_SLEEP_IN_SECONDS = 5

_SCRAPER = scraper.BuscaLibreScraper()
_UOW = unit_of_work.AbstractUnitOfWork = mongo_uow.MongoUOW()

print("Running ...")
schedule.every(_DEFAULT_TIME_TO_RUN_SCRIPT_IN_SECONDS).seconds.do(
    buscalibre_services.buscalibre_price_tracker,
    uow=_UOW,
    scraper=_SCRAPER,
)

while True:
    print("______________________________________________________")
    schedule.run_pending()
    time.sleep(_DEFAULT_TIME_TO_SLEEP_IN_SECONDS)