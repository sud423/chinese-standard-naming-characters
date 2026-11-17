"""Command line interface. Exit codes: 0 in-table, 1 absent, 2 input/error."""

import argparse
from dataclasses import asdict
import json
from pathlib import Path
import sys

from . import __version__, check_name, lookup


def _print_check(result, as_json: bool) -> None:
    if as_json:
        print(json.dumps(result.to_dict(), ensure_ascii=False))
        return
    print(f"{result.text}: {'全部在表' if result.all_in_table else '含表外字符'}")
    for item in result.characters:
        detail = (
            f"第{item.record.level}级 / 序号{item.record.index}"
            if item.record else "未在2013版字表中匹配"
        )
        print(f"  {item.position}. {item.character!r} {item.codepoint} {detail}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="永嘉取名网 · 2013版通用规范汉字表校验")
    parser.add_argument("--version", action="version", version=__version__)
    commands = parser.add_subparsers(dest="command", required=True)
    lookup_parser = commands.add_parser("lookup", help="查询一个汉字")
    lookup_parser.add_argument("character")
    lookup_parser.add_argument("--json", action="store_true", help="输出JSON")
    check_parser = commands.add_parser("check", help="逐字校验姓名或文本")
    check_parser.add_argument("names", nargs="*")
    check_parser.add_argument("--file", type=Path, help="UTF-8文本，每行一个姓名；跳过空行")
    check_parser.add_argument("--json", action="store_true", help="每个输入输出一行JSON")
    args = parser.parse_args(argv)
    try:
        if args.command == "lookup":
            record = lookup(args.character)
            if args.json:
                print(json.dumps(asdict(record) if record else None, ensure_ascii=False))
            else:
                _print_check(check_name(args.character), False)
            return 0 if record else 1
        if bool(args.names) == bool(args.file):
            parser.error("check需要姓名参数或--file，且只能使用其中一种")
        if args.file:
            # Keep leading/trailing spaces: they are part of the submitted text.
            names = [line for line in args.file.read_text(encoding="utf-8-sig").splitlines() if line]
            if not names:
                parser.error("输入文件没有非空行")
        else:
            names = args.names
        results = [check_name(name) for name in names]
        for result in results:
            _print_check(result, args.json)
        return 0 if all(result.all_in_table for result in results) else 1
    except (OSError, UnicodeError, TypeError, ValueError, RuntimeError) as error:
        print(f"错误: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
