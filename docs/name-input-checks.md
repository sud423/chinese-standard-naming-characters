# 中文姓名表单：先分清“字符可读”与“字表收录”

[文章目录](README.md) · 永嘉取名网开源文档

永嘉取名网开源的这份工具，解决的是一个基础问题：按原始输入核对 2013 版规范字表，并把结果与依据返回给调用方。

## 1. 不用一个基本区正则代替规范字表

常见写法 `^[\u4e00-\u9fa5]+$` 检查的是一个码点区间。它既不等于全部汉字，也不等于《通用规范汉字表》。例如表内的 `𣲗` 是 `U+23C97`，处于补充平面，落在这个区间之外。

```python
from yongjia_naming import lookup

record = lookup("𣲗")
assert record.codepoint == "U+23C97"
assert record.index == 6613
assert record.level == 3
```

反过来，处在某个汉字区间内也不能证明已被这份字表收录。需要核对字表时，应使用实际成员集合，并返回字表版本。

## 2. JavaScript 的字符串长度不是汉字数

```javascript
const input = '李𣲗';
console.log(input.length);             // 3 个 UTF-16 码元
console.log(Array.from(input).length); // 2 个 Unicode 码点
```

浏览器示例用 `Array.from()` 遍历码点，Python 3 的字符串迭代也能保留这个补充平面字符。两端测试均核对 `U+23C97` 和序号 `6613`，避免浏览器与服务端给出不同结果。

码点数也不等于用户感知的字素数量。带异体选择符的显示字形可能包含多个码点；本工具逐码点报告，不替调用方判断应该显示成几个字。

## 3. 检查阶段保留空白和字形差异

```python
from yongjia_naming import check_name

report = check_name("李 A").to_dict()
assert report["text"] == "李 A"
assert report["characters"][1]["codepoint"] == "U+0020"
assert report["characters"][1]["in_table"] is False
```

如果先删除空白、自动繁简转换或执行 Unicode 归一化，再告诉用户“原文通过”，就会隐藏实际输入与被检查文字之间的差异。若产品需要整理输入，应显示整理前后内容，再由用户确认；本工具默认不做这一步。

## 4. 使用“需要核对”，避免把结果解释过头

建议把返回结果用于编辑提示，例如：

> 第 2 个码点未在 2013 版字表中匹配，请核对原始字形。

不要直接改写成“这个字是错字”“名字一定不能登记”或“三级字不适合取名”。字表收录、读音字义、地区系统支持与具体姓名登记是不同的问题。这里的工具只给出第一项依据。

## 接入与来源

- [Python API、命令行及浏览器示例](../README.md)
- [数据来源、字段与可复现方法](../DATA_SOURCES.md)
- [把规范字校验接入编辑流程](editorial-character-checks.md)：继续安排读音、字义与实际使用核对。
- [永嘉取名网](https://www.yjmbjy.com/)：继续了解名字的读音、字义与使用场景。
