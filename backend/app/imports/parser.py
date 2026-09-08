"""Bounded untrusted-file inspection. Never execute formulas or extract ZIP members."""

import csv
import io
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import PurePosixPath
from xml.etree.ElementTree import ParseError
from zipfile import BadZipFile, ZipFile

import openpyxl
from defusedxml import ElementTree
from defusedxml.common import DefusedXmlException
from openpyxl.utils.exceptions import InvalidFileException

from app.platform.errors import DomainError

MAX_ROWS = 1000
MAX_COLUMNS = 64
MAX_CELL = 5000
MAX_INFLATED = 32 * 1024 * 1024


@dataclass
class InspectedTable:
    headers: list[str]
    rows: list[dict[str, str]]


def _table(rows: Iterable[list[str]]) -> InspectedTable:
    iterator = iter(rows)
    headers = [value.strip() for value in next(iterator, [])]
    if (
        not headers
        or len(headers) > MAX_COLUMNS
        or any(not value for value in headers)
        or len(set(headers)) != len(headers)
        or any(len(value) > 100 for value in headers)
    ):
        raise DomainError("Provide unique nonempty headers (maximum 64 columns, 100 characters)")
    parsed: list[dict[str, str]] = []
    for row in iterator:
        if len(parsed) >= MAX_ROWS:
            raise DomainError("Import exceeds 1000 data rows", 413)
        if len(row) != len(headers):
            raise DomainError(f"Row {len(parsed) + 2} does not match the header width")
        if any(len(cell) > MAX_CELL or "\x00" in cell for cell in row):
            raise DomainError("Cell contains unsupported content or exceeds 5000 characters")
        # Plus/minus numeric values (including international phone numbers) remain data.
        # Any spreadsheet export escapes all formula-prefix characters independently.
        if any(cell.lstrip().startswith(("=", "@")) for cell in row):
            raise DomainError("Formula-like cell content is not accepted")
        parsed.append(dict(zip(headers, row, strict=True)))
    if not parsed:
        raise DomainError("Import must contain at least one data row")
    return InspectedTable(headers, parsed)


def _xlsx(content: bytes) -> InspectedTable:
    with ZipFile(io.BytesIO(content)) as archive:
        members = archive.infolist()
        names = [item.filename for item in members]
        if len(names) != len(set(names)) or len(members) > 100:
            raise DomainError("Spreadsheet archive has too many or duplicate members")
        if not {"[Content_Types].xml", "xl/workbook.xml"}.issubset(names):
            raise DomainError("File is not an XLSX workbook")
        if sum(member.file_size for member in members) > MAX_INFLATED:
            raise DomainError("Expanded spreadsheet exceeds 32 MiB", 413)
        for member in members:
            path = PurePosixPath(member.filename)
            lowered = member.filename.casefold()
            if (
                path.is_absolute()
                or ".." in path.parts
                or "\\" in member.filename
                or member.flag_bits & 1
                or any(
                    part in lowered
                    for part in ("vbaproject", "externallinks", "embeddings", "activex")
                )
                or member.file_size > max(member.compress_size, 1) * 300
            ):
                raise DomainError("Unsupported or unsafe spreadsheet archive member")
            if lowered.endswith((".xml", ".rels")):
                root = ElementTree.fromstring(archive.read(member), forbid_dtd=True)
                for element in root.iter():
                    if element.attrib.get("TargetMode") == "External":
                        raise DomainError("External spreadsheet relationships are not accepted")
        workbook = openpyxl.load_workbook(
            io.BytesIO(content), read_only=True, data_only=False, keep_links=False
        )
        try:
            if len(workbook.worksheets) != 1:
                raise DomainError("Upload exactly one worksheet")
            sheet = workbook.worksheets[0]
            if (sheet.max_row or 0) > MAX_ROWS + 1 or (sheet.max_column or 0) > MAX_COLUMNS:
                raise DomainError("Spreadsheet dimensions exceed import limits", 413)

            def values() -> Iterable[list[str]]:
                for row in sheet.iter_rows():
                    cells: list[str] = []
                    for cell in row:
                        if cell.data_type == "f":
                            raise DomainError("Spreadsheet formulas are not accepted")
                        value = cell.value
                        cells.append(
                            value.isoformat()
                            if isinstance(value, date | datetime)
                            else ""
                            if value is None
                            else str(value)
                        )
                    yield cells

            return _table(values())
        finally:
            workbook.close()


def inspect_file(filename: str, content: bytes, max_bytes: int) -> InspectedTable:
    if not content or len(content) > max_bytes:
        raise DomainError("File is empty or exceeds upload size limit", 413)
    if (
        len(filename) > 200
        or "/" in filename
        or "\\" in filename
        or "\x00" in filename
        or filename.startswith(".")
    ):
        raise DomainError("Unsafe filename")
    extension = PurePosixPath(filename).suffix.lower()
    try:
        if extension == ".xlsx" and content.startswith(b"PK\x03\x04"):
            return _xlsx(content)
        if extension == ".csv" and not content.startswith((b"PK", b"%PDF", b"\xd0\xcf")):
            decoded = content.decode("utf-8-sig")
            return _table(
                list(row) for row in csv.reader(io.StringIO(decoded, newline=""), strict=True)
            )
    except (
        UnicodeError,
        csv.Error,
        BadZipFile,
        DefusedXmlException,
        ParseError,
        InvalidFileException,
        ValueError,
        KeyError,
    ) as exc:
        raise DomainError("Malformed or unsafe CSV/XLSX file") from exc
    raise DomainError("Only UTF-8 CSV or genuine XLSX content is accepted")
