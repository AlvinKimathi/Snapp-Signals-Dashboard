from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd


def _safe_read_csv(path: Path) -> pd.DataFrame:
    try:
        if path.exists():
            return pd.read_csv(path)
        return pd.DataFrame()
    except Exception:
        return pd.DataFrame()


def wide_years_to_long(df: pd.DataFrame, id_cols: list[str]) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()
    year_cols = [c for c in df.columns if str(c).isdigit()]
    if not year_cols:
        year_cols = [
            c
            for c in df.columns
            if isinstance(c, (int, float)) and str(int(c)).isdigit()
        ]
    if not year_cols:
        return pd.DataFrame()
    out = df.melt(id_vars=id_cols, value_vars=year_cols, var_name="year", value_name="value")
    out["year"] = pd.to_numeric(out["year"], errors="coerce")
    out["value"] = pd.to_numeric(out["value"], errors="coerce")
    return out.dropna(subset=["year"]).sort_values("year")


def wide_to_long(df: pd.DataFrame, id_col: str) -> pd.DataFrame:
    if df is None or df.empty or id_col not in df.columns:
        return pd.DataFrame(columns=[id_col, "year", "value"])
    year_cols = [c for c in df.columns if c != id_col]
    out = df.melt(id_vars=[id_col], value_vars=year_cols, var_name="year", value_name="value")
    out["year"] = pd.to_numeric(out["year"], errors="coerce")
    out["value"] = pd.to_numeric(out["value"], errors="coerce")
    out = out.dropna(subset=["year"])
    return out


def regional_wide_to_long(wide: pd.DataFrame) -> pd.DataFrame:
    if wide is None or wide.empty or "year" not in wide.columns:
        return pd.DataFrame(columns=["year", "country", "indicator", "value"])

    cols = [c for c in wide.columns if c != "year"]
    if not cols:
        return pd.DataFrame(columns=["year", "country", "indicator", "value"])

    df = wide.copy()
    for c in cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    long_df = df.melt(id_vars=["year"], value_vars=cols, var_name="series", value_name="value")
    long_df["series"] = long_df["series"].astype(str)

    parts = long_df["series"].str.split(r"\s*\|\s*", n=1, expand=True)
    long_df["country"] = parts[0].fillna("").astype(str).str.strip()
    long_df["indicator"] = parts[1].fillna("").astype(str).str.strip()

    long_df["year"] = pd.to_numeric(long_df["year"], errors="coerce")
    long_df = long_df.dropna(subset=["year"])
    long_df = long_df.drop(columns=["series"])
    return long_df


@dataclass(frozen=True)
class PreparedData:
    frames: dict[str, pd.DataFrame]

    def __getitem__(self, key: str) -> pd.DataFrame:
        return self.frames.get(key, pd.DataFrame())


def load_and_prepare_data(clean_dir: Path) -> PreparedData:
    fx = _safe_read_csv(clean_dir / "fx_monthly.csv")
    rates = _safe_read_csv(clean_dir / "cbk_rates.csv")
    cpi = _safe_read_csv(clean_dir / "cpi_inflation.csv")
    veh = _safe_read_csv(clean_dir / "knbs_vehicle_registrations.csv")
    lic = _safe_read_csv(clean_dir / "knbs_transport_licenses.csv")
    acc_sum = _safe_read_csv(clean_dir / "knbs_road_accidents_summary.csv")
    acc_class = _safe_read_csv(clean_dir / "knbs_road_accidents_by_type_class.csv")

    trends = _safe_read_csv(clean_dir / "demand_google_trends.csv")
    wb_ctx = _safe_read_csv(clean_dir / "worldbank_demand_context.csv")
    epra = _safe_read_csv(clean_dir / "epra_pump_prices.csv")
    wb_reg = _safe_read_csv(clean_dir / "worldbank_regional_context.csv")

    cpix = _safe_read_csv(clean_dir / "compliance_pressure_index.csv")
    kra_events = _safe_read_csv(clean_dir / "kra_events.csv")
    friction = _safe_read_csv(clean_dir / "friction_map.csv")
    kra_rev = _safe_read_csv(clean_dir / "kpi_kra_revenue.csv")
    esi = _safe_read_csv(clean_dir / "energy_stress_index.csv")

    # Parse / clean date fields
    if not esi.empty and "month_key" in esi.columns:
        esi = esi.copy()
        esi["month"] = pd.to_datetime(esi["month_key"], errors="coerce")
        esi = esi.dropna(subset=["month"]).sort_values("month")

    for name, df, col in [
        ("fx", fx, "date"),
        ("rates", rates, "date"),
        ("cpi", cpi, "date"),
    ]:
        if not df.empty and col in df.columns:
            _df = df.copy()
            _df[col] = pd.to_datetime(_df[col], errors="coerce")
            _df = _df.dropna(subset=[col]).sort_values(col)
            if name == "fx":
                fx = _df
            elif name == "rates":
                rates = _df
            elif name == "cpi":
                cpi = _df

    if not trends.empty and "date" in trends.columns:
        trends = trends.copy()
        trends["date"] = pd.to_datetime(trends["date"], errors="coerce")
        trends = trends.dropna(subset=["date"]).sort_values("date")

    if not epra.empty:
        epra = epra.copy()
        if "cycle_start" in epra.columns:
            epra["cycle_start"] = pd.to_datetime(epra["cycle_start"], errors="coerce")
        if "cycle_end" in epra.columns:
            epra["cycle_end"] = pd.to_datetime(epra["cycle_end"], errors="coerce")
        if "city" in epra.columns:
            epra["city"] = epra["city"].astype(str).str.strip()
        sort_cols = [c for c in ["cycle_start", "city"] if c in epra.columns]
        if sort_cols:
            epra = epra.sort_values(sort_cols)

    if not wb_ctx.empty and "year" in wb_ctx.columns:
        wb_ctx = wb_ctx.copy()
        wb_ctx["year"] = pd.to_numeric(wb_ctx["year"], errors="coerce")
        wb_ctx = wb_ctx.dropna(subset=["year"]).sort_values("year")

    if not wb_reg.empty:
        wb_reg = wb_reg.copy()
        if "year" in wb_reg.columns:
            wb_reg["year"] = pd.to_numeric(wb_reg["year"], errors="coerce")
            wb_reg = wb_reg.dropna(subset=["year"]).sort_values("year")
        else:
            wb_reg = pd.DataFrame()

    if not cpix.empty and "period" in cpix.columns:
        cpix = cpix.copy()
        cpix["period"] = pd.to_datetime(cpix["period"], errors="coerce")
        cpix = cpix.dropna(subset=["period"]).sort_values("period")

    if not kra_events.empty and "event_date" in kra_events.columns:
        kra_events = kra_events.copy()
        kra_events["event_date"] = pd.to_datetime(kra_events["event_date"], errors="coerce")
        kra_events = kra_events.dropna(subset=["event_date"]).sort_values(
            "event_date", ascending=False
        )

    # Precompute common long forms
    veh_long = (
        wide_to_long(veh, "Type")
        if not veh.empty and "Type" in veh.columns
        else pd.DataFrame(columns=["Type", "year", "value"])
    )
    lic_long = (
        wide_to_long(lic, "License_Type")
        if not lic.empty and "License_Type" in lic.columns
        else pd.DataFrame(columns=["License_Type", "year", "value"])
    )
    acc_sum_long = (
        wide_years_to_long(acc_sum, ["Metric"])
        if not acc_sum.empty and "Metric" in acc_sum.columns
        else pd.DataFrame(columns=["Metric", "year", "value"])
    )
    acc_class_long = (
        wide_years_to_long(acc_class, ["Type", "Class"])
        if not acc_class.empty and {"Type", "Class"}.issubset(acc_class.columns)
        else pd.DataFrame(columns=["Type", "Class", "year", "value"])
    )
    wb_reg_long = (
        regional_wide_to_long(wb_reg)
        if not wb_reg.empty
        else pd.DataFrame(columns=["year", "country", "indicator", "value"])
    )

    # Clean known label noise in accident summary
    if not acc_sum_long.empty and "Metric" in acc_sum_long.columns:
        acc_sum_long = acc_sum_long.copy()
        acc_sum_long["Metric"] = acc_sum_long["Metric"].astype(str).str.strip()
        acc_sum_long = acc_sum_long[
            ~acc_sum_long["Metric"].isin(["of which:", "Persons Killed or Injured:-"])
        ]

    if not acc_class_long.empty:
        acc_class_long = acc_class_long.copy()
        acc_class_long["Type"] = acc_class_long["Type"].astype(str).str.strip()
        acc_class_long["Class"] = acc_class_long["Class"].astype(str).str.strip()

    return PreparedData(
        frames={
            "fx": fx,
            "rates": rates,
            "cpi": cpi,
            "veh": veh,
            "lic": lic,
            "acc_sum": acc_sum,
            "acc_class": acc_class,
            "trends": trends,
            "wb_ctx": wb_ctx,
            "epra": epra,
            "wb_reg": wb_reg,
            "cpix": cpix,
            "kra_events": kra_events,
            "friction": friction,
            "kra_rev": kra_rev,
            "esi": esi,
            "veh_long": veh_long,
            "lic_long": lic_long,
            "acc_sum_long": acc_sum_long,
            "acc_class_long": acc_class_long,
            "wb_reg_long": wb_reg_long,
        }
    )


def compute_latest_values(data: PreparedData) -> dict[str, Any]:
    fx = data["fx"]
    rates = data["rates"]
    cpi = data["cpi"]
    trends = data["trends"]
    epra = data["epra"]
    wb_ctx = data["wb_ctx"]
    wb_reg = data["wb_reg"]
    veh = data["veh"]
    acc_sum = data["acc_sum"]

    latest_fx = None
    if not fx.empty and "United States dollar" in fx.columns:
        tmp = fx.dropna(subset=["United States dollar"])
        if len(tmp):
            latest_fx = tmp.iloc[-1]

    latest_rates = None
    if not rates.empty and "Central Bank Rate" in rates.columns:
        tmp = rates.dropna(subset=["Central Bank Rate"])
        if len(tmp):
            latest_rates = tmp.iloc[-1]

    latest_cpi = None
    if not cpi.empty and "12-Month Inflation" in cpi.columns:
        tmp = cpi.dropna(subset=["12-Month Inflation"])
        if len(tmp):
            latest_cpi = tmp.iloc[-1]

    latest_trends_date = None
    if not trends.empty and "date" in trends.columns:
        tmp = trends.dropna(subset=["date"])
        if len(tmp):
            latest_trends_date = tmp.iloc[-1]["date"]

    latest_epra_cycle = None
    if not epra.empty and "cycle_start" in epra.columns:
        tmp = epra.dropna(subset=["cycle_start"])
        if len(tmp):
            latest_epra_cycle = tmp.iloc[-1]["cycle_start"]

    latest_wb_year = None
    if not wb_ctx.empty and "year" in wb_ctx.columns:
        tmp = wb_ctx.dropna(subset=["year"])
        if len(tmp):
            latest_wb_year = int(tmp.iloc[-1]["year"])

    latest_wb_reg_year = None
    if not wb_reg.empty and "year" in wb_reg.columns:
        tmp = wb_reg.dropna(subset=["year"])
        if len(tmp):
            latest_wb_reg_year = int(tmp.iloc[-1]["year"])

    latest_year = None
    if not veh.empty:
        year_cols = [c for c in veh.columns if str(c).isdigit()]
        if year_cols:
            latest_year = int(max(int(c) for c in year_cols))

    acc_latest_year = None
    if not acc_sum.empty:
        year_cols = [c for c in acc_sum.columns if str(c).isdigit()]
        if year_cols:
            acc_latest_year = int(max(int(c) for c in year_cols))

    return {
        "latest_fx": latest_fx,
        "latest_rates": latest_rates,
        "latest_cpi": latest_cpi,
        "latest_trends_date": latest_trends_date,
        "latest_epra_cycle": latest_epra_cycle,
        "latest_wb_year": latest_wb_year,
        "latest_wb_reg_year": latest_wb_reg_year,
        "latest_year": latest_year,
        "acc_latest_year": acc_latest_year,
    }


def compute_signals_base(
    *,
    cpi: pd.DataFrame,
    fx: pd.DataFrame,
    rates: pd.DataFrame,
    esi: pd.DataFrame,
    cpix: pd.DataFrame,
    trends: pd.DataFrame,
) -> pd.DataFrame:
    def _to_month(series):
        return pd.to_datetime(series, errors="coerce").dt.to_period("M").dt.to_timestamp()

    def _minmax_0_100(s: pd.Series) -> pd.Series:
        s = pd.to_numeric(s, errors="coerce")
        if s.dropna().empty:
            return s
        mn, mx = float(s.min()), float(s.max())
        if mx == mn:
            return s * 0
        return (s - mn) / (mx - mn) * 100

    def _safe_col(df: pd.DataFrame, col: str) -> bool:
        return (df is not None) and (not df.empty) and (col in df.columns)

    base = pd.DataFrame()

    if _safe_col(cpi, "date") and _safe_col(cpi, "12-Month Inflation"):
        tmp = cpi.copy()
        tmp["month"] = _to_month(tmp["date"])
        tmp = tmp.dropna(subset=["month"]).groupby("month", as_index=False)["12-Month Inflation"].mean()
        base = tmp.rename(columns={"12-Month Inflation": "infl_yoy"})

    if _safe_col(fx, "date") and _safe_col(fx, "United States dollar"):
        tmp = fx.copy()
        tmp["month"] = _to_month(tmp["date"])
        tmp = tmp.dropna(subset=["month"]).groupby("month", as_index=False)["United States dollar"].mean()
        base = base.merge(tmp.rename(columns={"United States dollar": "kes_usd"}), on="month", how="outer") if not base.empty else tmp.rename(columns={"United States dollar": "kes_usd"})

    if _safe_col(rates, "date") and _safe_col(rates, "Central Bank Rate"):
        tmp = rates.copy()
        tmp["month"] = _to_month(tmp["date"])
        tmp = tmp.dropna(subset=["month"]).groupby("month", as_index=False)["Central Bank Rate"].mean()
        base = base.merge(tmp.rename(columns={"Central Bank Rate": "cbr"}), on="month", how="outer") if not base.empty else tmp.rename(columns={"Central Bank Rate": "cbr"})

    if (esi is not None) and (not esi.empty) and ("month" in esi.columns) and ("esi_overall" in esi.columns):
        tmp = esi.copy()
        tmp["month"] = _to_month(tmp["month"])
        tmp = tmp.dropna(subset=["month"]).groupby("month", as_index=False)["esi_overall"].mean()
        base = base.merge(tmp, on="month", how="outer") if not base.empty else tmp

    if (cpix is not None) and (not cpix.empty) and ("period" in cpix.columns) and ("cpix_overall" in cpix.columns):
        tmp = cpix.copy()
        tmp["month"] = _to_month(tmp["period"])
        tmp["cpix_overall"] = pd.to_numeric(tmp["cpix_overall"], errors="coerce")
        tmp = tmp.dropna(subset=["month"]).groupby("month", as_index=False)["cpix_overall"].mean()
        base = base.merge(tmp, on="month", how="outer") if not base.empty else tmp

    if (trends is not None) and (not trends.empty) and ("date" in trends.columns):
        demand_cols = [c for c in trends.columns if c.endswith("_index")]
        if demand_cols:
            tmp = trends.copy()
            tmp["month"] = _to_month(tmp["date"])
            tmp = tmp.dropna(subset=["month"])
            for c in demand_cols:
                tmp[c] = pd.to_numeric(tmp[c], errors="coerce")
            tmp = tmp.groupby("month", as_index=False)[demand_cols].mean()
            tmp["demand_pulse_raw"] = tmp[demand_cols].mean(axis=1, skipna=True)
            base = base.merge(tmp[["month", "demand_pulse_raw"]], on="month", how="outer") if not base.empty else tmp[["month", "demand_pulse_raw"]]

    if base.empty:
        return pd.DataFrame()

    base = base.sort_values("month").reset_index(drop=True)

    if "infl_yoy" in base.columns:
        base["infl_100"] = _minmax_0_100(base["infl_yoy"])
    if "kes_usd" in base.columns:
        base["fx_100"] = _minmax_0_100(base["kes_usd"])
    if "cbr" in base.columns:
        base["cbr_100"] = _minmax_0_100(base["cbr"])
    if "esi_overall" in base.columns:
        base["esi_100"] = _minmax_0_100(base["esi_overall"])
    if "cpix_overall" in base.columns:
        base["cpix_100"] = _minmax_0_100(base["cpix_overall"])
    if "demand_pulse_raw" in base.columns:
        base["demand_100"] = _minmax_0_100(base["demand_pulse_raw"])

    pressure_parts = [c for c in ["infl_100", "fx_100", "cbr_100", "esi_100"] if c in base.columns]
    if pressure_parts:
        base["macro_pressure"] = base[pressure_parts].mean(axis=1, skipna=True)

    compl_parts = [c for c in ["cbr_100", "cpix_100"] if c in base.columns]
    if compl_parts:
        base["compliance_tightness"] = base[compl_parts].mean(axis=1, skipna=True)

    if "esi_100" in base.columns:
        base["energy_stress"] = base["esi_100"]

    return base


def compute_opportunity_df(base_signals: pd.DataFrame) -> pd.DataFrame:
    # Mirrors logic in App.py "Opportunity Map".
    if base_signals is None or base_signals.empty:
        return pd.DataFrame()

    latest = base_signals.dropna(subset=["month"]).iloc[-1]
    demand = float(latest.get("demand_100")) if pd.notna(latest.get("demand_100")) else 50.0
    pressure = float(latest.get("macro_pressure")) if pd.notna(latest.get("macro_pressure")) else 50.0
    compliance = float(latest.get("compliance_tightness")) if pd.notna(latest.get("compliance_tightness")) else 50.0

    sectors = [
        "Transport & Logistics",
        "Manufacturing",
        "Agriculture Value Chain",
        "Construction",
        "FMCG Distribution",
        "Retail",
        "Hospitality",
        "Financial Services",
        "Professional Services",
        "Digital / SaaS",
    ]

    opp = pd.DataFrame({"Sector": sectors})
    # Simple heuristic scoring: demand helps, pressure/compliance hurt.
    opp["Opportunity_Score"] = (demand * 0.6) - (pressure * 0.25) - (compliance * 0.15)
    return opp.sort_values("Opportunity_Score", ascending=False).reset_index(drop=True)

