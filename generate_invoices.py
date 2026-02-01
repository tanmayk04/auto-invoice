import os
import re
import pandas as pd

from invoice_template import draw_invoice  # uses your existing template


EXCEL_PATH = "input/Invoice_Upload.xlsx"
OUT_DIR = "output/invoices"


def _safe_filename(s: str) -> str:
    s = str(s).strip()
    s = re.sub(r"[^\w\- ]+", "", s)  # remove weird chars
    s = re.sub(r"\s+", "_", s)
    return s[:80] if s else "invoice"


def _fmt_date(v) -> str:
    if pd.isna(v):
        return ""
    try:
        dt = pd.to_datetime(v)
        return dt.strftime("%b %d, %Y")  # Dec 01, 2025
    except Exception:
        return str(v)


def _fmt_month(row) -> str:
    # Prefer Month Name column if it’s actually text
    m = row.get("Month Name", "")
    if isinstance(m, str) and m.strip():
        return m.strip()

    # If Month Name is a date/timestamp (like your file), derive from Invoice Date
    inv_date = row.get("Invoice Date", "")
    try:
        dt = pd.to_datetime(inv_date)
        return dt.strftime("%b %Y")  # Nov 2025
    except Exception:
        return ""


def _fmt_number_string(v) -> str:
    # For account/routing numbers coming as floats, convert safely
    if pd.isna(v):
        return ""
    try:
        # handle floats like 1044100301.0
        if isinstance(v, float):
            return str(int(v))
        return str(v).strip()
    except Exception:
        return str(v).strip()


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    df = pd.read_excel(EXCEL_PATH, header=2)
    df = df.loc[:, ~df.columns.str.contains("^Unnamed")]

    count = 0

    for _, r in df.iterrows():
        row = r.to_dict()

        # Normalize / format fields expected by your template
        row["Invoice Date"] = _fmt_date(row.get("Invoice Date", ""))
        row["Month Name"] = _fmt_month(row)
        row["Account Number"] = _fmt_number_string(row.get("Account Number", ""))
        row["Routing Number"] = _fmt_number_string(row.get("Routing Number", ""))

        inv_no = _fmt_number_string(row.get("Invoice Num#", ""))
        vendor = row.get("Vendor Name", "")

        filename = f"{inv_no}_{_safe_filename(vendor)}.pdf"
        out_path = os.path.join(OUT_DIR, filename)

        draw_invoice(out_path, row)
        count += 1

    print(f"✅ Generated {count} invoices in: {OUT_DIR}")


if __name__ == "__main__":
    main()
