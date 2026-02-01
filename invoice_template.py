from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

# ---- Font registration ----
FONT_DIR = "fonts"

pdfmetrics.registerFont(
    TTFont("Montserrat", f"{FONT_DIR}/Montserrat-Regular.ttf")
)
pdfmetrics.registerFont(
    TTFont("Montserrat-Bold", f"{FONT_DIR}/Montserrat-Bold.ttf")
)


PAGE_W, PAGE_H = A4  # A4 detected from your sample PDF

def _wrap_text(c, text, font_name, font_size, max_width):
    """Word-wrap text into lines that fit max_width."""
    if not text:
        return []
    words = str(text).replace("\r", "").replace("\n", " ").split()
    lines = []
    cur = ""
    for w in words:
        test = (cur + " " + w).strip()
        if c.stringWidth(test, font_name, font_size) <= max_width:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

def _draw_lines(c, lines, x, y, line_height, font_name, font_size):
    c.setFont(font_name, font_size)
    for line in lines:
        c.drawString(x, y, line)
        y -= line_height
    return y

def _money(v):
    try:
        return f"${float(v):,.2f}"
    except Exception:
        return "" if v is None else str(v)

def draw_invoice(pdf_path: str, data: dict):
    c = canvas.Canvas(pdf_path, pagesize=A4)

    # --- Brand styling ---
    # pylint: disable=invalid-name
    BRAND_BLUE = colors.HexColor("#00A1E0")   # close to your invoice blue
    # pylint: disable=unused-variable
    LIGHT_GRAY = colors.HexColor("#F3F5F7")

    FONT_BOLD = "Montserrat-Bold"
    FONT_REG = "Montserrat"

    # --- Type scale (smaller + cleaner like the reference) ---
    FS_TITLE = 22
    FS_LABEL = 9
    FS_VALUE = 9
    FS_TABLE_HDR = 10
    FS_BODY = 9.5
    FS_TOTALS_LABEL = 10
    FS_TOTALS_VALUE = 10
    FS_GRAND = 11


    margin_x = 0.65 * inch
    right_edge = PAGE_W - margin_x
    top_y = PAGE_H - 0.65 * inch

    logo_path = os.path.join("assets", "logo.png")

    # --- Top bar content: Logo + Company header ---
    logo_w = 3.0 * inch
    logo_h = 3.0 * inch

    if os.path.exists(logo_path):
        try:
            img = ImageReader(logo_path)
            c.drawImage(
                img,
                margin_x,
                PAGE_H - logo_h,
                width=logo_w,
                height=logo_h,
                mask="auto",
                preserveAspectRatio=True
            )
        except Exception:
            pass

    # --- Company address (top-right) ---
    SF_BLUE = colors.HexColor("#00A1E0")  # Salesforce / sky blue

    y_addr = PAGE_H - 1.5 * inch

    # Choose a fixed LEFT start for this block (top-right area)
    addr_x = PAGE_W - 3.0 * inch   # tweak this later if needed

    # Company name in blue (LEFT aligned)
    c.setFont(FONT_BOLD, 10)
    c.setFillColor(SF_BLUE)
    c.drawString(addr_x, y_addr, "Peramal Services LLC")

    # Address in neutral gray (LEFT aligned)
    c.setFont(FONT_REG, 9)
    c.setFillColor(colors.gray)

    y_addr -= 16
    c.drawString(addr_x, y_addr, "13284 Pond Springs Road")
    y_addr -= 14
    c.drawString(addr_x, y_addr, "Suite 501")
    y_addr -= 14
    c.drawString(addr_x, y_addr, "Austin, TX 78729")

    # Reset color for rest of document
    c.setFillColor(colors.black)


    # --- INVOICE title ---
    c.setFont(FONT_BOLD, FS_TITLE)
    c.drawString(margin_x, top_y - 170, "INVOICE")

   # --- Meta lines under INVOICE (left side, like original) ---
    meta_left_x = margin_x
    meta_left_y = top_y - 210  # adjust if you want more/less gap from the title

    c.setFillColor(colors.black)
    c.setFont(FONT_REG, FS_LABEL)

    inv_no = str(data.get("Invoice Num#", "")).strip()
    inv_date = str(data.get("Invoice Date", "")).strip()
    total_due = _money(data.get("Inv Amount", ""))

    c.setFillColor(colors.black)

    c.setFont(FONT_REG, FS_LABEL)
    c.drawString(meta_left_x, meta_left_y, "INVOICE NO      :")
    c.setFont(FONT_BOLD, FS_VALUE)
    c.drawString(meta_left_x + 130, meta_left_y, inv_no)

    # INVOICE DATE
    c.setFont(FONT_REG, FS_LABEL)
    c.drawString(meta_left_x, meta_left_y - 18, "INVOICE DATE    :")
    c.setFont(FONT_BOLD, FS_VALUE)
    c.drawString(meta_left_x + 130, meta_left_y - 18, inv_date)

    # TOTAL DUE
    c.setFont(FONT_REG, FS_LABEL)
    c.drawString(meta_left_x, meta_left_y - 36, "TOTAL DUE       :")
    c.setFont(FONT_BOLD, FS_VALUE)
    c.drawString(meta_left_x + 130, meta_left_y - 36, total_due)


# --- Bill To panel (right) with blue header ---
    panel_w = 3.05 * inch
    panel_x = right_edge - panel_w
    panel_top = top_y - 170
    header_h = 0.32 * inch

    # Header bar
    c.setFillColor(BRAND_BLUE)
    c.rect(panel_x, panel_top - header_h, panel_w, header_h, stroke=0, fill=1)
    c.setFillColor(colors.white)
    c.setFont(FONT_BOLD, FS_VALUE)
    c.drawString(panel_x + 8, panel_top - header_h + 7, "BILL TO")

    # Body box
    body_h = 1.15 * inch
    c.setFillColor(colors.white)
    c.rect(panel_x, panel_top - header_h - body_h, panel_w, body_h, stroke=0, fill=0)

   # --- BILL TO content (Company name + address) ---
    bill_to_raw = str(data.get("Bill to Address", "")).strip()

    lines = [l.strip() for l in bill_to_raw.split("\n") if l.strip()]

    start_y = panel_top - header_h - 14

    # --- BILL TO content (company bold, address below) ---
    if lines:
        c.setFillColor(colors.black)

        full_line = lines[0].strip()

        # Heuristic: company name ends before first digit
        split_idx = None
        for i, ch in enumerate(full_line):
            if ch.isdigit():
                split_idx = i
                break

        if split_idx:
            company = full_line[:split_idx].strip()
            address_part = full_line[split_idx:].strip()
            address_lines = [address_part] + lines[1:]
        else:
            # Fallback: whole line is company name
            company = full_line
            address_lines = lines[1:]

        # Company name (bold, single line, wrapped if needed)
        c.setFont(FONT_BOLD, FS_VALUE)
        company_wrapped = _wrap_text(c, company, FONT_BOLD, FS_VALUE, panel_w - 16)
        for w in company_wrapped:
            c.drawString(panel_x + 8, start_y, w)
            start_y -= 14

        # Address (regular, starts on new line)
        c.setFont(FONT_REG, FS_VALUE)
        for addr_line in address_lines:
            wrapped = _wrap_text(c, addr_line, FONT_REG, FS_VALUE, panel_w - 16)
            for w in wrapped:
                c.drawString(panel_x + 8, start_y, w)
                start_y -= 12


        # Remaining lines = address (regular, wrapped)
        c.setFont(FONT_REG, FS_VALUE)
        for addr_line in lines[1:]:
            wrapped = _wrap_text(c, addr_line, FONT_REG, FS_VALUE, panel_w - 16)
            for w in wrapped:
                c.drawString(panel_x + 8, start_y, w)
                start_y -= 12


    # --- Items table with blue header ---
    table_x = margin_x
    table_w = PAGE_W - 2 * margin_x
    table_top = top_y - 340

    panel_w = 2.95 * inch          # SAME width used for totals panel
    amt_w = panel_w
    desc_w = table_w - amt_w

    row_h = 22

    item_row_h = row_h * 2   # allows 2 lines

    # Table header bar
    c.setFillColor(BRAND_BLUE)
    c.rect(table_x, table_top - row_h, table_w, row_h, stroke=0, fill=1)
    c.setFillColor(colors.white)
    c.setFont(FONT_BOLD, FS_VALUE)
    c.drawString(table_x + 8, table_top - 15, "Item Description")
    c.drawRightString(table_x + desc_w + amt_w - 8, table_top - 15, "Amount")

   # Row box (2-line height, grey background)
    c.setFillColor(LIGHT_GRAY)
    c.rect(
        table_x,
        table_top - row_h - item_row_h,
        table_w,
        item_row_h,
        stroke=1,
        fill=1
    )
    c.setFillColor(colors.black)

    # Vertical divider
    c.line(
        table_x + desc_w,
        table_top - row_h - item_row_h,
        table_x + desc_w,
        table_top - row_h
    )


    c.setFont(FONT_REG, FS_LABEL)
    desc = str(data.get("Description", "")).strip()
    amt = _money(data.get("Inv Amount", ""))
    c.setFillColor(colors.black)
    desc_lines = _wrap_text(
        c,
        desc,
        FONT_REG,
        FS_VALUE,
        desc_w - 16
    )[:2]  # max 2 lines

    y_text = table_top - row_h - 16
    for line in desc_lines:
        c.drawString(table_x + 8, y_text, line)
        y_text -= 12

    amt_y = table_top - row_h - (item_row_h / 2) + 5
    c.setFont(FONT_REG, FS_VALUE)
    c.drawRightString(
        table_x + desc_w + amt_w - 8,
        amt_y,
        amt
    )


    # ===== Single Amount + Totals box (attached to Amount column) =====

    total_amt = _money(data.get("Inv Amount", ""))
    zero_amt = _money(0)

    # Make Amount column width match totals box width
    panel_w = 2.95 * inch  # keep consistent
    amt_w = panel_w
    desc_w = table_w - amt_w  # ensures divider aligns with totals box

    # Amount column starts exactly at the divider
    amt_box_x = table_x + desc_w
    amt_box_w = amt_w

    # Attach directly under the table header area
    amt_box_top = table_top

    # Heights
    hdr_h = row_h          # same as table header height
    amt_row_h = item_row_h      # same as item row height
    break_h = 0.85 * inch  # gray breakdown height
    gt_h = 0.52 * inch     # grand total blue bar height

    total_h = hdr_h + amt_row_h + break_h + gt_h
    amt_box_bottom = amt_box_top - total_h

    # OUTER border (single box)
    c.setStrokeColor(colors.black)
    c.setLineWidth(1)
    c.setFillColor(colors.white)
    c.rect(amt_box_x, amt_box_bottom, amt_box_w, total_h, stroke=1, fill=0)

    # 1) Amount header (blue)
    c.setFillColor(BRAND_BLUE)
    c.rect(amt_box_x, amt_box_top - hdr_h, amt_box_w, hdr_h, stroke=0, fill=1)
    c.setFillColor(colors.white)
    c.setFont(FONT_BOLD, FS_TABLE_HDR)
    c.drawCentredString(amt_box_x + amt_box_w / 2, amt_box_top - hdr_h + 7, "Amount")

    # 2) Amount value row (gray, same as breakdown)
    c.setFillColor(colors.HexColor("#F2F2F2"))
    c.rect(
        amt_box_x,
        amt_box_top - hdr_h - amt_row_h,
        amt_box_w,
        amt_row_h,
        stroke=0,
        fill=1
    )

    c.setFillColor(colors.black)
    c.setFont(FONT_REG, FS_TOTALS_VALUE)
    amt_y = amt_box_top - hdr_h - (amt_row_h / 2) + 5
    c.drawRightString(
        amt_box_x + amt_box_w - 10,
        amt_y,
        total_amt
    )


    # 3) Breakdown area (gray)
    break_top = amt_box_top - hdr_h - amt_row_h
    c.setFillColor(colors.HexColor("#F2F2F2"))
    c.rect(amt_box_x, break_top - break_h, amt_box_w, break_h, stroke=0, fill=1)

    label_x = amt_box_x + 12
    val_x = amt_box_x + amt_box_w - 12
    y0 = break_top - 20

    c.setFillColor(colors.black)

    c.setFont(FONT_BOLD, FS_VALUE)
    c.drawString(label_x, y0, "Sub Total")
    c.setFont(FONT_REG, FS_VALUE)
    c.drawRightString(val_x, y0, total_amt)

    c.setFont(FONT_BOLD, FS_VALUE)
    c.drawString(label_x, y0 - 20, "Tax")
    c.setFont(FONT_REG, FS_VALUE)
    c.drawRightString(val_x, y0 - 20, zero_amt)

    c.setFont(FONT_BOLD, FS_VALUE)
    c.drawString(label_x, y0 - 40, "Previous Due")
    c.setFont(FONT_REG, FS_VALUE)
    c.drawRightString(val_x, y0 - 40, zero_amt)

    # 4) GRAND TOTAL (blue bottom bar)
    gt_y = amt_box_bottom
    c.setFillColor(BRAND_BLUE)
    c.rect(amt_box_x, gt_y, amt_box_w, gt_h, stroke=0, fill=1)

    c.setFillColor(colors.white)
    c.setFont(FONT_BOLD, FS_VALUE)
    c.drawString(label_x, gt_y + 0.16 * inch, "GRAND TOTAL")
    c.drawRightString(val_x, gt_y + 0.16 * inch, total_amt)


    # Reset
    c.setFillColor(colors.black)
    c.setStrokeColor(colors.black)
    c.setLineWidth(1)



    # --- PAYMENT METHOD (bottom left) ---
    pay_y = 4.0 * inch   # moved UP (increase if you want even higher)

    # PAYMENT METHOD title in brand blue
    c.setFillColor(BRAND_BLUE)
    c.setFont(FONT_BOLD, FS_GRAND)
    c.drawString(margin_x, pay_y, "PAYMENT METHOD")

    # By Bank in bold (black)
    c.setFillColor(colors.black)
    c.setFont(FONT_BOLD, 10)
    c.drawString(margin_x, pay_y - 28, "By Bank")

    # Details (regular)
    c.setFont(FONT_REG, 10)
    c.drawString(
        margin_x,
        pay_y - 42,
        "Bank Name & Branch : VERABANK – (TX 78641)"
    )

    c.drawString(
        margin_x,
        pay_y - 58,
        "Account Holder Name : Peramal Services LLC"
    )

    c.drawString(
        margin_x,
        pay_y - 74,
        "Account Number. : 1044100301"
    )

    c.drawString(
        margin_x,
        pay_y - 88,
        "Routing Number : 111903151"
    )

    # Reset color
    c.setFillColor(colors.black)


    # --- Thank you message (below PAYMENT METHOD) ---
    thank_y = pay_y - 140   # spacing below payment block (adjust if needed)

    c.setFont(FONT_BOLD, 12)
    c.setFillColor(BRAND_BLUE)
    c.drawString(margin_x, thank_y, "Thank you for your business!")

    c.setFont(FONT_REG, 9)
    c.setFillColor(colors.gray)
    c.drawString(
        margin_x,
        thank_y - 18,
        "If you have any queries regarding this invoice,"
    )
    c.drawString(
        margin_x,
        thank_y - 32,
        "please reach us at accounts@peramalservices.com"
    )

    # Reset color
    c.setFillColor(colors.black)


# --- Bottom blue stripe ---
    c.setFillColor(BRAND_BLUE)
    c.rect(0, 0, PAGE_W, 0.18 * inch, stroke=0, fill=1)

    c.showPage()
    c.save()
