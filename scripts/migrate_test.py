"""Apply migrations only to the separately named local test database."""

import os
import subprocess

from app.platform.config import Settings
from sqlalchemy.engine import make_url

settings = Settings()
assert settings.migration_database_url
url = make_url(settings.migration_database_url.get_secret_value()).set(database="growthpilot_test")
environment = dict(os.environ, GP_MIGRATION_DATABASE_URL=url.render_as_string(hide_password=False))
subprocess.run([".venv/bin/alembic", "upgrade", "head"], env=environment, check=True)
