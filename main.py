import pdfplumber
from parser import parse_the_page
from formatter import format_transaction

def main():
    print("Hello from beancount-importer!")

    with pdfplumber.open('pdfs/statement.pdf') as pdf:

        transactions = []
        for page_num, page in enumerate(pdf.pages):
            words = page.extract_words(x_tolerance=1)
            # x_tolerance=1 for KartentransakationLidl is detected to be one word in the default value of 3

            # 检查这一页是否有 BARMITTELÜBERSICHT
            barmittel = next((w for w in words if w['text'] == 'BARMITTELÜBERSICHT'), None)
            
            if barmittel:
                words = [w for w in words if w['bottom'] < barmittel['top']-10]
            
            if page_num == 0:
                umsatz = next((w for w in words if w['text'] == 'UMSATZÜBERSICHT'), None)
                if umsatz:
                    words = [w for w in words if w['top'] > umsatz['bottom']+30]
                else:
                    raise ValueError("No UMSATZÜBERSICHT in the first page.")

            transactions.extend(parse_the_page(words))

            if barmittel:
                break

        with open("output.bean", "w", encoding="utf-8") as f:
            for t in transactions:
                entry = format_transaction(t)
                if entry:
                    f.write(entry)
                    f.write("\n")

if __name__ == "__main__":
    main()
