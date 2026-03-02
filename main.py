import argparse
from pathlib import Path

import pdfplumber

from formatter import format_transaction
from parser import parse_the_page


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert a Trade Republic PDF statement to Beancount entries."
    )
    parser.add_argument(
        "--input",
        default="statements/statement.pdf",
        help="Path to input PDF statement (default: statements/statement.pdf)",
    )
    parser.add_argument(
        "--output",
        default="output/output.bean",
        help="Path to output .bean file (default: output/output.bean)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.exists():
        raise FileNotFoundError(f"Input PDF not found: {input_path}")

    transactions = []
    with pdfplumber.open(str(input_path)) as pdf:
        for page_num, page in enumerate(pdf.pages):
            words = page.extract_words(x_tolerance=1)
            # x_tolerance=1 so texts like "KartentransakationLidl" are split correctly.

            # Stop parsing once the cash overview section starts.
            barmittel = next((w for w in words if w["text"] == "BARMITTELÜBERSICHT"), None)
            if barmittel:
                words = [w for w in words if w["bottom"] < barmittel["top"] - 10]

            if page_num == 0:
                umsatz = next((w for w in words if w["text"] == "UMSATZÜBERSICHT"), None)
                if umsatz:
                    words = [w for w in words if w["top"] > umsatz["bottom"] + 30]
                else:
                    raise ValueError("No UMSATZÜBERSICHT in the first page.")

            transactions.extend(parse_the_page(words))

            if barmittel:
                break

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        for t in transactions:
            if t is None:
                continue
            entry = format_transaction(t)
            if entry:
                f.write(entry)
                f.write("\n")

    print(f"Wrote {len([t for t in transactions if t is not None])} transactions to {output_path}")


if __name__ == "__main__":
    main()
