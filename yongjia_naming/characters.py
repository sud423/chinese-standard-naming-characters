"""Exact Unicode scalar lookup; no transliteration or silent normalization."""

from dataclasses import asdict, dataclass
from functools import lru_cache
import hashlib
from importlib.resources import files
import json


@dataclass(frozen=True)
class Character:
    character: str
    codepoint: str
    index: int
    level: int
    source_ref: str


@dataclass(frozen=True)
class CharacterCheck:
    position: int
    character: str
    codepoint: str
    record: Character | None

    @property
    def in_table(self) -> bool:
        return self.record is not None


@dataclass(frozen=True)
class NameCheck:
    text: str
    characters: tuple[CharacterCheck, ...]

    @property
    def all_in_table(self) -> bool:
        return all(item.in_table for item in self.characters)

    def to_dict(self) -> dict:
        return {
            "text": self.text,
            "table_edition": "2013",
            "unicode_version": "17.0.0",
            "all_in_table": self.all_in_table,
            "characters": [
                {
                    "position": item.position,
                    "character": item.character,
                    "codepoint": item.codepoint,
                    "in_table": item.in_table,
                    "record": asdict(item.record) if item.record else None,
                }
                for item in self.characters
            ],
        }


@lru_cache(maxsize=1)
def _table() -> dict[str, Character]:
    resource = files("yongjia_naming").joinpath("data")
    content = resource.joinpath("characters.json").read_bytes()
    manifest = json.loads(resource.joinpath("manifest.json").read_text(encoding="utf-8"))
    if hashlib.sha256(content).hexdigest() != manifest["json_sha256"]:
        raise RuntimeError("Bundled character data failed its SHA-256 integrity check")
    records = [Character(**row) for row in json.loads(content)]
    table = {record.character: record for record in records}
    if len(records) != 8105 or len(table) != 8105:
        raise RuntimeError("Expected 8,105 distinct characters in the bundled dataset")
    return table


def _text(value: str) -> None:
    if not isinstance(value, str):
        raise TypeError("Expected a Unicode string")
    if not value:
        raise ValueError("Text must not be empty")
    if any(0xD800 <= ord(char) <= 0xDFFF for char in value):
        raise ValueError("Text must not contain unpaired UTF-16 surrogates")


def lookup(character: str) -> Character | None:
    """Return a 2013 table entry, or None if the exact scalar is absent."""
    _text(character)
    if len(character) != 1:
        raise ValueError("lookup() accepts exactly one Unicode scalar")
    return _table().get(character)


def characters(level: int | None = None) -> tuple[Character, ...]:
    """Return entries in official index order, optionally limited to level 1/2/3."""
    if level is not None and (type(level) is not int or level not in (1, 2, 3)):
        raise ValueError("level must be 1, 2, 3 or None")
    return tuple(record for record in _table().values() if level is None or record.level == level)


def check_name(text: str) -> NameCheck:
    """Check every scalar, including spaces, punctuation and variation selectors.

    Table membership is not a judgment about registration, pronunciation,
    suitability, meaning or the quality of a name. Input is never normalized.
    """
    _text(text)
    table = _table()
    return NameCheck(
        text,
        tuple(
            CharacterCheck(position, char, f"U+{ord(char):04X}", table.get(char))
            for position, char in enumerate(text, start=1)
        ),
    )
