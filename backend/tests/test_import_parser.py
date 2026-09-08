import io
from zipfile import ZIP_DEFLATED, ZipFile

import openpyxl
import pytest
from app.imports.parser import inspect_file
from app.platform.errors import DomainError


@pytest.mark.parametrize(
    "name,content",
    [
        ("x.csv", b"name,name\na,b"),
        ("../x.csv", b"name\na"),
        ("x.csv", b"name\n=HYPERLINK(1)"),
        ("x.csv", b"name\n@SUM(1)"),
        ("x.csv", b"name\n\xff"),
        ("x.csv", b"a,b\n1"),
        ("x.csv", b"a\n\x00"),
        ("x.exe", b"name\na"),
        ("x.xlsx", b"PK\x03\x04broken"),
        ("x.csv", b"%PDF-1.0"),
        ("x.csv", b"a\n" + b"a\n" * 1001),
        ("x.csv", b"a\n" + b"b" * 5001),
    ],
)
def test_rejects_untrusted_content(name: str, content: bytes) -> None:
    with pytest.raises(DomainError):
        inspect_file(name, content, 100000)


def test_size_and_bom() -> None:
    with pytest.raises(DomainError):
        inspect_file("x.csv", b"a\n123", 4)
    result = inspect_file("x.csv", b"\xef\xbb\xbfname,phone\nExample,+905550001122", 100)
    assert result.rows == [{"name": "Example", "phone": "+905550001122"}]


def test_xlsx_values_and_formula_rejection() -> None:
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    assert sheet
    sheet.append(["name", "price"])
    sheet.append(["Synthetic", 12.5])
    buffer = io.BytesIO()
    workbook.save(buffer)
    assert inspect_file("x.xlsx", buffer.getvalue(), 100000).rows[0]["price"] == "12.5"
    sheet["A2"] = "=1+1"
    buffer = io.BytesIO()
    workbook.save(buffer)
    with pytest.raises(DomainError, match="formulas"):
        inspect_file("x.xlsx", buffer.getvalue(), 100000)


@pytest.mark.parametrize(
    "member,content",
    [
        ("../escape.xml", b"<x/>"),
        ("xl/vbaProject.bin", b"unsafe"),
        ("xl/unsafe.xml", b'<!DOCTYPE x [<!ENTITY a "boom">]><x>&a;</x>'),
        (
            "xl/unsafe.rels",
            b'<Relationships><Relationship TargetMode="External" /></Relationships>',
        ),
        ("xl/unsafe.xml", b"x" * 1000000),
        ("xl/unsafe.xml", b"<broken"),
    ],
)
def test_zip_xml_defenses(member: str, content: bytes) -> None:
    buffer = io.BytesIO()
    with ZipFile(buffer, "w", ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", "<Types/>")
        archive.writestr("xl/workbook.xml", "<workbook/>")
        archive.writestr(member, content)
    with pytest.raises(DomainError):
        inspect_file("x.xlsx", buffer.getvalue(), 100000)
