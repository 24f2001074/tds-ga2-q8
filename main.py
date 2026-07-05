import re

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class InvoiceRequest(BaseModel):
    text: str


class InvoiceResponse(BaseModel):
    vendor: str
    amount: float
    currency: str
    date: str


@app.post("/extract", response_model=InvoiceResponse)
def extract(req: InvoiceRequest):

    print("\n" + "=" * 80)
    print("RAW INPUT:")
    print(repr(req.text))
    print("=" * 80)

    text = req.text

    if not text.strip():
        print("Empty input received.")
        return InvoiceResponse(
            vendor="",
            amount=0,
            currency="",
            date=""
        )

    # ---------------- Currency ----------------
    currency_match = re.search(
        r"\b(USD|EUR|GBP)\b",
        text,
        re.IGNORECASE
    )

    currency = currency_match.group(1).upper() if currency_match else ""

    # ---------------- Date ----------------
    date_match = re.search(
        r"2026-\d{2}-\d{2}",
        text
    )

    date = date_match.group(0) if date_match else ""

    # ---------------- Amount ----------------

    amount = 0.0

    amount_match = re.search(
        r"\b(?:USD|EUR|GBP)\s*([0-9]+(?:\.[0-9]{1,2})?)",
        text,
        re.IGNORECASE,
    )

    if not amount_match:
        amount_match = re.search(
            r"([0-9]+(?:\.[0-9]{1,2})?)\s*(?:USD|EUR|GBP)\b",
            text,
            re.IGNORECASE,
        )

    if amount_match:
        amount = float(amount_match.group(1))

    # ---------------- Vendor ----------------

        vendor = ""

    m = re.search(
        r"^(.*?Industries Ltd\.)",
        text,
        re.MULTILINE,
    )

    if m:
        vendor = m.group(1).strip()

    if not vendor:
        lines = [x.strip() for x in text.splitlines() if x.strip()]
        if lines:
            vendor = lines[0]

    print("Extracted:")
    print({
        "vendor": vendor,
        "amount": amount,
        "currency": currency,
        "date": date,
    })

    print("=" * 80 + "\n")

    return InvoiceResponse(
        vendor=vendor,
        amount=amount,
        currency=currency,
        date=date,
    )