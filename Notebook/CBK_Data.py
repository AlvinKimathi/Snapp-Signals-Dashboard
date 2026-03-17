from pathlib import Path
import pandas as pd

# Filepath
BASE_DIR = Path(r"C:\Users\Admin\OneDrive\Desktop\Projects\Snapp")
RAW_DIR = BASE_DIR / "Raw_Data"
CLEAN_DIR = BASE_DIR / "Clean_Data"
RAW_DIR.mkdir(parents=True, exist_ok=True)
CLEAN_DIR.mkdir(parents=True, exist_ok=True)

# URLS
EXCHANGE_RATE_CSV = "https://www.centralbank.go.ke/uploads/exchange_rates/1775061450_Monthly%20Exchange%20rate%20%28period%20average%29.csv"
CBK_RATES_CSV = "https://www.centralbank.go.ke/uploads/interest_rates/410481034_Central%20Bank%20Rates.csv"
INFLATION_RATES_CSV = Path(r"C:\Users\Admin\Downloads\Inflation Rates.csv")


# FX Cleaning
df_fx = pd.read_csv(EXCHANGE_RATE_CSV)

if "Month" not in df_fx.columns and "MONTH" not in df_fx.columns:
    df_fx = pd.read_csv(EXCHANGE_RATE_CSV, skiprows=1)

# Save raw
fx_raw_path = RAW_DIR / "cbk_monthly_exchange_rate_period_average.csv"
df_fx.to_csv(fx_raw_path, index=False)
print("Saved raw FX:", fx_raw_path)

# Clean
df_fx.columns = [str(c).strip().replace("\n", " ") for c in df_fx.columns]
df_fx = df_fx.rename(columns={"YEAR": "Year", "MONTH": "Month", "year": "Year", "month": "Month"})

df_fx["Year"] = pd.to_numeric(df_fx["Year"], errors="coerce").astype("Int64")
df_fx["Month"] = pd.to_numeric(df_fx["Month"], errors="coerce").astype("Int64")
df_fx["date"] = pd.to_datetime(df_fx["Year"].astype(str) + "-" + df_fx["Month"].astype(str) + "-01", errors="coerce")

# Convert currencies to numeric
for c in df_fx.columns:
    if c not in ["Year", "Month", "date"]:
        df_fx[c] = pd.to_numeric(df_fx[c], errors="coerce")

fx_cols = [c for c in ["date", "Year", "Month", "United States dollar", "Euro", "Sterling pound"] if c in df_fx.columns]
df_fx_clean = df_fx[fx_cols].dropna(subset=["date"]).sort_values("date")

fx_clean_path = CLEAN_DIR / "fx_monthly.csv"
df_fx_clean.to_csv(fx_clean_path, index=False)
print("Saved clean FX:", fx_clean_path)


# Rates Cleaning
df_rates = pd.read_csv(CBK_RATES_CSV)

# Same issue: sometimes a title row exists
if "MONTH" not in df_rates.columns and "Month" not in df_rates.columns:
    df_rates = pd.read_csv(CBK_RATES_CSV, skiprows=1)

# Save raw
rates_raw_path = RAW_DIR / "cbk_central_bank_rates.csv"
df_rates.to_csv(rates_raw_path, index=False)
print("Saved raw Rates:", rates_raw_path)

# Clean
df_rates.columns = [str(c).strip().replace("\n", " ") for c in df_rates.columns]
df_rates = df_rates.rename(columns={"year": "YEAR", "month": "MONTH", "Year": "YEAR", "Month": "MONTH"})

# YEAR often blank for some rows -> forward fill
df_rates["YEAR"] = df_rates["YEAR"].replace(r"^\s*$", pd.NA, regex=True).ffill()
df_rates["YEAR"] = pd.to_numeric(df_rates["YEAR"], errors="coerce").astype("Int64")
df_rates["MONTH"] = df_rates["MONTH"].astype(str).str.strip()

# Convert numeric columns safely
for c in df_rates.columns:
    if c not in ["YEAR", "MONTH"]:
        df_rates[c] = (
            df_rates[c]
            .astype(str)
            .str.replace(",", "", regex=False)
            .str.replace(r"\s+", "", regex=True)
            .replace({"-": pd.NA, "": pd.NA, "nan": pd.NA})
        )
        df_rates[c] = pd.to_numeric(df_rates[c], errors="coerce")

df_rates["date"] = pd.to_datetime(
    df_rates["YEAR"].astype(str) + "-" + df_rates["MONTH"] + "-01",
    format="%Y-%b-%d",
    errors="coerce"
)

wanted = ["date", "YEAR", "MONTH", "Interbank Rate", "91-Day Tbill", "182-days Tbill", "364-days Tbill", "Central Bank Rate"]
rate_cols = [c for c in wanted if c in df_rates.columns]

df_rates_clean = df_rates[rate_cols].dropna(subset=["date"]).sort_values("date")

rates_clean_path = CLEAN_DIR / "cbk_rates.csv"
df_rates_clean.to_csv(rates_clean_path, index=False)
print("Saved clean Rates:", rates_clean_path)

#CPI / INFLATION
df_cpi = pd.read_csv(INFLATION_RATES_CSV)

# Save raw copy 
cpi_raw_path = RAW_DIR / "cbk_inflation_rates.csv"
df_cpi.to_csv(cpi_raw_path, index=False)
print("Saved raw CPI:", cpi_raw_path)

# Clean (minimal)
df_cpi.columns = [str(c).strip().replace("\n", " ") for c in df_cpi.columns]

df_cpi["Year"] = pd.to_numeric(df_cpi["Year"], errors="coerce").astype("Int64")
df_cpi["Month"] = df_cpi["Month"].astype(str).str.strip()

# Month is full name e.g., "December"
df_cpi["date"] = pd.to_datetime(
    df_cpi["Year"].astype(str) + "-" + df_cpi["Month"] + "-01",
    format="%Y-%B-%d",
    errors="coerce"
)

df_cpi["Annual Average Inflation"] = pd.to_numeric(df_cpi["Annual Average Inflation"], errors="coerce")
df_cpi["12-Month Inflation"] = pd.to_numeric(df_cpi["12-Month Inflation"], errors="coerce")

df_cpi_clean = df_cpi.dropna(subset=["date"]).sort_values("date")

cpi_clean_path = CLEAN_DIR / "cpi_inflation.csv"
df_cpi_clean.to_csv(cpi_clean_path, index=False)
print("Saved clean CPI:", cpi_clean_path)

