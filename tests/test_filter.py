import csv
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("filter_module", ROOT / "filter_data.py")
filter_data = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules["filter_module"] = filter_data
spec.loader.exec_module(filter_data)


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["name", "status"])
        writer.writeheader()
        writer.writerows(rows)


def test_parse_filter():
    assert filter_data.parse_filter("status:active") == ("status", "active")


def test_filter_csv(tmp_path: Path):
    source = tmp_path / "input.csv"
    output = tmp_path / "out.csv"
    write_csv(
        source,
        [
            {"name": "a", "status": "active"},
            {"name": "b", "status": "inactive"},
            {"name": "c", "status": "active"},
        ],
    )
    count = filter_data.filter_with_csv(source, [("status", "active")], output, False)
    assert count == 2
    text = output.read_text(encoding="utf-8")
    assert "a" in text and "c" in text and "inactive" not in text
