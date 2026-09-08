"""Create isolated local PostgreSQL infrastructure; never modify another cluster."""

import os
import secrets
import shutil
import subprocess
from pathlib import Path

import psycopg
from psycopg import sql

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / ".local"
CLUSTER = STATE / "postgres"
SOCKET = STATE / "pgsocket"


def run(*args: str) -> None:
    subprocess.run(args, check=True, cwd=ROOT)


def main() -> None:
    if not shutil.which("pg_ctl"):
        raise SystemExit("PostgreSQL 17 tools are required (or use infra/compose.yaml).")
    STATE.mkdir(mode=0o700, exist_ok=True)
    SOCKET.mkdir(mode=0o700, exist_ok=True)
    env_path = ROOT / ".env"
    if env_path.exists():
        print("Existing .env preserved.")
    else:
        app_password = secrets.token_urlsafe(32)
        owner_password = secrets.token_urlsafe(32)
        content = (
            "GP_ENVIRONMENT=development\nGP_AUTH_MODE=development\n"
            f"GP_DATABASE_URL=postgresql+psycopg://growthpilot_app:{app_password}"
            "@127.0.0.1:55432/growthpilot\n"
            f"GP_MIGRATION_DATABASE_URL=postgresql+psycopg://growthpilot_migrator:{owner_password}"
            "@127.0.0.1:55432/growthpilot\n"
            f"GP_DEV_SIGNING_SECRET={secrets.token_urlsafe(48)}\n"
            'GP_ALLOWED_ORIGINS=["http://localhost:3000"]\n'
        )
        descriptor = os.open(env_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        with os.fdopen(descriptor, "w") as output:
            output.write(content)
    if not CLUSTER.exists():
        run(
            "initdb",
            "-D",
            str(CLUSTER),
            "-U",
            "growthpilot_bootstrap",
            "--auth-local=trust",
            "--auth-host=scram-sha-256",
            "--encoding=UTF8",
            "--no-locale",
        )
    status = subprocess.run(["pg_ctl", "-D", str(CLUSTER), "status"], capture_output=True)
    if status.returncode != 0:
        run(
            "pg_ctl",
            "-D",
            str(CLUSTER),
            "-l",
            str(STATE / "postgres.log"),
            "-o",
            f"-p 55432 -h 127.0.0.1 -k {SOCKET}",
            "-w",
            "start",
        )
    from app.platform.config import Settings
    from sqlalchemy.engine import make_url

    settings = Settings()
    assert settings.migration_database_url
    urls = [
        make_url(settings.database_url.get_secret_value()),
        make_url(settings.migration_database_url.get_secret_value()),
    ]
    with psycopg.connect(
        host=str(SOCKET),
        port=55432,
        dbname="postgres",
        user="growthpilot_bootstrap",
        autocommit=True,
    ) as connection:
        for url in urls:
            exists = connection.execute(
                "SELECT 1 FROM pg_roles WHERE rolname=%s", (url.username,)
            ).fetchone()
            if not exists:
                connection.execute(
                    sql.SQL("CREATE ROLE {} LOGIN PASSWORD {} NOSUPERUSER NOBYPASSRLS").format(
                        sql.Identifier(url.username), sql.Literal(url.password)
                    )
                )
        for database in ("growthpilot", "growthpilot_test"):
            if not connection.execute(
                "SELECT 1 FROM pg_database WHERE datname=%s", (database,)
            ).fetchone():
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
                    "GRANT CONNECT ON DATABASE {} TO growthpilot_app, growthpilot_migrator"
                ).format(sql.Identifier(database))
            )
    print("GrowthPilot local cluster ready on 127.0.0.1:55432. Secrets remain in ignored .env.")


if __name__ == "__main__":
    main()
