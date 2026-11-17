"""Run from the repository root: python examples/python_usage.py (after pip install .)."""

from yongjia_naming import check_name, lookup

entry = lookup("一")
print(entry)

for sample in ("李明", "李𣲗", "李 A"):
    result = check_name(sample)
    print(result.to_dict())
