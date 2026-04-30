import abc
from typing import Generic, Iterator, Optional, Type, TypeVar, Dict

from commons import base_types

T = TypeVar("T", bound=base_types.Aggregate)
U = TypeVar("U", bound=base_types.EntityId)


class AbstractRepository(abc.ABC, Generic[T]):
    @abc.abstractmethod
    def __init__(self, uow: "AbstractUnitOfWork") -> None:
        raise NotImplementedError()

    @abc.abstractmethod
    def get_model_type(self) -> Type[T]:
        raise NotImplementedError()

    @abc.abstractmethod
    def save(self, new_item: T) -> None:
        raise NotImplementedError()

    @abc.abstractmethod
    def get_all(self, descending: bool, limit: int, sort_by: str) -> Iterator[T]:
        raise NotImplementedError()

    @abc.abstractmethod
    def find_by_id(self, entity_id: U, entity_type: Type[T]) -> Optional[T]:
        raise NotImplementedError()

    @abc.abstractmethod
    def query(self) -> Iterator[T]:
        raise NotImplementedError()

    @abc.abstractmethod
    def find_by(self, find: Dict[str, str], sort_by: str, descending: bool, **kwargs: str) -> Iterator[T]:
        raise NotImplementedError()


class AbstractUnitOfWork(abc.ABC):
    @abc.abstractmethod
    def get_repo(self, entity_type: Type[T]) -> AbstractRepository[T]:
        raise NotImplementedError()
