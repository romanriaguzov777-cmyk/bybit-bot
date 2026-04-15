from uuid import uuid4


def order_link_id(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex[:20]}"
