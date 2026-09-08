import os

from alembic import context
from app.platform.config import get_settings
from sqlalchemy import create_engine

url = os.environ.get("GP_MIGRATION_DATABASE_URL")
if not url:
    configured = get_settings().migration_database_url
    if configured is None:
        raise RuntimeError("Set GP_MIGRATION_DATABASE_URL for the separate migration role")
    url = configured.get_secret_value()

if context.is_offline_mode():
    context.configure(url=url, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()
else:
    with create_engine(url).connect() as connection:
        context.configure(connection=connection, transaction_per_migration=True)
        with context.begin_transaction():
            context.run_migrations()
