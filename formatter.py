def format_transaction(t):
    date = t.date.strftime("%Y-%m-%d")
    amount = t.amount_out if t.amount_out > 0 else t.amount_in
    payee, account_out, account_in = get_account(t)
    
    return f"""{date} * "{payee}" "{t.description}"
    {account_out}        -{amount:.2f} EUR
    {account_in}             {amount:.2f} EUR
            """

GROCERY_STORES = ["lidl", "aldi", "hit", "rewe", "edeka", "penny",
                   "rossman", "asia feinkost", "joybuy", "netto",
                   'KAUFLAND']
DM_KEYWORDS = ["dm-drogerie", "dm.de",'DM DROGERIE']
BOULDER_GYM = ['eb muenchen','dav kletterzentrum']
RESTAURANT = ['burger king','studierendenwerk','ha vietnamese','Pizza and More','MCDONALD']

def if_health_insurance(t):
    return "barmer" in t.description.lower() and t.amount_out > 150

def if_mobile(t):
    return "vodafone" in t.description.lower() and t.amount_out < 30

def if_internet(t):
    return "vodafone" in t.description.lower() and t.amount_out > 30

DEFAULT_JOINT = "Assets:TradeRepublic:Joint"

RULES = [
    (lambda t: any(store.lower() in t.description.lower() for store in GROCERY_STORES),
     lambda t: next(store for store in GROCERY_STORES if store.lower() in t.description.lower()),
        DEFAULT_JOINT,
        "Expenses:Shared:Groceries"),
    
    (lambda t: "s&p 500" in t.description.lower(),
        "Invest",
        "Assets:TradeRepublic:Personal",
        "Assets:Investment:ETF:SP500"),
    
    (lambda t: any(restaurant.lower() in t.description.lower() for restaurant in RESTAURANT),
     lambda t: next(store for store in RESTAURANT if store.lower() in t.description.lower()),
        DEFAULT_JOINT,
        "Expenses:Shared:DineOut"),

    (if_health_insurance,
        "Barmer",
        "Assets:TradeRepublic:Personal",
        "Expenses:Personal:HealthInsurance"),
    
    (if_mobile,
     "Vodafone",
        DEFAULT_JOINT,
        "Expenses:Shared:Utility:Mobile"),

    (if_internet,
     "Vodafone",
        DEFAULT_JOINT,
        "Expenses:Shared:Utility:Internet"),

    (lambda t: "chatgpt" in t.description.lower(),
        "Open-AI",
        DEFAULT_JOINT,
        "Expenses:Shared:Utility:Subscription"),

    (lambda t: "e.on" in t.description.lower(),
        "e.on",
        DEFAULT_JOINT,
        "Expenses:Shared:Utility:Electricity"),

    (lambda t: "muenchner verkehrsge" in t.description.lower(),
        "MVG",
        "Assets:TradeRepublic:Personal",
        "Expenses:Personal:PublicTransport"),

    (lambda t: "getsafe" in t.description.lower(),
        'getsafe',
        DEFAULT_JOINT,
        "Expenses:Shared:Insurance"),

    (lambda t: any(kw.lower() in t.description.lower() for kw in DM_KEYWORDS),
     'dm-drogerie',
        DEFAULT_JOINT,
        "Expenses:Shared:Household:Supplies"),

    (lambda t: any(gym.lower() in t.description.lower() for gym in BOULDER_GYM),
     lambda t: next(store for store in BOULDER_GYM if store.lower() in t.description.lower()),
        DEFAULT_JOINT,
        "Expenses:Shared:Sport"),
]

def get_account(t):
    for match, payee, from_account, to_account in RULES:
        if match(t):
            resolved_payee = payee(t) if callable(payee) else payee
            return resolved_payee, from_account, to_account
    return "None", "Assets:TradeRepublic:Personal", "NEEDS PERSONAL MODIFICATION"