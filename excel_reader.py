import pandas as pd

EXCEL_PATH = "input/Invoice_Upload.xlsx"

df = pd.read_excel(EXCEL_PATH, header=2)

# Drop the first empty column if it exists
df = df.loc[:, ~df.columns.str.contains("^Unnamed")]

print("Columns found:")
print(list(df.columns))

print("\nFirst row:")
print(df.iloc[0].to_dict())
