# 8,105 个规范字从哪里来：版本、序号与数据一致性

[文章目录](README.md) · 永嘉取名网开源文档

下载到一份“8,105 字”的文件，只能先确认条数。要用于姓名表单或内容编辑，还需要知道它依据哪一版字表、每条记录从哪里取得，以及 JSON、CSV 和 TXT 是否表达了同一份数据。本文沿着本仓库的实际文件，给出一套可以自己运行的检查方法。

## 字表年份与数据库版本分别记录

本项目依据的是 **2013 版《通用规范汉字表》**，机器可读映射来自固定的 **Unicode 17.0.0 Unihan** 快照。2013 是字表年份，17.0.0 是所用 Unicode 数据库版本，两者不能互相替代。

转换脚本读取 Unihan 的 `kTGH` 属性。例如 `2013:1` 表示这份字表中的序号 1；它不表示读音、笔画或起名评分。脚本保留原始引用，并按序号排列字符。字段的官方定义见 [UAX #38 固定版本](https://www.unicode.org/reports/tr38/tr38-39.html#kTGH)。

这条来源链也有明确边界：`kTGH` 是上游的 Provisional 属性，本项目验证其映射和产物的一致性，尚未逐字人工比对官方 PDF 字形。固定快照便于复现，不代表持续跟随最新版本。

## 为什么只数到 8,105 还不够

文件即使条数正确，也可能把一个字重复两次、漏掉另一个字，或者在转换时改变顺序。至少要把以下问题分开检查：

| 检查 | 能发现的问题 |
| --- | --- |
| 字符互异、每项只有一个码点 | 重复记录、把多码点文本当成单字 |
| 序号完整覆盖 `1..8105` | 缺号、重复序号、顺序变化 |
| 每字与记录的码点一致 | 展示文字与 `U+...` 字段不对应 |
| 按序号分级，核对各级数量 | 分级边界或转换条件写错 |
| JSON、CSV、TXT 对照 | 某一种下载格式漏字或顺序不同 |
| JSON、CSV 哈希与清单一致 | 文件内容发生变化或意外损坏 |

这些检查用于确认数据结构和转换结果。它们不会把字表级别变成名字质量等级。

## 在仓库根目录运行一次检查

下面的 Python 示例只读取仓库现有文件，无须联网或安装第三方库。可以从仓库根目录进入 Python，将整段代码执行：

```python
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path

root = Path.cwd()
data = root / "yongjia_naming" / "data"
manifest = json.loads((data / "manifest.json").read_text(encoding="utf-8"))
json_bytes = (data / "characters.json").read_bytes()
csv_bytes = (root / "data" / "characters.csv").read_bytes()
rows = json.loads(json_bytes)

assert manifest["table_edition"] == "2013"
assert manifest["unicode_version"] == "17.0.0"
assert manifest["source_property"] == "kTGH"
assert len(rows) == manifest["count"] == 8105
assert len({row["character"] for row in rows}) == 8105
assert [row["index"] for row in rows] == list(range(1, 8106))

for row in rows:
    assert len(row["character"]) == 1
    assert row["codepoint"] == f"U+{ord(row['character']):04X}"
    assert row["source_ref"] == f"2013:{row['index']}"
    expected_level = 1 if row["index"] <= 3500 else 2 if row["index"] <= 6500 else 3
    assert row["level"] == expected_level

assert Counter(row["level"] for row in rows) == {1: 3500, 2: 3000, 3: 1605}
assert hashlib.sha256(json_bytes).hexdigest() == manifest["json_sha256"]
assert hashlib.sha256(csv_bytes).hexdigest() == manifest["csv_sha256"]

csv_rows = list(csv.DictReader(csv_bytes.decode("utf-8").splitlines()))
expected_csv = [{field: str(row[field]) for field in manifest["fields"]} for row in rows]
assert csv_rows == expected_csv
txt_rows = (root / "data" / "characters.txt").read_text(encoding="utf-8").splitlines()
assert txt_rows == [row["character"] for row in rows]
print("8,105 条记录及 JSON / CSV / TXT 一致性检查通过")
```

哈希在这里用于检查文件与清单是否一致。如果文件和清单同时被替换，单靠二者相等不能证明来源可信；来源版本、上游下载地址和转换过程仍需保留。

## 需要追溯上游时，再复现转换

日常查询可直接使用随包数据。核查来源或准备升级时，按[数据来源说明](../DATA_SOURCES.md#复现)下载固定 Unihan ZIP，再执行已有脚本：

```sh
python scripts/build_data.py --unihan Unihan-17.0.0.zip --check
```

`--check` 会先核对上游 ZIP 的固定 SHA-256，再提取映射，并逐字节比较仓库的四个数据产物。它只检查，不写入文件。升级来源时，应查看字符、序号、级别及许可变化，再决定是否更新，不能只改一个哈希让检查通过。

## 把依据与数据一起交付

复制一份 TXT 到另一个应用，确实很方便，但使用者也需要知道它来自哪里。再分发时应一并保留[来源说明](../DATA_SOURCES.md)、[Unicode 数据许可](../yongjia_naming/data/LICENSE-UNICODE.txt)及必要归属。本仓库的原创代码与文档采用 MIT，派生数据单独遵循 Unicode License V3。

数据确认以后，可以继续看[姓名表单接入说明](name-input-checks.md)，或者在[永嘉取名网起名知识](https://www.yjmbjy.com/knowledge)阅读字形、读音与实际使用问题。
