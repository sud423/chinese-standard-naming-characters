"""Reproduce bundled data from a pinned, locally supplied official Unihan ZIP."""

import argparse
import csv
import hashlib
from io import StringIO
import json
from pathlib import Path
import re
import zipfile

SOURCE_URL = "https://www.unicode.org/Public/17.0.0/ucd/Unihan.zip"
SOURCE_SHA256 = "f7a48b2b545acfaa77b2d607ae28747404ce02baefee16396c5d2d7a8ef34b5e"
ROOT = Path(__file__).resolve().parents[1]
FIELDS = ("character", "codepoint", "index", "level", "source_ref")


def extract(archive: Path) -> list[dict]:
    content = archive.read_bytes()
    if hashlib.sha256(content).hexdigest() != SOURCE_SHA256:
        raise ValueError("Source SHA-256 mismatch; use the pinned Unicode 17.0.0 archive")
    records = {}
    # Read members in memory; never extract archive paths to the filesystem.
    with zipfile.ZipFile(archive) as source:
        for member in source.infolist():
            if not member.filename.endswith(".txt"):
                continue
            if member.file_size > 100_000_000:
                raise ValueError("Unexpected Unihan member size")
            for line in source.read(member).decode("utf-8").splitlines():
                if not line or line.startswith("#"):
                    continue
                codepoint, field, value = line.split("\t", 2)
                if field != "kTGH":
                    continue
                match = re.fullmatch(r"2013:([1-9][0-9]{0,3})", value)
                if not match:
                    raise ValueError(f"Unexpected kTGH reference: {value}")
                index = int(match.group(1))
                scalar = int(codepoint[2:], 16)
                if index in records or not 1 <= index <= 8105:
                    raise ValueError(f"Duplicate or invalid table index: {index}")
                records[index] = {
                    "character": chr(scalar),
                    "codepoint": f"U+{scalar:04X}",
                    "index": index,
                    "level": 1 if index <= 3500 else 2 if index <= 6500 else 3,
                    "source_ref": value,
                }
    if set(records) != set(range(1, 8106)):
        raise ValueError("Expected the complete contiguous index range 1..8105")
    rows = [records[index] for index in range(1, 8106)]
    if len({row["character"] for row in rows}) != 8105:
        raise ValueError("Duplicate characters in the source mapping")
    return rows


def artifacts(rows: list[dict]) -> dict[Path, bytes]:
    json_bytes = ("[\n" + ",\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n]\n").encode("utf-8")
    csv_text = StringIO(newline="")
    writer = csv.DictWriter(csv_text, fieldnames=FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    csv_bytes = csv_text.getvalue().encode("utf-8")
    manifest = {
        "dataset_version": "0.1.0",
        "table_edition": "2013",
        "unicode_version": "17.0.0",
        "source_property": "kTGH",
        "source_url": SOURCE_URL,
        "source_sha256": SOURCE_SHA256,
        "source_documentation": "https://www.unicode.org/reports/tr38/tr38-39.html#kTGH",
        "license": "Unicode-3.0",
        "count": 8105,
        "levels": {"1": 3500, "2": 3000, "3": 1605},
        "json_sha256": hashlib.sha256(json_bytes).hexdigest(),
        "csv_sha256": hashlib.sha256(csv_bytes).hexdigest(),
        "fields": list(FIELDS),
        "maintainer": "永嘉取名网 · Yongjia Naming",
        "maintainer_url": "https://www.yjmbjy.com/",
    }
    data_dir = ROOT / "yongjia_naming" / "data"
    return {
        data_dir / "characters.json": json_bytes,
        data_dir / "manifest.json": (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8"),
        ROOT / "data" / "characters.csv": csv_bytes,
        ROOT / "data" / "characters.txt": ("\n".join(row["character"] for row in rows) + "\n").encode("utf-8"),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--unihan", type=Path, required=True, help="Pinned Unihan.zip path")
    parser.add_argument("--check", action="store_true", help="Verify committed artifacts without writing")
    args = parser.parse_args()
    for path, expected in artifacts(extract(args.unihan)).items():
        if args.check:
            if not path.exists() or path.read_bytes() != expected:
                raise SystemExit(f"Data differs: {path.relative_to(ROOT)}")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(expected)
        print(f"{'Verified' if args.check else 'Wrote'} {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
