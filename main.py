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

    text = req.text

    if not text.strip():
        return InvoiceResponse(
            vendor="",
            amount=0,
            currency="",
            date=""
        )

    # ---------- Currency ----------
    currency_match = re.search(r"\b(USD|EUR|GBP)\b", text, re.IGNORECASE)
    currency = currency_match.group(1).upper() if currency_match else ""

    # ---------- Date ----------
    date_match = re.search(r"2026-\d{2}-\d{2}", text)
    date = date_match.group(0) if date_match else ""

    # ---------- Amount ----------
    amount = 0.0

    amount_patterns = [
        r"Grand Total[:\s]*\$?([0-9]+(?:\.[0-9]{1,2})?)",
        r"Total Due[:\s]*\$?([0-9]+(?:\.[0-9]{1,2})?)",
        r"Amount Due[:\s]*\$?([0-9]+(?:\.[0-9]{1,2})?)",
        r"Amount[:\s]*\$?([0-9]+(?:\.[0-9]{1,2})?)",
        r"Total[:\s]*\$?([0-9]+(?:\.[0-9]{1,2})?)",
        r"\b([0-9]+(?:\.[0-9]{1,2})?)\s*(USD|EUR|GBP)\b",
    ]

    for pattern in amount_patterns:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            amount = float(m.group(1))
            break

    # ---------- Vendor ----------
        # ---------- Vendor ----------
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

    return InvoiceResponse(
        vendor=vendor,
        amount=amount,
        currency=currency,
        date=date,
    )