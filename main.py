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

    # Grab every number in the document
    numbers = re.findall(r"\d+(?:\.\d+)?", text)

    print("Numbers found:", numbers)

    candidates = []

    for n in numbers:
        try:
            value = float(n)

            # Ignore date pieces
            if value == 2026:
                continue

            candidates.append(value)

        except Exception:
            pass

    print("Candidate amounts:", candidates)

    if candidates:
        amount = max(candidates)

    # ---------------- Vendor ----------------

    vendor = ""

    vendor_patterns = [
        r"Vendor[:\s]*(.+)",
        r"Supplier[:\s]*(.+)",
        r"Invoice From[:\s]*(.+)",
        r"From[:\s]*(.+)",
        r"Issuer[:\s]*(.+)",
    ]

    for pattern in vendor_patterns:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            vendor = m.group(1).split("\n")[0].strip()
            break

    if not vendor:
        lines = [l.strip() for l in text.splitlines() if l.strip()]
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