import csv
import io
from collections.abc import Iterable


def safe_csv(rows: Iterable[list[object]]) -> str:
    output = io.StringIO(newline="")
    writer = csv.writer(output)
    for row in rows:
        values: list[str] = []
        for value in row:
            cell = "" if value is None else str(value)
            if cell.lstrip().startswith(("=", "+", "-", "@")) or cell.startswith(
                ("\t", "\r", "\n")
            ):
                cell = "'" + cell
            values.append(cell)
        writer.writerow(values)
    return output.getvalue()
