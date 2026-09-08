from sqlalchemy import text
from sqlalchemy.orm import Session


def serialize_key(session: Session, namespace: str, key: str) -> None:
    session.execute(
        text("SELECT pg_advisory_xact_lock(hashtextextended(:key, 0))"),
        {"key": f"{namespace}:{key}"},
    )
