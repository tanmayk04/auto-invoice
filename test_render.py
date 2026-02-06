import os
from invoice_template import draw_invoice

os.makedirs("output/invoices", exist_ok=True)

sample = {
    "Vendor Name": "Jacent",
    "Project Name": "Dell Boomi",
    "Invoice Num#": "1322",
    "Invoice Date": "2025-12-30",
    "Month Name": "Nov 2025",
    "Description": "Professional Services - Integration Support",
    "Bill to Address": "Dell Technologies\n1 Dell Way\nRound Rock, TX 78682",
    "Bill from Address": "Jacent Strategic Merchandising\n123 Vendor St\nChicago, IL 60601",
    "Inv Amount": 2500.00,
    "Vendor Email ID": "billing@jacent.com",
    "Bank Name & Branch": "Bank of America - Downtown Branch",
    "Account Holder Name": "Jacent Strategic Merchandising",
    "Account Number": "1234567890",
    "Routing Number": "111000025",
}

draw_invoice("output/invoices/_sample_invoice.pdf", sample)
print("✅ Generated: output/invoices/_sample_invoice.pdf")
