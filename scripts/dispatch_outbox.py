"""Run from a trusted scheduler for an explicitly configured organization."""

import argparse
import time
from uuid import UUID

from app.platform.jobs import dispatch
from app.platform.worker import enqueue


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tenant", type=UUID, required=True)
    parser.add_argument("--watch", action="store_true")
    args = parser.parse_args()
    while True:
        print(f"Dispatched {dispatch(args.tenant, enqueue)} events")
        if not args.watch:
            break
        time.sleep(5)


if __name__ == "__main__":
    main()
