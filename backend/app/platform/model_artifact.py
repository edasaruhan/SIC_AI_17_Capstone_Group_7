"""Verify and install a trusted model artifact without deserializing it."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_and_install(model: Path, manifest: Path, destination: Path) -> str:
    expected = json.loads(manifest.read_text(encoding="utf-8"))["artifact_sha256"]
    actual = sha256(model)
    if actual != expected:
        raise RuntimeError("Frozen model artifact checksum mismatch")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(model, destination)
    destination.chmod(0o444)
    if sha256(destination) != expected:
        raise RuntimeError("Installed model artifact checksum mismatch")
    return actual


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--destination", type=Path, required=True)
    args = parser.parse_args()
    print(verify_and_install(args.model, args.manifest, args.destination))


if __name__ == "__main__":
    main()
