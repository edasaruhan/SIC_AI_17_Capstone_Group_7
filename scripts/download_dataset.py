"""Reproduce the selected UCI source without silently accepting changed bytes."""

import hashlib
import urllib.request
from pathlib import Path
from zipfile import BadZipFile, ZipFile

URL = "https://archive.ics.uci.edu/static/public/502/online+retail+ii.zip"
SHA256 = "572e36277c2390fbfde10664750731e0a86f55e33470d91919085f0408e67bfb"
TARGET = Path("data/raw/uci_online_retail_ii/source.zip")


def digest(path: Path) -> str:
    checksum = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            checksum.update(chunk)
    return checksum.hexdigest()


def main() -> None:
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    if not TARGET.exists():
        temporary = TARGET.with_suffix(".download")
        try:
            with (
                urllib.request.urlopen(URL, timeout=60) as response,
                temporary.open("xb") as output,
            ):
                while chunk := response.read(1024 * 1024):
                    output.write(chunk)
            if digest(temporary) != SHA256:
                raise SystemExit("Downloaded dataset checksum differs from the reviewed source")
            temporary.replace(TARGET)
        finally:
            if temporary.exists():
                temporary.unlink()
    if digest(TARGET) != SHA256:
        raise SystemExit("Existing raw dataset checksum differs; file preserved for investigation")
    try:
        with ZipFile(TARGET) as archive:
            if archive.namelist() != ["online_retail_II.xlsx"] or archive.testzip() is not None:
                raise SystemExit("Dataset archive structure/integrity is unexpected")
    except BadZipFile as exc:
        raise SystemExit("Dataset archive is malformed") from exc
    print(f"Verified UCI Online Retail II: {SHA256}")


if __name__ == "__main__":
    main()
