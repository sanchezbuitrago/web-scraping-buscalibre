from typing import Dict, Iterator, Optional, Type, Any

from commons import logs, unit_of_work

_LOGGER = logs.get_logger()


class InMemoryUOW(unit_of_work.AbstractUnitOfWork):
    def __init__(self) -> None:
        self._db: Dict[str, Dict[str, Dict]] = {}

    def get_repo(
        self, entity_type: Type[unit_of_work.T]
    ) -> unit_of_work.AbstractRepository[unit_of_work.T]:
        return InMemoryRepository(entity_type=entity_type, db_session=self._db)


class InMemoryRepository(unit_of_work.AbstractRepository):
    def __init__(
        self,
        entity_type: Type[unit_of_work.T],
        db_session: Dict[str, Dict[str, Dict]],
    ) -> None:
        self._entity_type: Type[unit_of_work.T] = entity_type
        self.db_session = db_session

    def get_model_type(self) -> Type[unit_of_work.T]:
        return self._entity_type

    def query(self) -> Iterator[unit_of_work.T]:
        raise NotImplementedError()

    def save(self, new_item: unit_of_work.T) -> None:
        if self.db_session.get(self._entity_type.__name__):
            self.db_session[self._entity_type.__name__].update(
                {new_item.id.key(): new_item.dict()}
            )
        else:
            self.db_session.update(
                {self._entity_type.__name__: {new_item.id.key(): new_item.dict()}}
            )

    def find_by_id(
        self, entity_id: unit_of_work.U, entity_type: Type[unit_of_work.T]
    ) -> Optional[unit_of_work.T]:
        _LOGGER.info("GETTING BY ID")
        fields = self.db_session.get(self._entity_type.__name__, {})
        item = fields.get(entity_id.key(), None)
        return self._entity_type.parse_obj(item) if item else None  # type: ignore

    def get_all(self, descending: bool = True, limit: int = 20, find: Dict[str, Any] = {}, sort_by: str = "created_at") -> Iterator[
        unit_of_work.T]:
        _LOGGER.info("GETTING ALL DATA")
        for key_item, value_item in self.db_session.get(
            self._entity_type.__name__, {}
        ).items():
            yield self._entity_type.parse_obj(value_item)

    def find_by(self, sort_by: str, **kwargs: str) -> Iterator[unit_of_work.T]:
        _LOGGER.info(f"Getting data filtering by {kwargs}")
        for key_item, value_item in self.db_session.get(
            self._entity_type.__name__, {}
        ).items():
            item_mach = all(
                value_item.get(item_property) == kwargs[item_property]
                for item_property in list(kwargs.keys())
            )
            if item_mach:
                yield self._entity_type.parse_obj(value_item)
