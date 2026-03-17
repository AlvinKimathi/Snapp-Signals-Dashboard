from pathlib import Path
import os
import pandas as pd
import requests
from io import StringIO

# ============================
# PATHS
# ============================
BASE_DIR = Path(r"C:\Users\Admin\OneDrive\Desktop\Projects\Snapp")
CLEAN_DIR = BASE_DIR / "Clean_Data"

FX_PATH = CLEAN_DIR / "fx_monthly.csv"
EPRA_PATH = CLEAN_DIR / "epra_pump_prices.csv"
OUT_PATH = CLEAN_DIR / "energy_stress_index.csv"

# ============================
# HELPERS
# ============================
def _to_num(s):
    return pd.to_numeric(s, errors="coerce")

def normalize(s: pd.Series) -> pd.Series:
    s = _to_num(s)
    if s.dropna().empty:
        return s
    mn, mx = float(s.min()), float(s.max())
    if mx == mn:
        return s * 0
    return (s - mn) / (mx - mn) * 100

def band(x):
    if x < 40:
        return "Low"
    if x < 60:
        return "Moderate"
    if x < 80:
        return "Elevated"
    return "Severe"

# ============================
# BRENT MONTHLY (EIA → FRED fallback)
# ============================
def fetch_brent_monthly():
    eia_key = os.getenv("EIA_API_KEY", "").strip()

    # ---- Try EIA API v2 first
    if eia_key:
        try:
            url = "https://api.eia.gov/v2/petroleum/pri/spt/data/"
            params = {
                "api_key": eia_key,
                "frequency": "monthly",
                "data[0]": "value",
                "facets[series][]": "RBRTE",
                "start": "2000-01",
            }
            r = requests.get(url, params=params, timeout=45)
            if r.ok:
                j = r.json()
                recs = (j.get("response") or {}).get("data") or []
                if recs:
                    df = pd.DataFrame(recs)
                    df["month_key"] = df["period"].astype(str).str.slice(0, 7)
                    df["brent_usd_bbl"] = _to_num(df["value"])
                    out = df.groupby("month_key", as_index=False)["brent_usd_bbl"].mean()
                    if not out.empty:
                        return out
        except Exception:
            pass

    # ---- FRED fallback (no key required)
    fred_csv = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=DCOILBRENTEU"
    r = requests.get(fred_csv, timeout=45)
    r.raise_for_status()

    df = pd.read_csv(StringIO(r.text))
    df.columns = ["date", "brent_usd_bbl"]
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["brent_usd_bbl"] = _to_num(df["brent_usd_bbl"])
    df = df.dropna(subset=["date"]).copy()

    df["month_key"] = df["date"].dt.strftime("%Y-%m")
    return df.groupby("month_key", as_index=False)["brent_usd_bbl"].mean()

# ============================
# LOAD DATA
# ============================
fx = pd.read_csv(FX_PATH)
epra = pd.read_csv(EPRA_PATH)

# ----------------------------
# FX CLEAN (monthly average)
# ----------------------------
fx["date"] = pd.to_datetime(fx["date"], errors="coerce")
fx = fx.dropna(subset=["date"]).copy()

if "United States dollar" not in fx.columns:
    raise ValueError("FX column 'United States dollar' not found.")

fx = fx.rename(columns={"United States dollar": "kes_usd"})
fx["kes_usd"] = _to_num(fx["kes_usd"])
fx["month_key"] = fx["date"].dt.strftime("%Y-%m")

fx_m = fx.groupby("month_key", as_index=False)["kes_usd"].mean()

# ----------------------------
# EPRA CLEAN (Nairobi diesel)
# ----------------------------
epra["cycle_start"] = pd.to_datetime(epra["cycle_start"], errors="coerce")
epra = epra.dropna(subset=["cycle_start"]).copy()

epra["city"] = epra["city"].astype(str).str.strip()
epra_nairobi = epra[epra["city"].str.lower() == "nairobi"].copy()

if epra_nairobi.empty:
    raise ValueError("No Nairobi rows found in EPRA.")

epra_nairobi["diesel"] = _to_num(epra_nairobi["diesel"])
epra_nairobi["month_key"] = epra_nairobi["cycle_start"].dt.strftime("%Y-%m")

epra_m = (
    epra_nairobi.groupby("month_key", as_index=False)["diesel"]
    .mean()
    .rename(columns={"diesel": "diesel_kes_l"})
)

# ----------------------------
# BRENT
# ----------------------------
brent_m = fetch_brent_monthly()

# ============================
# MERGE (EPRA base timeline)
# ============================
df = epra_m.merge(brent_m, on="month_key", how="left")
df = df.merge(fx_m, on="month_key", how="left")

df = df.sort_values("month_key").reset_index(drop=True)

print("\n=== RANGE CHECK ===")
print("EPRA:", df["month_key"].min(), "→", df["month_key"].max())
print("FX:", fx_m["month_key"].min(), "→", fx_m["month_key"].max())
print("Brent:", brent_m["month_key"].min(), "→", brent_m["month_key"].max())

if df["kes_usd"].isna().any():
    missing = df.loc[df["kes_usd"].isna(), "month_key"].tolist()
    raise ValueError("FX missing for months: " + ", ".join(missing))

if df["brent_usd_bbl"].isna().any():
    missing = df.loc[df["brent_usd_bbl"].isna(), "month_key"].tolist()
    raise ValueError("Brent missing for months: " + ", ".join(missing))

# ============================
# 3-MONTH MOMENTUM
# ============================
df["diesel_mom"] = df["diesel_kes_l"].pct_change(3, fill_method=None)
df["fx_mom"] = df["kes_usd"].pct_change(3, fill_method=None)
df["brent_mom"] = df["brent_usd_bbl"].pct_change(3, fill_method=None)

df = df.dropna().reset_index(drop=True)

# ============================
# NORMALIZE
# ============================
df["pump_index"] = normalize(df["diesel_mom"])
df["fx_index"] = normalize(df["fx_mom"])
df["brent_index"] = normalize(df["brent_mom"])

# ============================
# ESI (fixed weights)
# ============================
df["esi_overall"] = (
    0.50 * df["pump_index"] +
    0.30 * df["fx_index"] +
    0.20 * df["brent_index"]
)

df["interpretation_band"] = df["esi_overall"].apply(band)

# ============================
# EXPORT
# ============================
final = df[[
    "month_key",
    "diesel_kes_l",
    "kes_usd",
    "brent_usd_bbl",
    "pump_index",
    "fx_index",
    "brent_index",
    "esi_overall",
    "interpretation_band"
]]

final.to_csv(OUT_PATH, index=False)

print("\n✅ Energy Stress Index generated:", OUT_PATH)
print("Rows exported:", len(final))
print(final.tail(6))
