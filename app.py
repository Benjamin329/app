# app.py
from flask import Flask, render_template, url_for
import random
from datetime import datetime, timedelta

app = Flask(__name__, static_folder="static", template_folder="templates")

# ---------- Safe test BINs/prefixes (non-production/test-like) ----------
BRAND_PREFIXES = {
    "VISA": ["411111", "401288"],
    "MASTERCARD": ["555555", "510510"],
    "AMEX": ["378282", "371449"]
}

BRAND_CONFIG = {
    "VISA": {"length": 16, "cvv_len": 3},
    "MASTERCARD": {"length": 16, "cvv_len": 3},
    "AMEX": {"length": 15, "cvv_len": 4}
}

FIRST = ["Alex","Jordan","Taylor","Morgan","Riley","Casey","Jamie","Avery","Quinn","Cameron",
         "Charlie","Rowan","Sam","Parker","Reese","Harper","Skyler","Logan","Blake","Drew"]
LAST = ["Smith","Johnson","Brown","Jones","Miller","Davis","Wilson","Taylor","Anderson","Thomas",
        "Moore","Jackson","Martin","Lee","Perez","Thompson","White","Harris","Sanchez","Clark"]

# ---------- Helpers ----------
def luhn_check_digit(digits: str) -> int:
    total = 0
    rev = digits[::-1]
    for i,ch in enumerate(rev):
        d = int(ch)
        if i % 2 == 0:
            total += d
        else:
            d2 = d*2
            total += (d2 - 9) if d2 > 9 else d2
    return (10 - (total % 10)) % 10

def generate_luhn_number(prefix: str, length: int) -> str:
    body_len = length - len(prefix) - 1
    body = ''.join(str(random.randint(0,9)) for _ in range(body_len))
    partial = prefix + body
    return partial + str(luhn_check_digit(partial))

def random_name():
    return f"{random.choice(FIRST)} {random.choice(LAST)}"

def random_expiry():
    future = datetime.utcnow() + timedelta(days=random.randint(30, 365*5))
    return future.strftime("%m/%y")

def random_cvv(n=3):
    if n==4:
        return f"{random.randint(0,9999):04d}"
    return f"{random.randint(0,999):03d}"

def chunk_card(num: str) -> str:
    if len(num) == 15:  # Amex style grouping
        return f"{num[:4]} {num[4:10]} {num[10:]}"
    return " ".join(num[i:i+4] for i in range(0, len(num), 4))

def mask_number(num: str) -> str:
    if len(num) >= 16:
        return "•••• •••• •••• " + num[-4:]
    if len(num) == 15:
        return "•••• •••• •" + num[-4:]
    return "•••• " + num[-4:]

# ---------- Generate a batch of cards ----------
def generate_cards(count=8):
    cards = []
    for i in range(count):
        brand = random.choice(list(BRAND_PREFIXES.keys()))
        prefix = random.choice(BRAND_PREFIXES[brand])
        length = BRAND_CONFIG[brand]["length"]
        number = generate_luhn_number(prefix, length)
        name = random_name()
        expiry = random_expiry()
        cvv = random_cvv(BRAND_CONFIG[brand]["cvv_len"])
        cards.append({
            "id": i+1,
            "brand": brand,
            "name": name,
            "number": number,
            "display": chunk_card(number),
            "masked": mask_number(number),
            "expiry": expiry,
            "cvv": cvv
        })
    return cards

# ---------- Routes ----------
@app.route("/")
def index():
    cards = generate_cards(count=12)  # change count if you want more or fewer
    return render_template("index.html", cards=cards)

# Health check for some hosts
@app.route("/ping")
def ping():
    return "pong", 200

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
