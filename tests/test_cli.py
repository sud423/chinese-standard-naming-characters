import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class CLITests(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run(
            [sys.executable, "-m", "yongjia_naming", *args], cwd=ROOT,
            env={**os.environ, "PYTHONUTF8": "1"}, capture_output=True, text=True, encoding="utf-8",
        )

    def test_lookup_json(self):
        result = self.run_cli("lookup", "一", "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["index"], 1)

    def test_lookup_absent(self):
        result = self.run_cli("lookup", "😀", "--json")
        self.assertEqual(result.returncode, 1)
        self.assertIsNone(json.loads(result.stdout))

    def test_multiple_names_and_json_lines(self):
        result = self.run_cli("check", "李明", "李 A", "--json")
        self.assertEqual(result.returncode, 1, result.stderr)
        reports = [json.loads(line) for line in result.stdout.splitlines()]
        self.assertEqual([row["all_in_table"] for row in reports], [True, False])

    def test_readable_output(self):
        result = self.run_cli("check", "李𣲗")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("全部在表", result.stdout)
        self.assertIn("U+23C97", result.stdout)

    def test_bom_crlf_blank_lines_and_spaces(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "names.txt"
            target.write_bytes("\ufeff李明\r\n\r\n 李\r\n".encode("utf-8"))
            result = self.run_cli("check", "--file", str(target), "--json")
        self.assertEqual(result.returncode, 1, result.stderr)
        reports = [json.loads(line) for line in result.stdout.splitlines()]
        self.assertEqual([row["text"] for row in reports], ["李明", " 李"])

    def test_file_errors_are_distinct_from_absent_characters(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            for filename, content in (("empty.txt", b"\n"), ("invalid.txt", b"\xff")):
                target = Path(temp_dir) / filename
                target.write_bytes(content)
                result = self.run_cli("check", "--file", str(target))
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stdout, "")
            missing = self.run_cli("check", "--file", str(Path(temp_dir) / "missing.txt"))
            self.assertEqual(missing.returncode, 2)

    def test_invalid_argument_combinations(self):
        for args in (("check",), ("check", ""), ("check", "李", "--file", "names.txt"), ("lookup", "李明")):
            with self.subTest(args=args):
                result = self.run_cli(*args)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stdout, "")


if __name__ == "__main__":
    unittest.main()
