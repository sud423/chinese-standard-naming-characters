# 数据来源与复现

## 来源链

| 项目 | 固定来源 |
| --- | --- |
| 字表依据 | 2013 版《通用规范汉字表》 |
| 官方背景说明 | [教育部：国务院公布《通用规范汉字表》](https://www.moe.gov.cn/jyb_xwfb/xw_fbh/moe_2069/s7135/s7562/s7564/201308/t20130827_156334.html) |
| 机器可读上游 | [Unicode 17.0.0 / Unihan.zip](https://www.unicode.org/Public/17.0.0/ucd/Unihan.zip) |
| 使用字段 | `kTGH`：`2013:序号`；不使用 `kTGHZ2013` 字典读音字段 |
| 字段定义 | [UAX #38（Unicode 17.0.0 固定版）](https://www.unicode.org/reports/tr38/tr38-39.html#kTGH) |
| 数据许可 | [Unicode License V3，随包完整保留](yongjia_naming/data/LICENSE-UNICODE.txt) |
| 整理维护 | 永嘉取名网 · Yongjia Naming |

固定使用 Unicode 17.0.0 快照是为了可复现，不代表这是最新 Unicode 版本。字表年份与 Unicode 数据库版本是两个不同概念。

## 已核验范围

从固定快照所有 `Unihan*.txt` 成员中提取 `kTGH`，按其序号排序，校验：

- 共 8,105 个互异 Unicode 字符，序号完整覆盖 `1..8105`。
- 一级 `1..3500`，共 3,500 字；二级 `3501..6500`，共 3,000 字；三级 `6501..8105`，共 1,605 字。
- JSON、CSV、TXT 的字符、顺序一致；JSON 与 CSV 的 SHA-256 存在清单中。
- 补充平面字符按完整 Unicode 码点处理，不按 UTF-16 两个码元拆字。

这是对 Unihan 映射和生成产物的一致性校验，尚未逐字人工比对官方 PDF 的字形。`kTGH` 在上游定义中属于 Provisional 属性；发现差异时应附官方依据反馈，而不是把程序结果当作最终行政结论。

## 字段

| 字段 | 类型 | 示例 | 含义 |
| --- | --- | --- | --- |
| `character` | string | `一` | 单个 Unicode 码点 |
| `codepoint` | string | `U+4E00` | 大写十六进制码点，至少四位 |
| `index` | integer | `1` | 2013 版字表序号 |
| `level` | integer | `1` | 1、2 或 3；由字表序号区间得到 |
| `source_ref` | string | `2013:1` | 原始 `kTGH` 值 |

“级别”不是姓名质量分数。本数据不包含字义、姓氏读法、五行、笔画吉凶、取名适宜性或登记可用性判断。

## 复现

只需 Python 3.10+ 标准库。先从固定上游下载原始 ZIP，再运行转换；脚本不自动联网、不解压路径到磁盘。

```sh
curl -fL https://www.unicode.org/Public/17.0.0/ucd/Unihan.zip -o Unihan-17.0.0.zip
python scripts/build_data.py --unihan Unihan-17.0.0.zip --check
```

上游 SHA-256：

```text
f7a48b2b545acfaa77b2d607ae28747404ce02baefee16396c5d2d7a8ef34b5e
```

`--check` 不修改文件；省略它会重新生成本仓库的四个数据产物。日常使用无须下载原始 ZIP，仓库和 Python 包已附完整数据。

升级上游前须先确认版本、许可、来源哈希、字符差异和测试；不得仅修改哈希跳过内容核验。来源变更记录维护在 [CHANGELOG.md](CHANGELOG.md)。
