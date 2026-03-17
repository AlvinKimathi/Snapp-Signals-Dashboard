from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

BASE_DIR = Path(r"C:\Users\Admin\OneDrive\Desktop\Projects\Snapp")
CLEAN_DIR = BASE_DIR / "Clean_Data"
OUT_DIR = BASE_DIR / "Output" / "Charts"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Load clean datasets
fx = pd.read_csv(CLEAN_DIR / "fx_monthly.csv")
rates = pd.read_csv(CLEAN_DIR / "cbk_rates.csv")
cpi=pd.read_csv(CLEAN_DIR / "cpi_inflation.csv")


fx["date"] = pd.to_datetime(fx["date"])
rates["date"] = pd.to_datetime(rates["date"])
cpi["date"] = pd.to_datetime(cpi["date"])

# FX (KES/USD)
plt.figure(figsize=(10, 5))
plt.plot(fx["date"], fx["United States dollar"])
plt.title("KES/USD Trend (Monthly Average)")
plt.xlabel("Date")
plt.ylabel("KES per USD")
plt.grid(True)
plt.tight_layout()
plt.savefig(OUT_DIR / "week1_fx_kes_usd.png", dpi=200)
plt.close()

# Central Bank Rate
if "Central Bank Rate" in rates.columns:
    plt.figure(figsize=(10, 5))
    plt.plot(rates["date"], rates["Central Bank Rate"])
    plt.title("Central Bank Rate (CBR) Trend")
    plt.xlabel("Date")
    plt.ylabel("Rate (%)")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(OUT_DIR / "week1_cbr_trend.png", dpi=200)
    plt.close()

# 91-Day T-bill
if "91-Day Tbill" in rates.columns:
    plt.figure(figsize=(10, 5))
    plt.plot(rates["date"], rates["91-Day Tbill"])
    plt.title("91-Day Treasury Bill Trend")
    plt.xlabel("Date")
    plt.ylabel("Rate (%)")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(OUT_DIR / "week1_91day_tbill_trend.png", dpi=200)
    plt.close()
    
# CPI / Inflation (12-Month)
plt.figure(figsize=(10, 5))
plt.plot(cpi["date"], cpi["12-Month Inflation"])
plt.title("Inflation Trend (12-Month)")
plt.xlabel("Date")
plt.ylabel("Inflation (%)")
plt.grid(True)
plt.tight_layout()
plt.savefig(OUT_DIR / "week1_inflation_trend.png", dpi=200)
plt.close()


print("✅ Charts saved to:", OUT_DIR)
