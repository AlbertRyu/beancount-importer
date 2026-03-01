from models import Transaction
from datetime import datetime
import pdfplumber

COLUMNS = [
    (74,  100, 'datum'),
    (100, 160, 'typ'),
    (160, 368, 'beschreibung'),
    (368, 422, 'eingang'),
    (422, 475, 'ausgang'),
    (475, 9999, 'saldo'),
]

def parse_the_pdf(file_path):
    # with pdfplumber.open('pdfs/statement.pdf') as pdf:
    #     page = pdf.pages[0]  # 第7页

    #     transaction_list = []
    pass
        

def parse_the_page(words):

    transaction_per_page = []
    
    rows = group_words_by_row(words)

    for row in rows:
        t = parse_row(row)
        transaction_per_page.append(t)

    return transaction_per_page

def group_words_by_row(words, tolerance=20):
    """把 top 值相近的词归为同一行"""
    rows = []
    
    for word in sorted(words, key=lambda w: w['top']):
        if not (word['top'] > 159 and word['top'] < 750): # Page middle
            #print(f'Skip {word['text']}')
            continue
        # 看这个词是否属于已有的某一行
        placed = False
        for row in rows:
            row_top = row[0]['top']
            if abs(word['top'] - row_top) <= tolerance:
                row.append(word)
                placed = True
                break
        
        # 没有匹配的行，新建一行
        if not placed:
            rows.append([word])
    
    return rows  # List[List[word]]


def get_column(x0):
    for start, end, name in COLUMNS:
        if start <= x0 < end:
            return name
    return None


def parse_row(row_words):
    """一行词 → 一个 Transaction（或 None 如果不是交易行）"""
    #print(''.join([w['text'] for w in row_words]))
    # 按列分组
    columns = {'datum': [], 'typ': [], 'beschreibung': [], 
               'eingang': [], 'ausgang': [], 'saldo': []}
    
    for word in row_words:
        col = get_column(word['x0'])
        if col:
            columns[col].append(word['text'])
    
    # 必须有日期才算是交易行
    if not columns['datum']:
        return None
    
    # 拼接各列文本
    date_str = " ".join(columns['datum'])      # "02 Jan. 2026"
    typ      = " ".join(columns['typ'])         # "Handel"
    desc     = " ".join(columns['beschreibung'])
    eingang  = " ".join(columns['eingang'])     # "100,00 €" 或空
    ausgang  = " ".join(columns['ausgang'])
    saldo  = " ".join(columns['saldo'])

    
    # 转换日期
    date = datetime.strptime(date_str, "%d %b. %Y").date()
    
    # 转换金额（德式格式："1.234,56 €" → 1234.56）
    def parse_amount(s):
        if not s:
            return 0.0
        s = s.replace("€", "").replace(".", "").replace(",", ".").strip()
        return float(s)
    
    return Transaction(
        date=date,
        typ=typ,
        description=desc,
        amount_in=parse_amount(eingang),
        amount_out=parse_amount(ausgang),
        saldo=parse_amount(saldo)
    )
