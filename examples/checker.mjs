// MIT — 永嘉取名网 (Yongjia Naming). All checks stay in the current browser.
export function createLookup(records) {
  if (!Array.isArray(records) || records.length !== 8105) {
    throw new Error("字表不完整，请重新载入。");
  }
  const table = new Map();
  records.forEach((record, offset) => {
    const expectedLevel = offset < 3500 ? 1 : offset < 6500 ? 2 : 3;
    if (
      typeof record.character !== "string" ||
      Array.from(record.character).length !== 1 ||
      record.index !== offset + 1 ||
      record.level !== expectedLevel ||
      record.codepoint !==
        `U+${record.character.codePointAt(0).toString(16).toUpperCase().padStart(4, "0")}` ||
      record.source_ref !== `2013:${offset + 1}` ||
      table.has(record.character)
    ) {
      throw new Error("字表记录有误，请核对数据版本。");
    }
    table.set(record.character, record);
  });
  return table;
}

export function checkText(text, table) {
  if (typeof text !== "string" || text.length === 0)
    throw new Error("请先填写需要核对的文字。");
  const input = Array.from(text);
  if (input.length > 40)
    throw new Error("请将本次输入控制在 40 个 Unicode 码点以内。");
  if (
    input.some(
      (char) => char.codePointAt(0) >= 0xd800 && char.codePointAt(0) <= 0xdfff,
    )
  ) {
    throw new Error("输入含有不完整的 Unicode 字符，请重新输入。");
  }
  return input.map((character, offset) => ({
    position: offset + 1,
    character,
    codepoint: `U+${character.codePointAt(0).toString(16).toUpperCase().padStart(4, "0")}`,
    record: table.get(character) ?? null,
  }));
}
