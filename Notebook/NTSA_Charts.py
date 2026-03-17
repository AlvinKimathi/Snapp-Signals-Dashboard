from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

# ============================================================
# PATHS
# ============================================================
BASE_DIR = Path(r"C:\Users\Admin\OneDrive\Desktop\Projects\Snapp")
CLEAN_DIR = BASE_DIR / "Clean_Data"
OUT_DIR = BASE_DIR / "Output" / "Charts"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# LOAD DATA
# ============================================================
veh = pd.read_csv(CLEAN_DIR / "knbs_vehicle_registrations.csv")
lic = pd.read_csv(CLEAN_DIR / "knbs_transport_licenses.csv")

# New (Week 8 / NTSA accidents)
ACC_SUM_PATH = CLEAN_DIR / "knbs_road_accidents.csv"  # Table 13.6(a) summary
ACC_CLASS_PATH = CLEAN_DIR / "knbs_road_accidents_by_type_class.csv"  # Table 13.6(b)

acc_sum = pd.read_csv(ACC_SUM_PATH) if ACC_SUM_PATH.exists() else None
acc_class = pd.read_csv(ACC_CLASS_PATH) if ACC_CLASS_PATH.exists() else None


# ============================================================
# HELPERS
# ============================================================
def wide_to_long(df: pd.DataFrame, id_col: str) -> pd.DataFrame:
    year_cols = [c for c in df.columns if c != id_col]
    long = df.melt(
        id_vars=[id_col],
        value_vars=year_cols,
        var_name="year",
        value_name="value",
    )
    long["year"] = pd.to_numeric(long["year"], errors="coerce")
    long["value"] = pd.to_numeric(long["value"], errors="coerce")
    return long.dropna(subset=["year"]).sort_values("year")


def _norm_text(s: pd.Series) -> pd.Series:
    return (
        s.astype(str)
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
        .str.lower()
    )


def save_line_chart(df, x, y, title, xlabel, ylabel, outpath, label=None):
    plt.figure(figsize=(10, 5))
    if label:
        plt.plot(df[x], df[y], label=label)
        plt.legend()
    else:
        plt.plot(df[x], df[y])
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(outpath, dpi=200)
    plt.close()


def save_two_line_chart(df, x, y1, y2, title, xlabel, ylabel, label1, label2, outpath):
    plt.figure(figsize=(10, 5))
    plt.plot(df[x], df[y1], label=label1)
    plt.plot(df[x], df[y2], label=label2)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(outpath, dpi=200)
    plt.close()


# ============================================================
# LONG FORM TABLES (13.4 & 13.5)
# ============================================================
veh_long = wide_to_long(veh, "Type")
lic_long = wide_to_long(lic, "License_Type")

veh_long["_type_norm"] = _norm_text(veh_long["Type"])
lic_long["_lic_norm"] = _norm_text(lic_long["License_Type"])


# ============================================================
# 1) TOTAL UNITS REGISTERED
# ============================================================
total_row = veh_long[veh_long["_type_norm"].str.contains("total units", na=False)]
if not total_row.empty:
    total_row = total_row.sort_values("year")
    save_line_chart(
        total_row,
        x="year",
        y="value",
        title="Total Units Registered (Road Motor Vehicles & Motorcycles)",
        xlabel="Year",
        ylabel="Number",
        outpath=OUT_DIR / "ntsa_total_units_registered.png",
    )
else:
    print("Could not find 'Total Units Registered' row in Table 13.4")


# ============================================================
# 2) MOTOR & AUTO CYCLES (BODA SIGNAL)
# ============================================================
moto = veh_long[veh_long["_type_norm"].str.contains("motor and auto", na=False)]
if not moto.empty:
    moto = moto.sort_values("year")
    save_line_chart(
        moto,
        x="year",
        y="value",
        title="Motor & Auto Cycles Registered (Boda Signal)",
        xlabel="Year",
        ylabel="Number",
        outpath=OUT_DIR / "ntsa_motor_auto_cycles_registered.png",
    )
else:
    print("Could not find 'Motor and Auto Cycles' row in Table 13.4")


# ============================================================
# 3) PSV LICENSES TOTAL (Table 13.5)
# ============================================================
psv_total = lic_long[lic_long["_lic_norm"].eq("total")].copy()

if psv_total.empty:
    # fallback: anything containing psv
    psv_total = lic_long[lic_long["_lic_norm"].str.contains("psv", na=False)].copy()

if not psv_total.empty:
    # if multiple, take max per year (safe fallback)
    psv_total = (
        psv_total.groupby("year", as_index=False)["value"]
        .max()
        .sort_values("year")
    )

    save_line_chart(
        psv_total,
        x="year",
        y="value",
        title="Road Transport Licenses Issued (Total / PSV fallback)",
        xlabel="Year",
        ylabel="Number",
        outpath=OUT_DIR / "ntsa_transport_licenses_total.png",
    )
else:
    print("Total / PSV not found clearly in Table 13.5 (values may be missing '..')")


# ============================================================
# 4) PRIVATE vs PUBLIC REGISTRATIONS (Proxy)
# ============================================================
saloon = veh_long[veh_long["_type_norm"].eq("saloon cars")]
station = veh_long[veh_long["_type_norm"].eq("station wagons")]
matatu = veh_long[veh_long["_type_norm"].eq("mini-buses/matatu")]
buses_coaches = veh_long[veh_long["_type_norm"].eq("buses and coaches")]

if not saloon.empty and not station.empty and not matatu.empty and not buses_coaches.empty:
    private_df = pd.merge(
        saloon[["year", "value"]].rename(columns={"value": "saloon"}),
        station[["year", "value"]].rename(columns={"value": "station"}),
        on="year",
        how="outer",
    )

    public_df = pd.merge(
        buses_coaches[["year", "value"]].rename(columns={"value": "buses_coaches"}),
        matatu[["year", "value"]].rename(columns={"value": "matatu"}),
        on="year",
        how="outer",
    )

    combo = pd.merge(private_df, public_df, on="year", how="outer").sort_values("year")

    combo["Private (Saloon+Station)"] = combo["saloon"].fillna(0) + combo["station"].fillna(0)
    combo["Public (Buses+Matatu)"] = combo["buses_coaches"].fillna(0) + combo["matatu"].fillna(0)

    save_two_line_chart(
        combo,
        x="year",
        y1="Private (Saloon+Station)",
        y2="Public (Buses+Matatu)",
        title="Private vs Public Vehicle Registrations (Proxy)",
        xlabel="Year",
        ylabel="Number",
        label1="Private (Saloon+Station)",
        label2="Public (Buses+Matatu)",
        outpath=OUT_DIR / "ntsa_private_vs_public_registrations.png",
    )
else:
    print("Private vs Public chart skipped (one or more required rows missing).")
    print("Expected rows: Saloon cars, Station wagons, Mini-buses/Matatu, Buses and Coaches")


# ============================================================
# WEEK 8 ADDITIONS: ACCIDENTS (Table 13.6a + 13.6b)
# ============================================================

# --- 5) Accidents summary (13.6a): Reported accidents + Killed/Injured total + breakdown
if acc_sum is not None:
    # Convert summary wide -> long
    acc_sum_long = wide_to_long(acc_sum, "Metric")
    acc_sum_long["_metric_norm"] = _norm_text(acc_sum_long["Metric"])

    # A) Reported traffic accidents
    rta = acc_sum_long[acc_sum_long["_metric_norm"].str.contains("reported traffic accidents", na=False)]
    if not rta.empty:
        save_line_chart(
            rta.sort_values("year"),
            x="year",
            y="value",
            title="Reported Road Traffic Accidents",
            xlabel="Year",
            ylabel="Number",
            outpath=OUT_DIR / "ntsa_reported_traffic_accidents.png",
        )
    else:
        print("Accidents summary: 'Reported Traffic Accidents' not found")

    # B) Persons killed or injured (total)
    pk = acc_sum_long[acc_sum_long["_metric_norm"].str.contains("persons killed or injured", na=False)]
    if not pk.empty:
        save_line_chart(
            pk.sort_values("year"),
            x="year",
            y="value",
            title="Persons Killed or Injured (Total)",
            xlabel="Year",
            ylabel="Number",
            outpath=OUT_DIR / "ntsa_persons_killed_or_injured_total.png",
        )
    else:
        print("Accidents summary: 'Persons Killed or Injured' not found")

    # C) Breakdown: killed / seriously injured / slightly injured
    killed = acc_sum_long[acc_sum_long["_metric_norm"].eq("killed")]
    serious = acc_sum_long[acc_sum_long["_metric_norm"].str.contains("seriously injured", na=False)]
    slight = acc_sum_long[acc_sum_long["_metric_norm"].str.contains("slightly injured", na=False)]

    if not killed.empty and not serious.empty and not slight.empty:
        # align by year
        kdf = killed[["year", "value"]].rename(columns={"value": "Killed"})
        sdf = serious[["year", "value"]].rename(columns={"value": "Seriously Injured"})
        ldf = slight[["year", "value"]].rename(columns={"value": "Slightly Injured"})

        breakdown = kdf.merge(sdf, on="year", how="outer").merge(ldf, on="year", how="outer").sort_values("year")

        plt.figure(figsize=(10, 5))
        plt.plot(breakdown["year"], breakdown["Killed"], label="Killed")
        plt.plot(breakdown["year"], breakdown["Seriously Injured"], label="Seriously Injured")
        plt.plot(breakdown["year"], breakdown["Slightly Injured"], label="Slightly Injured")
        plt.title("Accident Casualties Breakdown")
        plt.xlabel("Year")
        plt.ylabel("Number")
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.savefig(OUT_DIR / "ntsa_casualties_breakdown.png", dpi=200)
        plt.close()
    else:
        print("Accidents summary: casualty breakdown rows not complete (Killed/Serious/Slight)")


# --- 6) Accidents by Type & Class (13.6b): optional aggregated views
if acc_class is not None:
    # Expect: Type, Class, 2020..2024 columns
    # Make sure the first 2 columns are correct (safe normalize)
    cols = list(acc_class.columns)
    if len(cols) >= 2:
        acc_class = acc_class.rename(columns={cols[0]: "Type", cols[1]: "Class"})

    # Keep only expected columns
    year_cols = [c for c in acc_class.columns if str(c).isdigit()]
    keep_cols = ["Type", "Class"] + year_cols
    acc_class = acc_class[keep_cols].dropna(how="all")

    # Long format
    acc_class_long = acc_class.melt(
        id_vars=["Type", "Class"],
        value_vars=year_cols,
        var_name="year",
        value_name="value",
    )
    acc_class_long["year"] = pd.to_numeric(acc_class_long["year"], errors="coerce")
    acc_class_long["value"] = pd.to_numeric(acc_class_long["value"], errors="coerce")
    acc_class_long["Type_norm"] = _norm_text(acc_class_long["Type"])
    acc_class_long["Class_norm"] = _norm_text(acc_class_long["Class"])
    acc_class_long = acc_class_long.dropna(subset=["year"])

    # A) Total casualties (sum) by Type over time (all classes)
    type_totals = (
        acc_class_long.groupby(["year", "Type"], as_index=False)["value"]
        .sum()
        .sort_values(["Type", "year"])
    )

    # Keep only a few key types if present
    # Common in your sheet: pedestrians, drivers, passengers, pillion passengers
    key_types = ["pedestrians", "drivers", "passengers", "pillion passengers"]
    present_key = []
    for kt in key_types:
        if (type_totals["Type"].astype(str).str.lower() == kt).any():
            present_key.append(kt)

    if present_key:
        plt.figure(figsize=(10, 5))
        for kt in present_key:
            sub = type_totals[type_totals["Type"].astype(str).str.lower() == kt]
            plt.plot(sub["year"], sub["value"], label=kt.title())
        plt.title("Accident Casualties by Type (All Classes Combined)")
        plt.xlabel("Year")
        plt.ylabel("Number")
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.savefig(OUT_DIR / "ntsa_casualties_by_type.png", dpi=200)
        plt.close()
    else:
        # fallback: just do top 4 types by latest year total
        latest_year = int(type_totals["year"].max()) if not type_totals.empty else None
        if latest_year is not None:
            top_types = (
                type_totals[type_totals["year"] == latest_year]
                .sort_values("value", ascending=False)
                .head(4)["Type"]
                .tolist()
            )
            if top_types:
                plt.figure(figsize=(10, 5))
                for t in top_types:
                    sub = type_totals[type_totals["Type"] == t]
                    plt.plot(sub["year"], sub["value"], label=str(t))
                plt.title("Accident Casualties by Type (Top Types)")
                plt.xlabel("Year")
                plt.ylabel("Number")
                plt.grid(True)
                plt.legend()
                plt.tight_layout()
                plt.savefig(OUT_DIR / "ntsa_casualties_by_type.png", dpi=200)
                plt.close()

    # B) Total killed vs injured (Serious+Slight) (if classes are clean)
    # We'll attempt to build: Killed + (Seriously Injured + Slightly Injured)
    killed_df = acc_class_long[acc_class_long["Class_norm"].eq("killed")]
    serious_df = acc_class_long[acc_class_long["Class_norm"].str.contains("seriously", na=False)]
    slight_df = acc_class_long[acc_class_long["Class_norm"].str.contains("slightly", na=False)]

    if not killed_df.empty and not serious_df.empty and not slight_df.empty:
        killed_total = killed_df.groupby("year", as_index=False)["value"].sum().rename(columns={"value": "Killed"})
        serious_total = serious_df.groupby("year", as_index=False)["value"].sum().rename(columns={"value": "Seriously Injured"})
        slight_total = slight_df.groupby("year", as_index=False)["value"].sum().rename(columns={"value": "Slightly Injured"})

        merged = killed_total.merge(serious_total, on="year", how="outer").merge(slight_total, on="year", how="outer").sort_values("year")
        merged["Injured (Serious+Slight)"] = merged["Seriously Injured"].fillna(0) + merged["Slightly Injured"].fillna(0)

        save_two_line_chart(
            merged,
            x="year",
            y1="Killed",
            y2="Injured (Serious+Slight)",
            title="Killed vs Injured (All Types Combined)",
            xlabel="Year",
            ylabel="Number",
            label1="Killed",
            label2="Injured (Serious+Slight)",
            outpath=OUT_DIR / "ntsa_killed_vs_injured.png",
        )
    else:
        print("Accidents by type/class: could not build Killed vs Injured (classes missing/unclean).")


print("NTSA/Transport charts saved to:", OUT_DIR)
