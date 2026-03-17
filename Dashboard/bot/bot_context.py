from __future__ import annotations

from typing import Any
import pandas as pd


def _safe_float(v):
    try:
        if pd.isna(v):
            return None
        return float(v)
    except Exception:
        return None


def _safe_date(v):
    try:
        if pd.isna(v):
            return None
        return str(pd.to_datetime(v).date())
    except Exception:
        return None


def build_dashboard_context(
    *,
    latest_cpi=None,
    latest_fx=None,
    latest_rates=None,
    latest_trends_date=None,
    latest_epra_cycle=None,
    latest_wb_year=None,
    latest_year=None,
    acc_latest_year=None,
    latest_wb_reg_year=None,
    esi=None,
    cpix=None,
    kra_events=None,
    base_signals=None,
    opportunity_df=None,
    top3_opportunity=None,
) -> dict[str, Any]:
    esi_summary = {}
    if esi is not None and not esi.empty:
        latest_esi = esi.iloc[-1]
        esi_summary = {
            "latest_month": _safe_date(latest_esi.get("month")),
            "esi_overall": _safe_float(latest_esi.get("esi_overall")),
            "interpretation_band": latest_esi.get("interpretation_band"),
            "diesel_kes_l": _safe_float(latest_esi.get("diesel_kes_l")),
            "brent_usd_bbl": _safe_float(latest_esi.get("brent_usd_bbl")),
        }

    cpix_summary = {}
    if cpix is not None and not cpix.empty:
        latest_cpix = cpix.iloc[-1]
        cpix_summary = {
            "latest_period": _safe_date(latest_cpix.get("period")),
            "cpix_overall": _safe_float(latest_cpix.get("cpix_overall")),
            "cpix_sme": _safe_float(latest_cpix.get("cpix_sme")),
            "cpix_midmarket": _safe_float(latest_cpix.get("cpix_midmarket")),
            "cpix_enterprise": _safe_float(latest_cpix.get("cpix_enterprise")),
        }

    kra_preview = []
    if kra_events is not None and not kra_events.empty:
        preview_cols = [
            c for c in ["event_date", "event_type", "tax_area", "segment", "severity", "description"]
            if c in kra_events.columns
        ]
        if preview_cols:
            for _, row in kra_events[preview_cols].head(5).iterrows():
                item = {}
                for col in preview_cols:
                    value = row.get(col)
                    if col == "event_date":
                        value = _safe_date(value)
                    item[col] = value
                kra_preview.append(item)

    signals_summary = {}
    if base_signals is not None and not base_signals.empty:
        latest_row = base_signals.iloc[-1]
        signals_summary = {
            "latest_month": _safe_date(latest_row.get("month")),
            "macro_pressure": _safe_float(latest_row.get("macro_pressure")),
            "compliance_tightness": _safe_float(latest_row.get("compliance_tightness")),
            "demand_pulse": _safe_float(latest_row.get("demand_100")),
            "inflation_yoy": _safe_float(latest_row.get("infl_yoy")),
            "kes_usd": _safe_float(latest_row.get("kes_usd")),
            "cbr": _safe_float(latest_row.get("cbr")),
            "esi_overall": _safe_float(latest_row.get("esi_overall")),
            "cpix_overall": _safe_float(latest_row.get("cpix_overall")),
        }

    opportunity_summary = {}
    if opportunity_df is not None and not opportunity_df.empty:
        ranking_preview = []
        if {"Sector", "Opportunity_Score"}.issubset(opportunity_df.columns):
            ranking_preview = opportunity_df[["Sector", "Opportunity_Score"]].head(5).to_dict(orient="records")

        opportunity_summary = {
            "top_sectors": top3_opportunity or [],
            "ranking_preview": ranking_preview,
        }

    return {
        "dashboard_name": "Snapp Kenya Signals Dashboard",
        "assistant_name": "Snapp Bot",
        "welcome_prompt": "Hey There, Ask me anything?",
        "definitions": {
            "macro_pressure": "A combined 0-100 signal built from inflation, FX, interest rates, and energy stress. Higher means a tighter, more expensive macro environment.",
            "compliance_tightness": "A 0-100 signal derived from interest-rate/compliance-related pressure indicators, including CPIx where available.",
            "demand_pulse": "A 0-100 normalized signal built from dashboard demand proxy indices such as Google Trends baskets.",
            "esi": "Energy Stress Index. A composite measure of energy-related cost stress using pump prices, FX and Brent components.",
            "cpix": "Compliance Pressure Index. A signal showing compliance burden/intensity across customer segments.",
            "opportunity_score": "A dashboard score ranking sectors based on demand, macro pressure, compliance pressure, and exposure assumptions.",
        },
        "latest_macro": {
            "inflation_yoy_pct": _safe_float(latest_cpi.get("12-Month Inflation")) if latest_cpi is not None else None,
            "inflation_date": _safe_date(latest_cpi.get("date")) if latest_cpi is not None else None,
            "kes_usd": _safe_float(latest_fx.get("United States dollar")) if latest_fx is not None else None,
            "fx_date": _safe_date(latest_fx.get("date")) if latest_fx is not None else None,
            "cbr_pct": _safe_float(latest_rates.get("Central Bank Rate")) if latest_rates is not None else None,
            "tbill_91_pct": _safe_float(latest_rates.get("91-Day Tbill")) if latest_rates is not None else None,
            "rates_date": _safe_date(latest_rates.get("date")) if latest_rates is not None else None,
        },
        "latest_demand": {
            "latest_trends_date": _safe_date(latest_trends_date),
            "latest_epra_cycle": _safe_date(latest_epra_cycle),
            "latest_worldbank_year": latest_wb_year,
        },
        "latest_transport": {
            "latest_registration_year": latest_year,
            "latest_road_safety_year": acc_latest_year,
        },
        "latest_regional": {
            "latest_worldbank_regional_year": latest_wb_reg_year,
        },
        "esi_summary": esi_summary,
        "cpix_summary": cpix_summary,
        "signals_summary": signals_summary,
        "opportunity_summary": opportunity_summary,
        "kra_events_preview": kra_preview,
        "snapp_lens": {
            "macro": "CPI informs affordability, FX signals imported cost pressure, and rates indicate tighter credit conditions and caution.",
            "transport": "Registrations and road safety act as real-world signals for mobility demand, logistics reliability, and operational stress.",
            "demand": "Google Trends, EPRA prices and World Bank context help anticipate changes in household and business demand.",
            "regional": "Peer comparisons help show whether Kenya is moving with or away from comparable markets.",
            "compliance": "CPIx and friction mapping show where compliance pressure is rising and where support products may matter.",
            "energy": "ESI helps identify rising cost pressure in fuel, logistics and imported energy exposure.",
            "signals_map": "The Signals Map combines multiple indicators into simple operating signals for decision-making.",
            "opportunity_map": "The Opportunity Map highlights where Snapp may want to focus attention or capital based on current regime conditions.",
        },
    }