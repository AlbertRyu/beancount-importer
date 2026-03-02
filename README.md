# beancount-importer

Convert a Trade Republic PDF account statement into Beancount transactions.

## Quick start (no `uv` required)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

By default, this reads `statements/statement.pdf` and writes `output/output.bean`.

## Usage

```bash
python main.py --input statements/statement.pdf --output output/output.bean
```

You can also use `uv` if you want:

```bash
uv sync
uv run main.py
```

## What it does

- Reads transactions from a Trade Republic PDF statement
- Parses statement rows using a fixed layout
- Maps transactions to Beancount accounts using keyword rules
- Writes entries to a `.bean` file

## Requirements

- Python `3.13` (see `.python-version`)
- `pdfplumber==0.11.9`

## Project layout

- `main.py`: CLI entrypoint, PDF reading, output writing
- `parser.py`: row grouping and transaction parsing from PDF words
- `models.py`: `Transaction` dataclass
- `formatter.py`: Beancount formatting and account mapping rules

## Customization

### 1. Update account mapping rules

Edit `RULES` in `formatter.py`.

- Each rule is `(match_fn, payee, from_account, to_account)`
- `match_fn` receives a `Transaction` and returns `True/False`
- `payee` can be a string or callable
- First matching rule is used

Fallback mapping when no rule matches:

- Payee: `"None"`
- From account: `Assets:TradeRepublic:Personal`
- To account: `NEEDS PERSONAL MODIFICATION`

### 2. Update PDF parsing layout

Edit constants and filters in `parser.py` / `main.py`:

- `COLUMNS` boundaries (x-axis mapping)
- Row grouping tolerance in `group_words_by_row`
- Section markers (`UMSATZÜBERSICHT`, `BARMITTELÜBERSICHT`)

These are currently tailored to one Trade Republic statement format.

## Notes and limitations

- Parser assumes German date/amount formats.
- Parser logic is hardcoded for one statement structure.
- Multi-line or unusual rows may need parser adjustments.

## Example output

```beancount
2026-01-02 * "lidl" "Kartentransaktion Lidl ..."
    Assets:TradeRepublic:Joint        -24.90 EUR
    Expenses:Shared:Groceries          24.90 EUR
```
