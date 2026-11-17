import csv
from dataclasses import FrozenInstanceError
import hashlib
import json
from pathlib import Path
import unicodedata
import unittest

from yongjia_naming import characters, check_name, lookup

ROOT = Path(__file__).resolve().parents[1]


class DatasetTests(unittest.TestCase):
    def test_complete_table_and_level_boundaries(self):
        rows = characters()
        self.assertEqual(len(rows), 8105)
        self.assertEqual(len({row.character for row in rows}), 8105)
        self.assertEqual([row.index for row in rows], list(range(1, 8106)))
        self.assertEqual([len(characters(level)) for level in (1, 2, 3)], [3500, 3000, 1605])
        self.assertEqual([rows[i - 1].level for i in (1, 3500, 3501, 6500, 6501, 8105)], [1, 1, 2, 2, 3, 3])

    def test_scalar_and_source_fields_for_every_entry(self):
        for row in characters():
            self.assertEqual(len(row.character), 1)
            self.assertEqual(row.codepoint, f"U+{ord(row.character):04X}")
            self.assertEqual(row.source_ref, f"2013:{row.index}")
            self.assertEqual(lookup(row.character), row)

    def test_exports_agree_and_checksums_match(self):
        data_dir = ROOT / "yongjia_naming" / "data"
        manifest = json.loads((data_dir / "manifest.json").read_text(encoding="utf-8"))
        rows = json.loads((data_dir / "characters.json").read_text(encoding="utf-8"))
        with (ROOT / "data" / "characters.csv").open(encoding="utf-8", newline="") as stream:
            csv_rows = list(csv.DictReader(stream))
        self.assertEqual(len(csv_rows), 8105)
        for row, exported in zip(rows, csv_rows):
            self.assertEqual({key: str(value) for key, value in row.items()}, exported)
        self.assertEqual((ROOT / "data" / "characters.txt").read_text(encoding="utf-8").splitlines(), [row["character"] for row in rows])
        for key, path in (("json_sha256", data_dir / "characters.json"), ("csv_sha256", ROOT / "data" / "characters.csv")):
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), manifest[key])
        self.assertIn("UNICODE LICENSE V3", (data_dir / "LICENSE-UNICODE.txt").read_text(encoding="utf-8"))

    def test_records_are_immutable(self):
        with self.assertRaises(FrozenInstanceError):
            lookup("一").level = 3


class LookupTests(unittest.TestCase):
    def test_known_table_reference(self):
        record = lookup("一")
        self.assertEqual((record.index, record.codepoint, record.level), (1, "U+4E00", 1))

    def test_supplementary_plane_reference(self):
        record = lookup("𣲗")
        self.assertEqual((record.codepoint, record.index, record.level), ("U+23C97", 6613, 3))
        result = check_name("李𣲗")
        self.assertEqual(len(result.characters), 2)
        self.assertTrue(result.all_in_table)

    def test_absence_is_explicit(self):
        for value in ("A", "😀", " ", "·", "\u200b"):
            with self.subTest(value=value):
                self.assertIsNone(lookup(value))
                self.assertFalse(check_name(value).all_in_table)

    def test_no_silent_normalization(self):
        compatibility = "\uf9e1"
        self.assertEqual(unicodedata.normalize("NFKC", compatibility), "李")
        self.assertIsNone(lookup(compatibility))
        result = check_name("李 \ufe00")
        self.assertEqual([item.character for item in result.characters], ["李", " ", "\ufe00"])
        self.assertFalse(result.all_in_table)

    def test_empty_input_and_surrogates_are_errors(self):
        for value in ("", "\ud800", "李\udfff"):
            with self.subTest(value=repr(value)):
                with self.assertRaises(ValueError):
                    check_name(value)
        with self.assertRaises(ValueError):
            lookup("李明")
        with self.assertRaises(TypeError):
            check_name(None)

    def test_level_filter_rejects_ambiguous_types(self):
        for value in (0, 4, "1", True, 1.0):
            with self.assertRaises(ValueError):
                characters(value)

    def test_report_preserves_positions_and_null_record(self):
        report = check_name("李 A").to_dict()
        self.assertEqual(report["text"], "李 A")
        self.assertEqual(report["table_edition"], "2013")
        self.assertFalse(report["all_in_table"])
        self.assertEqual([item["position"] for item in report["characters"]], [1, 2, 3])
        self.assertIsNone(report["characters"][1]["record"])
        self.assertFalse(report["characters"][2]["in_table"])


if __name__ == "__main__":
    unittest.main()
