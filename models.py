from dataclasses import dataclass
from datetime import date

@dataclass
class Transaction:
    date: date                  # Date of the transaction
    typ: str                    # "Kartentransaction"
    description: str            # ?
    amount_in: float               # Amount in or out
    amount_out: float               # Amount in or out
    saldo: float