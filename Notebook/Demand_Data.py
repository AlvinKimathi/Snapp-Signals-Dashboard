from __future__ import annotations

from pathlib import Path
import time
import pandas as pd
import requests


# ============================================================
# PATHS
# ============================================================
BASE_DIR = Path(r"C:\Users\Admin\OneDrive\Desktop\Projects\Snapp")
RAW_DIR = BASE_DIR / "Raw_Data"
CLEAN_DIR = BASE_DIR / "Clean_Data"

RAW_DIR.mkdir(parents=True, exist_ok=True)
CLEAN_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# UTILS
# ============================================================
def _safe_to_numeric(s):
    return pd.to_numeric(s, errors="coerce")


def normalize_0_100(s: pd.Series) -> pd.Series:
    """
    Normalize a series to 0–100 scale (good for index-like charts).
    """
    s = _safe_to_numeric(s)
    if s.dropna().empty:
        return s
    mn, mx = float(s.min()), float(s.max())
    if mx == mn:
        return s * 0
    return (s - mn) / (mx - mn) * 100


def _latest_matching_file(folder: Path, pattern: str) -> Path | None:
    files = sorted(folder.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)
    return files[0] if files else None


# ============================================================
# GOOGLE TRENDS (LOCAL ONLY) ✅ NO SCRAPING
# ============================================================
def build_trends_clean_from_local(local_df: pd.DataFrame) -> pd.DataFrame:
    """
    Accepts a local trends CSV that is either:
    A) Already CLEAN (has *_index columns) -> returns it (numeric coerced)
    B) TRUE RAW (date + keyword columns) -> computes *_index columns and returns clean
    """
    baskets = {
        "household_stress": ["unga", "maize flour", "fuel price", "rent", "loan"],
        "digital_spend": ["internet bundles", "safaricom bundles", "smartphone price", "laptop price"],
        "jobs_interest": ["jobs in kenya", "vacancies", "BrighterMonday"],
    }
    expected_index_cols = {f"{b}_index" for b in baskets.keys()}

    df = local_df.copy()

    # Ensure date column exists
    if "date" not in df.columns:
        df = df.rename(columns={df.columns[0]: "date"})

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"]).sort_values("date").reset_index(drop=True)

    # If already CLEAN, return as-is (numeric coercion)
    if set(df.columns).intersection(expected_index_cols):
        for c in df.columns:
            if c != "date":
                df[c] = _safe_to_numeric(df[c])
        return df

    # Otherwise compute indices from keyword columns (TRUE RAW)
    out = pd.DataFrame({"date": df["date"]})

    for basket, kws in baskets.items():
        cols = [c for c in kws if c in df.columns]
        if not cols:
            out[f"{basket}_index"] = pd.NA
            continue
        raw_idx = df[cols].apply(_safe_to_numeric).mean(axis=1)
        out[f"{basket}_index"] = normalize_0_100(raw_idx)

    # Keep keyword columns if present
    all_keywords = []
    for v in baskets.values():
        all_keywords.extend(v)
    all_keywords = list(dict.fromkeys(all_keywords))

    for k in all_keywords:
        if k in df.columns:
            out[k] = _safe_to_numeric(df[k])

    return out


def load_trends_local() -> pd.DataFrame:
    """
    Loads trends ONLY from local files in Raw_Data:
      - Raw_Data/demand_google_trends_raw.csv  (preferred)
      - else latest Raw_Data/demand_google_trends_raw*.csv

    Returns a CLEAN trends dataframe.
    """
    preferred = RAW_DIR / "demand_google_trends_raw.csv"
    if preferred.exists():
        df = pd.read_csv(preferred)
        return build_trends_clean_from_local(df)

    latest = _latest_matching_file(RAW_DIR, "demand_google_trends_raw*.csv")
    if latest is None:
        return pd.DataFrame()

    df = pd.read_csv(latest)
    return build_trends_clean_from_local(df)


# ============================================================
# WORLD BANK (STRUCTURAL CONTEXT) ✅ aligned + safe
# ============================================================
def _wb_get_json(country_code: str, indicator_code: str, session: requests.Session) -> list | None:
    """
    Fetch JSON from World Bank safely:
    - retries on transient errors
    - returns parsed JSON or None
    - does NOT raise
    """
    url = f"https://api.worldbank.org/v2/country/{country_code}/indicator/{indicator_code}"
    params = {"format": "json", "per_page": 2000}

    last_err = None
    for attempt in range(1, 4):
        try:
            r = session.get(url, params=params, timeout=30)

            # transient server/rate issues
            if r.status_code in (429, 500, 502, 503, 504):
                time.sleep(1.2 * attempt)
                continue

            if r.status_code != 200:
                last_err = f"HTTP {r.status_code}: {r.text[:120]}"
                break

            return r.json()

        except Exception as e:
            last_err = str(e)
            time.sleep(1.2 * attempt)

    if last_err:
        print(f"[WARN] World Bank fetch failed: {country_code} {indicator_code} -> {last_err}")
    return None


def fetch_worldbank_indicators() -> pd.DataFrame:
    """
    Fetch annual World Bank indicators for Kenya (KE) using the World Bank API.

    Output tidy table:
      year, indicator, value
    """
    indicators = {
        "unemployment_total_pct": "SL.UEM.TOTL.ZS",
        "unemployment_youth_pct": "SL.UEM.1524.ZS",
        "private_consumption_growth_pct": "NE.CON.PRVT.KD.ZG",
        "gdp_growth_pct": "NY.GDP.MKTP.KD.ZG",
    }

    rows = []
    session = requests.Session()
    session.headers.update({"User-Agent": "SnappSignals/1.0"})

    # Try both ISO2 + ISO3
    country_try = ["KE", "KEN"]

    for friendly, code in indicators.items():
        data = None
        for cc in country_try:
            data = _wb_get_json(cc, code, session)
            if data:
                break

        if not isinstance(data, list) or len(data) < 2 or data[1] is None:
            print(f"[WARN] World Bank returned empty/invalid for {friendly} ({code}). Skipping.")
            continue

        for obs in data[1]:
            year = obs.get("date")
            val = obs.get("value")
            if year is None:
                continue

            rows.append(
                {
                    "year": pd.to_numeric(year, errors="coerce"),
                    "indicator": friendly,
                    "value": pd.to_numeric(val, errors="coerce"),
                }
            )

    df = pd.DataFrame(rows)
    df = df.dropna(subset=["year"]).sort_values(["indicator", "year"]).reset_index(drop=True)
    return df


# ============================================================
# ✅ NEW: WORLD BANK REGIONAL CONTEXT (KE + RW + TZ + ET)
# ============================================================
def fetch_worldbank_regional_context() -> pd.DataFrame:
    """
    Fetch the SAME demand-context indicators for:
      Kenya (KE), Rwanda (RW), Tanzania (TZ), Ethiopia (ET)

    Output tidy table:
      year, country, indicator, value
    """
    indicators = {
        "unemployment_total_pct": "SL.UEM.TOTL.ZS",
        "unemployment_youth_pct": "SL.UEM.1524.ZS",
        "private_consumption_growth_pct": "NE.CON.PRVT.KD.ZG",
        "gdp_growth_pct": "NY.GDP.MKTP.KD.ZG",
    }

    countries = {
        "Kenya": ["KE", "KEN"],
        "Rwanda": ["RW", "RWA"],
        "Tanzania": ["TZ", "TZA"],
        "Ethiopia": ["ET", "ETH"],
    }

    rows = []
    session = requests.Session()
    session.headers.update({"User-Agent": "SnappSignals/1.0"})

    for country_name, code_try in countries.items():
        for friendly, indicator_code in indicators.items():
            data = None
            for cc in code_try:
                data = _wb_get_json(cc, indicator_code, session)
                if data:
                    break

            if not isinstance(data, list) or len(data) < 2 or data[1] is None:
                print(f"[WARN] WB regional empty/invalid: {country_name} {friendly} ({indicator_code})")
                continue

            for obs in data[1]:
                year = obs.get("date")
                val = obs.get("value")
                if year is None:
                    continue

                rows.append(
                    {
                        "year": pd.to_numeric(year, errors="coerce"),
                        "country": country_name,
                        "indicator": friendly,
                        "value": pd.to_numeric(val, errors="coerce"),
                    }
                )

    df = pd.DataFrame(rows)
    df = df.dropna(subset=["year"]).sort_values(["country", "indicator", "year"]).reset_index(drop=True)
    return df


# ============================================================
# EPRA (COST PRESSURE PROXY) - CSV FIRST
# ============================================================
def load_epra_from_csv() -> pd.DataFrame:
    """
    Loads EPRA pump prices from a manually downloaded CSV in Raw_Data.

    Expected location:
      Raw_Data/epra_pump_prices_raw.csv

    Output columns:
      cycle_start, cycle_end, city, super_petrol, diesel, kerosene
    """
    raw_path = RAW_DIR / "epra_pump_prices_raw.csv"
    if not raw_path.exists():
        return pd.DataFrame()

    df = pd.read_csv(raw_path)

    # Normalize columns
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    # Map likely EPRA names
    rename_map = {}
    for c in df.columns:
        cl = c.lower()

        if "town" in cl or "city" in cl or "location" in cl:
            rename_map[c] = "city"
        elif "super" in cl or "petrol" in cl or "pms" in cl:
            rename_map[c] = "super_petrol"
        elif "diesel" in cl or "ago" in cl:
            rename_map[c] = "diesel"
        elif "keros" in cl or "dpk" in cl:
            rename_map[c] = "kerosene"
        elif "cycle_start" in cl or "start" in cl or "effective_from" in cl or "from" == cl:
            rename_map[c] = "cycle_start"
        elif "cycle_end" in cl or "end" in cl or "effective_to" in cl or "to" == cl:
            rename_map[c] = "cycle_end"

    df = df.rename(columns=rename_map)

    # Keep only expected columns if present
    keep = [c for c in ["cycle_start", "cycle_end", "city", "super_petrol", "diesel", "kerosene"] if c in df.columns]
    df = df[keep].copy()

    # Dates (EPRA commonly uses day-first dates)
    if "cycle_start" in df.columns:
        df["cycle_start"] = pd.to_datetime(df["cycle_start"], errors="coerce", dayfirst=True)
    if "cycle_end" in df.columns:
        df["cycle_end"] = pd.to_datetime(df["cycle_end"], errors="coerce", dayfirst=True)

    # Prices
    for c in ["super_petrol", "diesel", "kerosene"]:
        if c in df.columns:
            df[c] = (
                df[c].astype(str)
                .str.replace(",", "", regex=False)
                .str.extract(r"(\d+(\.\d+)?)", expand=False)[0]
            )
            df[c] = pd.to_numeric(df[c], errors="coerce")

    # Basic cleaning
    if "city" in df.columns:
        df["city"] = df["city"].astype(str).str.strip()

    df = df.dropna(subset=["city"], how="any").reset_index(drop=True)
    return df


# ============================================================
# PIPELINE RUNNER
# ============================================================
def main():
    print("=== DEMAND PROXIES PIPELINE ===")

    # ----------------------------
    # 1) Google Trends (LOCAL ONLY) ✅
    # ----------------------------
    clean_trends_path = CLEAN_DIR / "demand_google_trends.csv"

    trends_local = load_trends_local()
    if trends_local.empty:
        print("[WARN] Local Google Trends file not found/empty.")
        print("       Put your local copy here:")
        print(f"       {RAW_DIR / 'demand_google_trends_raw.csv'}")
    else:
        trends_local.to_csv(clean_trends_path, index=False)
        print(f"[OK] Saved: {clean_trends_path}")

    # ----------------------------
    # 2) World Bank indicators (Kenya-only)
    # ----------------------------
    wb = fetch_worldbank_indicators()
    if wb.empty:
        print("[WARN] World Bank returned empty.")
    else:
        raw_wb_path = RAW_DIR / "worldbank_demand_context_raw.csv"
        clean_wb_path = CLEAN_DIR / "worldbank_demand_context.csv"
        wb.to_csv(raw_wb_path, index=False)

        pivot = wb.pivot_table(index="year", columns="indicator", values="value", aggfunc="mean").reset_index()
        pivot = pivot.sort_values("year")
        pivot.to_csv(clean_wb_path, index=False)

        print(f"[OK] Saved: {raw_wb_path}")
        print(f"[OK] Saved: {clean_wb_path}")

       # ----------------------------
    # ✅ 2B) World Bank REGIONAL context (KE + RW + TZ + ET)
    # ----------------------------
    wb_reg = fetch_worldbank_regional_context()

    if wb_reg.empty:
        print("[WARN] World Bank REGIONAL returned empty.")
    else:
        raw_reg_path = RAW_DIR / "worldbank_regional_context_raw.csv"
        clean_reg_path = CLEAN_DIR / "worldbank_regional_context.csv"

        wb_reg.to_csv(raw_reg_path, index=False)

        # ---- PIVOT ----
        wide = wb_reg.pivot_table(
            index="year",
            columns=["country", "indicator"],
            values="value",
            aggfunc="mean",
        )

        # Reset index safely
        wide = wide.reset_index()

        # ---- FORCE SIMPLE COLUMN NAMES ----
        # If columns are MultiIndex, flatten them properly
        if isinstance(wide.columns, pd.MultiIndex):
            wide.columns = [
                "year" if col[0] == "year" else f"{col[0]} | {col[1]}"
                for col in wide.columns
            ]
        else:
            # If not MultiIndex but year missing, force rename first column
            if "year" not in wide.columns:
                wide = wide.rename(columns={wide.columns[0]: "year"})

        # Ensure year column exists
        if "year" not in wide.columns:
            wide.insert(0, "year", wb_reg["year"].unique())

        wide["year"] = pd.to_numeric(wide["year"], errors="coerce")
        wide = wide.dropna(subset=["year"]).sort_values("year")

        wide.to_csv(clean_reg_path, index=False)

        print(f"[OK] Saved: {raw_reg_path}")
        print(f"[OK] Saved: {clean_reg_path}")


    # ----------------------------
    # 3) EPRA pump prices
    # ----------------------------
    epra = load_epra_from_csv()
    if epra.empty:
        print("[WARN] EPRA CSV not found or empty.")
        print("       Download EPRA CSV and save to:")
        print(f"       {RAW_DIR / 'epra_pump_prices_raw.csv'}")
    else:
        clean_epra_path = CLEAN_DIR / "epra_pump_prices.csv"
        epra.to_csv(clean_epra_path, index=False)
        print(f"[OK] Saved: {clean_epra_path}")

    print("=== DONE ===")


if __name__ == "__main__":
    main()
