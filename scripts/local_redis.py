"""Start a password-protected project-local Redis without a system service."""

import os
import secrets
import shutil
import subprocess
import time
from pathlib import Path

from app.platform.config import Settings
from redis import Redis
from redis.exceptions import AuthenticationError
from redis.exceptions import ConnectionError as RedisConnectionError

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    if not shutil.which("redis-server"):
        raise SystemExit("Install Redis; this script never configures a system service")
    env_path = ROOT / ".env"
    if not env_path.exists():
        raise SystemExit("Run local_setup.py first")
    if "GP_REDIS_URL=" not in env_path.read_text():
        with env_path.open("a") as output:
            output.write(f"GP_REDIS_URL=redis://:{secrets.token_urlsafe(32)}@127.0.0.1:56379/0\n")
    settings = Settings()
    if settings.environment == "production":
        raise SystemExit("Local setup is disabled in production")
    client = Redis.from_url(settings.redis_url.get_secret_value(), socket_connect_timeout=2)
    options = client.connection_pool.connection_kwargs
    if (
        options.get("host") != "127.0.0.1"
        or options.get("port") != 56379
        or not options.get("password")
    ):
        raise SystemExit("Expected password-protected project loopback Redis on 56379")
    directory = ROOT / ".local" / "redis"
    directory.mkdir(mode=0o700, parents=True, exist_ok=True)
    configuration = directory / "redis.conf"
    try:
        if client.ping():
            print("Existing authenticated project Redis preserved on 56379")
            return
    except AuthenticationError:
        raise SystemExit("Existing Redis rejects project credentials; nothing changed") from None
    except RedisConnectionError:
        print("Project Redis is not listening yet; starting its isolated instance")
    if not configuration.exists():
        with os.fdopen(
            os.open(configuration, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600), "w"
        ) as output:
            output.write(
                "bind 127.0.0.1\nport 56379\nprotected-mode yes\n"
                f"requirepass {options['password']}\n"
                f'dir "{directory}"\nappendonly yes\nsave ""\ndaemonize yes\n'
                f'pidfile "{directory / "redis.pid"}"\nlogfile "{directory / "redis.log"}"\n'
                "maxmemory 256mb\nmaxmemory-policy noeviction\n"
            )
    subprocess.run(["redis-server", str(configuration)], check=True)
    for _ in range(50):
        try:
            if client.ping():
                print("Authenticated local Redis ready on 56379; no system service enabled")
                return
        except RedisConnectionError:
            time.sleep(0.1)
    raise SystemExit("Redis did not become ready; inspect the private project log")


if __name__ == "__main__":
    main()
