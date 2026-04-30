import datetime
import enum
import numbers
import random
import string
import uuid
from typing import Any, Dict, Iterator

import pydantic


class Key(pydantic.BaseModel):
    class _MalformedIDError(Exception):
        def __init__(self) -> None:
            super().__init__(
                """Keys DO NOT support complex types, only primitives. """
                """None values are NOT allowed"""
            )

    def dict(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        atts_dict = super().dict(**kwargs)
        atts_dict["_key"] = self.key()
        return atts_dict

    def key(self, **kwargs: Any) -> str:
        atts_dict = super().dict(**kwargs)

        def key_values(atts_dict: Dict[str, Any]) -> Iterator[str]:
            for v in atts_dict.values():
                if not v or not isinstance(v, (str, numbers.Number, enum.Enum)):
                    raise Key._MalformedIDError()
                yield str(v.value if isinstance(v, enum.Enum) else v)

        return "_".join((key_values(atts_dict=atts_dict)))


class IDGenerator:
    @staticmethod
    def human_friendly(size: int = 10) -> str:
        return "".join(
            random.SystemRandom().choices(
                string.ascii_uppercase + string.digits, k=size
            )
        )

    @staticmethod
    def uuid() -> str:
        return str(uuid.uuid4())


class EntityId(Key):
    ...


class HumanFriendlyId(EntityId):
    value: str = pydantic.Field(default_factory=IDGenerator.human_friendly)

    def __str__(self) -> str:
        return self.value


class ValueObject(pydantic.BaseModel):
    class Config:
        frozen = True


class Command(ValueObject):
    ...


class RootEntity(pydantic.BaseModel):
    id: EntityId


class Entity(RootEntity):
    ...


class Aggregate(RootEntity):
    ...


class Time(ValueObject):
    posix_time: int

    @staticmethod
    def now() -> "Time":
        return Time(posix_time=datetime.datetime.now().timestamp())

    @staticmethod
    def from_date(date: datetime.date) -> "Time":
        return Time(
            posix_time=datetime.datetime.combine(
                date, datetime.datetime.min.time()
            ).timestamp()
        )

    @staticmethod
    def from_date_with_time(date_with_time: datetime.datetime) -> "Time":
        return Time(posix_time=date_with_time.timestamp())

    def get_datetime(self) -> datetime.datetime:
        return datetime.datetime.fromtimestamp(self.posix_time)
