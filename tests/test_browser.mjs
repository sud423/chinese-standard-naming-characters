import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import { createLookup, checkText } from "../examples/checker.mjs";

const records = JSON.parse(
  readFileSync(
    new URL("../yongjia_naming/data/characters.json", import.meta.url),
    "utf8",
  ),
);
const table = createLookup(records);

test("complete table and counts in the browser module", () => {
  assert.equal(table.size, 8105);
  assert.deepEqual(
    [1, 2, 3].map(
      (level) =>
        [...table.values()].filter((row) => row.level === level).length,
    ),
    [3500, 3000, 1605],
  );
  assert.equal(table.get("一").index, 1);
});

test("supplementary-plane characters remain one scalar", () => {
  const result = checkText("李𣲗", table);
  assert.equal(result.length, 2);
  assert.equal(result[1].codepoint, "U+23C97");
  assert.equal(result[1].record.index, 6613);
});

test("spaces, Latin characters and variation selectors are retained", () => {
  const result = checkText("李 A\uFE00", table);
  assert.deepEqual(
    result.map((row) => row.character),
    ["李", " ", "A", "\uFE00"],
  );
  assert.deepEqual(
    result.map((row) => row.record !== null),
    [true, false, false, false],
  );
});

test("compatibility characters are not silently normalized", () => {
  assert.equal("\uF9E1".normalize("NFKC"), "李");
  assert.equal(checkText("\uF9E1", table)[0].record, null);
});

test("length checks use scalars, not UTF-16 code units", () => {
  assert.equal(checkText("𣲗".repeat(40), table).length, 40);
  assert.throws(() => checkText("𣲗".repeat(41), table), /40/);
});

test("empty and unpaired-surrogate input is rejected", () => {
  assert.throws(() => checkText("", table));
  assert.throws(() => checkText(null, table));
  assert.throws(() => checkText("\uD800", table));
});

test("missing, duplicate and damaged table records are rejected", () => {
  assert.throws(() => createLookup(records.slice(1)));
  const duplicate = structuredClone(records);
  duplicate[1] = { ...duplicate[0], index: 2, source_ref: "2013:2" };
  assert.throws(() => createLookup(duplicate));
  const wrongLevel = structuredClone(records);
  wrongLevel[3500].level = 1;
  assert.throws(() => createLookup(wrongLevel));
  const wrongCodepoint = structuredClone(records);
  wrongCodepoint[0].codepoint = "U+0000";
  assert.throws(() => createLookup(wrongCodepoint));
});

test("all exported scalars return their exact original records", () => {
  for (const record of records) {
    assert.deepEqual(checkText(record.character, table)[0].record, record);
  }
});
