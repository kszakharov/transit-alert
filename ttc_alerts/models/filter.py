import logging

logger = logging.getLogger(__name__)

def filter_duplicates(items: list, field: str) -> list:
    items_sorted = sorted(items, key=lambda x: len(x.dict().get(field, "")), reverse=True)
    result = []
    for item in items_sorted:
        if not any(item.dict().get(field, "") in other.dict().get(field, "") for other in result):
            result.append(item)
        else:
            logger.info(f"Duplicate alert: {item}")
    return result
