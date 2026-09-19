# CSV / Excel Filter CLI

Lightweight row filter for `.csv`, `.xlsx`, and `.xls` files.

## Setup

```bash
pip install pandas openpyxl
```

## Usage

```bash
python filter_data.py input.csv --filter status:active --output filtered.csv
python filter_data.py data.xlsx --filter country:AR --filter tier:pro --print
```

## Notes

- Filters are exact string matches (`column:value`).
- Multiple `--filter` flags are ANDed together.
- Without `--output`, results print to stdout unless `--print` is set.
