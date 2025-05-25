import logging
from typing import TypeVar, cast, Mapping
from pydantic import BaseModel


logger = logging.getLogger(__name__)

T = TypeVar('T', bound=BaseModel)

def get_field_value(item: T, field: str) -> str:
    data = cast(Mapping[str, object], item.model_dump())
    value = data.get(field, "")
    return str(value)

def filter_duplicates(items: list[T], field: str) -> list[T]:
    def get_value_length(item: T) -> int:
        return len(get_field_value(item, field))

    items_sorted = sorted(items, key=get_value_length, reverse=True)
    result: list[T] = []
    for item in items_sorted:
        if not any(get_field_value(item, field) in get_field_value(other, field) for other in result):
            result.append(item)
        else:
            logger.debug(f"Duplicate has been filtered: {item}")
    return result
