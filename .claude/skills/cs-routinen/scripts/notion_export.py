#!/usr/bin/env python3
"""Brief in Notion-flavored Markdown übersetzen.

Notion kennt keine Pipe-Tabellen, sondern ein eigenes ``<table>``-Format. Dieses
Skript nimmt einen Brief aus ``output/`` und gibt ihn so aus, dass der Text
direkt als ``content`` an ``mcp__Notion__notion-create-pages`` bzw.
``notion-update-page`` gehen kann.

Aufruf:
    python3 scripts/notion_export.py output/2026-08-12-renewals.md
    python3 scripts/notion_export.py output/2026-08-12-renewals.md --strip-h1

``--strip-h1`` entfernt die erste ``# ``-Zeile: Notion zeigt den Seitentitel
schon als Überschrift, eine zweite wäre doppelt.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

#: Notion-Italic ist *Text*, nicht _Text_.
UNDERSCORE_ITALIC = re.compile(r"(?<![\w\\])_([^_\n]+)_(?![\w])")


def is_table_row(line: str) -> bool:
    stripped = line.strip()
    return stripped.startswith("|") and stripped.endswith("|")


def is_separator_row(line: str) -> bool:
    return bool(re.fullmatch(r"\|[\s:|-]+\|", line.strip()))


def split_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def convert_table(rows: list[str]) -> list[str]:
    """Pipe-Tabelle in ein Notion-``<table>`` überführen.

    Die erste Zeile wird als Kopfzeile behandelt, die Trennzeile verworfen.
    Zellen dürfen nur Rich Text enthalten -- das ist bei den Briefs gegeben.
    """
    body = [row for row in rows if not is_separator_row(row)]
    if not body:
        return []
    out = ['<table fit-page-width="true" header-row="true">']
    for index, row in enumerate(body):
        out.append("\t<tr>")
        for cell in split_row(row):
            text = cell if cell else " "
            if index == 0 and not text.startswith("**"):
                text = f"**{text}**"
            out.append(f"\t\t<td>{text}</td>")
        out.append("\t</tr>")
    out.append("</table>")
    return out


def indent_with_tabs(line: str, spaces_per_level: int = 4) -> str:
    """Notion erwartet Tabs zur Einrückung, nicht Leerzeichen."""
    stripped = line.lstrip(" ")
    depth = (len(line) - len(stripped)) // spaces_per_level
    return "\t" * depth + stripped if depth else line


def convert(markdown: str, strip_h1: bool = False) -> str:
    lines = markdown.splitlines()
    if strip_h1:
        while lines and (lines[0].startswith("# ") or not lines[0].strip()):
            lines.pop(0)

    out: list[str] = []
    buffer: list[str] = []
    for line in lines:
        if is_table_row(line):
            buffer.append(line)
            continue
        if buffer:
            out.extend(convert_table(buffer))
            buffer = []
        out.append(indent_with_tabs(UNDERSCORE_ITALIC.sub(r"*\1*", line)))
    if buffer:
        out.extend(convert_table(buffer))
    return "\n".join(out).strip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Brief nach Notion-Markdown")
    parser.add_argument("path", help="Pfad zum Brief in output/")
    parser.add_argument("--strip-h1", action="store_true", help="erste H1-Zeile entfernen")
    parser.add_argument("--out", help="Zieldatei (Standard: stdout)")
    args = parser.parse_args()

    source = Path(args.path)
    converted = convert(source.read_text(encoding="utf-8"), strip_h1=args.strip_h1)
    if args.out:
        Path(args.out).write_text(converted, encoding="utf-8")
        print(f"Geschrieben: {args.out}")
    else:
        print(converted, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
