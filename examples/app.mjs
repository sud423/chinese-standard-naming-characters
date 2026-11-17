import { createLookup, checkText } from "./checker.mjs";

const form = document.querySelector("#check-form");
const input = document.querySelector("#name-input");
const submit = document.querySelector("#check-button");
const status = document.querySelector("#data-status");
const error = document.querySelector("#error");
const retry = document.querySelector("#retry-button");
const result = document.querySelector("#result");
const empty = document.querySelector("#empty-state");
const examples = [...document.querySelectorAll("[data-example]")];
let table;

function showError(message) {
  error.textContent = message;
  error.hidden = false;
}

async function loadData() {
  retry.hidden = true;
  error.hidden = true;
  status.textContent = "正在载入字表…";
  try {
    if (location.protocol === "file:")
      throw new Error("请按照仓库 README 启动本地 HTTP 服务后打开此示例。");
    const response = await fetch("../yongjia_naming/data/characters.json");
    if (!response.ok)
      throw new Error("字表载入失败，请检查本地服务是否从仓库根目录启动。");
    table = createLookup(await response.json());
    status.textContent = "8,105 字 · 已就绪";
    submit.disabled = false;
    examples.forEach((button) => {
      button.disabled = false;
    });
  } catch (cause) {
    status.textContent = "字表未就绪";
    showError(cause.message || "载入失败，请重试。");
    retry.hidden = false;
  }
}

function render() {
  error.hidden = true;
  try {
    if (!table) throw new Error("字表尚未载入，请稍候。");
    const checks = checkText(input.value, table);
    const absent = checks.filter((item) => !item.record).length;
    document.querySelector("#result-title").textContent = absent
      ? `有 ${absent} 个字符未在表中匹配`
      : "每个字都在 2013 版字表中";
    document.querySelector("#result-detail").textContent = absent
      ? "请核对原始字形或输入；“未匹配”不等同于错字，也不代表不能登记。"
      : "这一步核对了收录情况；不会据此判断名字好坏或登记结果。";
    const rows = document.querySelector("#result-rows");
    rows.replaceChildren();
    for (const item of checks) {
      const row = document.createElement("tr");
      const display = item.character === " " ? "空格" : item.character;
      const detail = item.record
        ? `第 ${item.record.level} 级 · 序号 ${item.record.index}`
        : "未在表中匹配";
      for (const value of [display, item.codepoint, detail]) {
        const cell = document.createElement("td");
        cell.textContent = value;
        row.append(cell);
      }
      if (!item.record) row.classList.add("absent");
      rows.append(row);
    }
    result.hidden = false;
    empty.hidden = true;
  } catch (cause) {
    result.hidden = true;
    empty.hidden = false;
    showError(cause.message);
  }
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  render();
});
examples.forEach((button) =>
  button.addEventListener("click", () => {
    input.value = button.dataset.example;
    render();
  }),
);
retry.addEventListener("click", loadData);
loadData();
