from pathlib import Path
import pandas as pd
import re

# PATHS
BASE_DIR = Path(r"C:\Users\Admin\OneDrive\Desktop\Projects\Snapp")
RAW_DIR = BASE_DIR / "Raw_Data"
CLEAN_DIR = BASE_DIR / "Clean_Data"
RAW_DIR.mkdir(parents=True, exist_ok=True)
CLEAN_DIR.mkdir(parents=True, exist_ok=True)
XLSX_PATH = RAW_DIR / "Chapter-13-Transportation-and-Storage.xlsx"

# HELPERS
def clean_year(col):
    """Convert 2020.0 / '2024*' / '2020/21' -> numeric year where possible."""
    if pd.isna(col):
        return None

    # Handles numeric years coming as floats (e.g. 2020.0)
    if isinstance(col, (int, float)):
        y = int(col)
        if 1900 <= y <= 2100:
            return y

    s = str(col).strip()

    # Financial year (e.g. 2020/21) -> take first year
    if "/" in s:
        s = s.split("/")[0]

    # Remove everything except digits (e.g. 2024* -> 2024)
    s = re.sub(r"[^0-9]", "", s)

    return int(s) if s.isdigit() else None


def to_number(x):
    if pd.isna(x):
        return pd.NA
    s = str(x).strip()
    s = s.replace(",", "")
    s = re.sub(r"\s+", "", s)
    if s in ["", ".", "..", "…", "nan", "None", "-", "—"]:
        return pd.NA
    return pd.to_numeric(s, errors="coerce")


# ============================================================
# ROAD TRAFFIC ACCIDENTS & PERSONS KILLED/INJURED (Table 13.6a)
# ============================================================
df_136a_raw = pd.read_excel(XLSX_PATH, sheet_name="Table 13.6(a)", header=None)

header_row = None
target_years = {2020, 2021, 2022, 2023, 2024}

for i in range(min(60, len(df_136a_raw))):
    row_vals = df_136a_raw.iloc[i].tolist()

    # year signals
    years_found = {clean_year(v) for v in row_vals}
    years_found = {y for y in years_found if y in target_years}

    # text signals (stable anchor)
    row_text = " ".join([str(v).lower() for v in row_vals if pd.notna(v)])
    has_reported = ("reported" in row_text) or ("traffic accidents" in row_text)

    if len(years_found) >= 4 or (has_reported and len(years_found) >= 3):
        header_row = i
        break

if header_row is None:
    print(df_136a_raw.head(15))
    raise ValueError("Could not detect header row for Table 13.6(a)")

df_136a = pd.read_excel(XLSX_PATH, sheet_name="Table 13.6(a)", header=header_row)
df_136a = df_136a.dropna(how="all")

# rename first col
first_col = df_136a.columns[0]
df_136a = df_136a.rename(columns={first_col: "Metric"})

# clean year column names
new_cols = {}
for c in df_136a.columns:
    if c == "Metric":
        new_cols[c] = "Metric"
    else:
        y = clean_year(c)
        new_cols[c] = y if y else c
df_136a = df_136a.rename(columns=new_cols)

year_cols = [c for c in df_136a.columns if isinstance(c, int)]
df_136a = df_136a[["Metric"] + year_cols]

# numeric cleanup
for c in year_cols:
    df_136a[c] = df_136a[c].apply(to_number)

df_136a["Metric"] = df_136a["Metric"].astype(str).str.strip()
df_136a = df_136a[df_136a["Metric"].str.lower().ne("nan")]

# Drop note/source rows if present
drop_mask = df_136a["Metric"].str.lower().str.contains(r"source|provisional", na=False)
df_136a = df_136a[~drop_mask]

accidents_clean_path = CLEAN_DIR / "knbs_road_accidents_summary.csv"
df_136a.to_csv(accidents_clean_path, index=False)
print("Saved:", accidents_clean_path)


# ============================================================
# ROAD ACCIDENT CASUALTIES BY TYPE & CLASS (Table 13.6b)
# ============================================================
df_136b_raw = pd.read_excel(XLSX_PATH, sheet_name="Table 13.6(b)", header=None)

header_row = None
for i in range(min(80, len(df_136b_raw))):
    row_vals = df_136b_raw.iloc[i].tolist()
    row_text = " ".join([str(v).lower() for v in row_vals if pd.notna(v)])

    years_found = {clean_year(v) for v in row_vals}
    years_found = {y for y in years_found if y in target_years}

    # This sheet has explicit headers: "Type", "Class", then years
    has_type = "type" in row_text
    has_class = "class" in row_text

    if has_type and has_class and len(years_found) >= 3:
        header_row = i
        break

if header_row is None:
    print(df_136b_raw.head(20))
    raise ValueError("Could not detect header row for Table 13.6(b)")

df_136b = pd.read_excel(XLSX_PATH, sheet_name="Table 13.6(b)", header=header_row)
df_136b = df_136b.dropna(how="all")

# Normalize first 2 columns names (they should already be Type/Class)
cols = list(df_136b.columns)
cols[0] = "Type"
cols[1] = "Class"
df_136b.columns = cols

# Clean year columns
new_cols = {}
for c in df_136b.columns:
    if c in ["Type", "Class"]:
        new_cols[c] = c
    else:
        y = clean_year(c)
        new_cols[c] = y if y else c
df_136b = df_136b.rename(columns=new_cols)

year_cols = [c for c in df_136b.columns if isinstance(c, int)]
df_136b = df_136b[["Type", "Class"] + year_cols]

# Forward-fill Type (since group headers like Pedestrians appear once)
df_136b["Type"] = df_136b["Type"].ffill()

# Clean text columns
df_136b["Type"] = df_136b["Type"].astype(str).str.strip()
df_136b["Class"] = df_136b["Class"].astype(str).str.strip()

# Remove sub-totals (recommended for cleaner charts)
df_136b = df_136b[~df_136b["Class"].str.lower().str.contains("sub-total|subtotal", na=False)]

# Numeric cleanup
for c in year_cols:
    df_136b[c] = df_136b[c].apply(to_number)

# Drop blanks
df_136b = df_136b[df_136b["Type"].str.lower().ne("nan")]
df_136b = df_136b[df_136b["Class"].str.lower().ne("nan")]

accidents_b_clean_path = CLEAN_DIR / "knbs_road_accidents_by_type_class.csv"
df_136b.to_csv(accidents_b_clean_path, index=False)
print("Saved:", accidents_b_clean_path)
