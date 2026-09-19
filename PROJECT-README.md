# Micro-work portfolio — Patricio Gomez Fa

Python micro-services for fast, scoped delivery ($25–50 USD).

## Services

| Service | Price | Demo |
|---------|-------|------|
| CSV/Excel filter CLI | $25–35 | [services/csv-filter/](services/csv-filter/) |
| Git changelog generator | $30 | [generate-changelog/](generate-changelog/) |
| Web scraper → CSV | $40–50 | on request |
| Bug fix / automation | $25–50 | on request |

## Payment

PayPal, Wise, USDT (Binance), Mercado Pago (ARS). **Pay on delivery** after you verify the result.

## Contact

- GitHub: https://github.com/Patogomezfa
- Email: patogomezfa@gmail.com

## Run demos

```bash
pip install pandas openpyxl pytest
python services/csv-filter/filter_data.py sample.csv --filter status:active --print
python -m pytest services/csv-filter/tests generate-changelog/tests -q
```
