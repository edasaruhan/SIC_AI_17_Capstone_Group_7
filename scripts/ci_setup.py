"""Provision only a disposable CI database service; never point this at production."""

import os
import secrets
from pathlib import Path

import psycopg
from psycopg import sql


def main() -> None:
    if os.environ.get("CI") != "true":
        raise SystemExit("Only enabled inside disposable CI")
    env_path = Path(".env")
    if env_path.exists():
        raise SystemExit("Refusing to overwrite existing environment")
    app_password, migration_password = secrets.token_urlsafe(32), secrets.token_urlsafe(32)
    with psycopg.connect(os.environ["GP_CI_BOOTSTRAP_URL"], autocommit=True) as connection:
        for role, password in (
            ("growthpilot_app", app_password),
            ("growthpilot_migrator", migration_password),
        ):
            connection.execute(
                sql.SQL("CREATE ROLE {} LOGIN PASSWORD {} NOSUPERUSER NOBYPASSRLS").format(
                    sql.Identifier(role), sql.Literal(password)
                )
            )
        for database in ("growthpilot", "growthpilot_test"):
            connection.execute(
                sql.SQL("CREATE DATABASE {} OWNER growthpilot_migrator").format(
                    sql.Identifier(database)
                )
            )
            connection.execute(
                sql.SQL("REVOKE ALL ON DATABASE {} FROM PUBLIC").format(sql.Identifier(database))
            )
            connection.execute(
                sql.SQL(
                    "GRANT CONNECT ON DATABASE {} TO growthpilot_app,growthpilot_migrator"
                ).format(sql.Identifier(database))
            )
    with os.fdopen(os.open(env_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600), "w") as output:
        output.write(
            "GP_ENVIRONMENT=test\nGP_AUTH_MODE=development\n"
            f"GP_DATABASE_URL=postgresql+psycopg://growthpilot_app:{app_password}"
            "@127.0.0.1:55432/growthpilot\n"
            f"GP_MIGRATION_DATABASE_URL=postgresql+psycopg://growthpilot_migrator:"
            f"{migration_password}@127.0.0.1:55432/growthpilot\n"
            f"GP_DEV_SIGNING_SECRET={secrets.token_urlsafe(48)}\n"
        )
    print("Disposable CI roles created; credentials not printed.")


if __name__ == "__main__":
    main()
