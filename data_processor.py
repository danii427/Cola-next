"""
data_processor.py - Enterprise Data Processing, Normalization & Analytics Engine for Cola Next SMO KPI Analyzer
Handles Excel detection, robust column parsing, metric normalization, performance zone scoring, and coaching narratives.
"""

import pandas as pd
import numpy as np
import re
from typing import Tuple, Dict, Any, List, Optional


# ============================================================
# COLUMN ALIASES FOR COMPREHENSIVE 49-COLUMN COVERAGE
# ============================================================

COLUMN_ALIASES = {
    # Organization & Personnel
    "SR#": ["sr#", "sr no", "sr.", "serial", "sno", "s#"],
    "Region": ["region", "region name", "reg"],
    "Zone": ["zone", "zone name"],
    "Territory ID": ["territory id", "territory code", "terr id"],
    "Territory": ["territory", "territory name", "terr"],
    "Dist. Code": ["dist. code", "dist code", "distributor code", "distribution code"],
    "Distribution Name": ["distribution name", "distributor name", "distribution", "distributor"],
    "Route id": ["route id", "routeid", "route code", "routecode", "route no"],
    "Route Name": ["route name", "route", "routename"],
    "SMO Code": ["smo code", "smocode", "employee code", "emp code"],
    "SMO Name": ["smo name", "smo", "smoname", "sales officer", "sales man", "salesman"],
    "DoJ": ["doj", "date of joining", "join date", "joining date"],
    "Status": ["status", "emp status", "active status"],
    "Report Month": ["report month", "month", "reporting month"],
    "Report Year": ["report year", "year", "reporting year"],
    
    # Core Targets & Sales
    "Working Days": ["working days", "work days", "workingdays", "days worked", "days"],
    "Target": ["target", "sales target", "target cases", "month target"],
    "Route Sale": ["route sale", "actual sale", "total sale", "sale cases", "sales"],
    "Sale (ORD Date) out pjp": ["sale (ord date) out pjp", "sale out pjp", "out pjp sale", "out pjp"],
    "Ach.%": ["ach.%", "ach %", "ach%", "achievement %", "achievement%", "achievement", "achieved %"],
    
    # Outlets & Route Coverage
    "Outlets on Route": ["outlets on route", "total outlets", "route outlets"],
    "H PJP Outlets": ["h pjp outlets", "historical pjp outlets", "hpjp outlets"],
    "Current PJP Outlets": ["current pjp outlets", "pjp outlets"],
    "Plan Calls Per Week": ["plan calls per week", "planned calls/week"],
    "No. of Productive Unique Outlets": ["no. of productive unique outlets", "productive unique outlets", "productive outlets"],
    "Productive Unique Outlets %": ["productive unique outlets %", "productive unique outlets%", "productive outlets %"],
    "Actual Call On Unique Outlets": ["actual call on unique outlets", "actual unique calls"],
    
    # Calls & Call Completion
    "Plan Calls MTD": ["plan calls mtd", "planned calls mtd", "target calls"],
    "Actual Calls MTD": ["actual calls mtd", "calls mtd", "total calls"],
    "Call Comp. %": ["call comp. %", "call comp %", "callcomp%", "call completion %", "call completion%", "call completion"],
    "No. of Actual Un-Planned Calls": ["no. of actual un-planned calls", "unplanned calls", "un-planned calls"],
    "No. of Actual Un-Planned Calls %": ["no. of actual un-planned calls %", "unplanned calls %", "un-planned calls %"],
    "No. of Productive Calls MTD": ["no. of productive calls mtd", "productive calls mtd", "productive calls"],
    "Strike Rate %": ["strike rate %", "strike rate%", "strikerate%", "strike rate", "sr%"],
    
    # Execution & Basket Metrics
    "SKU Per Invoice": ["sku per invoice", "sku/invoice", "sku per bill", "sku/bill"],
    "Drop Size": ["drop size", "dropsize", "avg drop size", "cases per order"],
    "AVG. Time First Order": ["avg. time first order", "time first order", "first order time", "avg time first order"],
    "AVG. Time Last Order": ["avg. time last order", "time last order", "last order time", "avg time last order"],
    "AVG. Time in Market": ["avg. time in market", "time in market", "market time", "avg time in market"],
    
    # Delivery & Fulfillment
    "No. of Ordered Cases": ["no. of ordered cases", "ordered cases", "total orders"],
    "No. of Delivered Cases": ["no. of delivered cases", "delivered cases"],
    "No. of Un-Delivered Cases": ["no. of un-delivered cases", "undelivered cases", "un-delivered cases"],
    "Delivered Cases %": ["delivered cases %", "delivered cases%", "deliveredcases%", "delivered case %", "delivery %", "delivery rate %"],
    "No. of Specific FLV Delivered Cases": ["no. of specific flv delivered cases", "flv delivered cases", "flavor cases"],
    "Flavour %": ["flavour %", "flavor %", "flavour%", "flavor%"],
    
    # GPS Discipline & Field Compliance
    "No. of Calls (PJP)": ["no. of calls (pjp)", "pjp calls", "total pjp calls"],
    "No. of Calls within Radius (PJP)": ["no. of calls within radius (pjp)", "calls within radius", "in radius calls"],
    "No. of Calls Out of Radius (PJP)": ["no. of calls out of radius (pjp)", "calls out of radius", "out radius calls"],
    "GPS Accuracy % (PJP)": ["gps accuracy % (pjp)", "gps accuracy%", "gps accuracy %", "gps accuracy", "gps accuracy pjp"]
}

# Key columns required for minimum viable dashboard
CORE_KPI_COLUMNS = [
    "SMO Name",
    "Route Name",
    "Working Days",
    "Ach.%",
    "Call Comp. %",
    "Strike Rate %",
    "Delivered Cases %",
    "GPS Accuracy % (PJP)"
]


def normalize_header(value: Any) -> str:
    """Normalizes string header by removing punctuation, spaces, and converting to lowercase."""
    if pd.isna(value):
        return ""
    val_str = str(value).replace("\xa0", " ").strip().lower()
    val_str = val_str.replace("&", " and ")
    val_str = re.sub(r"\s+", "", val_str)
    val_str = re.sub(r"[^a-z0-9]", "", val_str)
    return val_str


# Build fast normalized lookup dictionary
ALIAS_LOOKUP = {}
for canonical_name, aliases in COLUMN_ALIASES.items():
    for alias in aliases:
        ALIAS_LOOKUP[normalize_header(alias)] = canonical_name


def find_excel_header(excel_file: pd.ExcelFile, rows_to_scan: int = 30) -> Tuple[Optional[str], Optional[int]]:
    """Automatically scans workbook sheets to find the true KPI header row."""
    best_sheet = None
    best_header_row = None
    best_score = -1

    for sheet_name in excel_file.sheet_names:
        try:
            preview = pd.read_excel(excel_file, sheet_name=sheet_name, header=None, nrows=rows_to_scan)
        except Exception:
            continue

        for row_index in range(len(preview)):
            row_values = preview.iloc[row_index].tolist()
            recognized_columns = set()

            for value in row_values:
                norm = normalize_header(value)
                if norm in ALIAS_LOOKUP:
                    recognized_columns.add(ALIAS_LOOKUP[norm])

            score = len(recognized_columns)
            if "SMO Name" in recognized_columns:
                score += 4
            if "Route Name" in recognized_columns:
                score += 2
            if "Target" in recognized_columns:
                score += 2
            if "Ach.%" in recognized_columns:
                score += 3
            if "GPS Accuracy % (PJP)" in recognized_columns:
                score += 2

            if score > best_score:
                best_score = score
                best_sheet = sheet_name
                best_header_row = row_index

    if best_sheet is None or best_header_row is None or best_score < 6:
        return None, None

    return best_sheet, best_header_row


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Standardizes column names in dataframe according to canonical alias dictionary."""
    rename_map = {}
    for column in df.columns:
        norm = normalize_header(column)
        if norm in ALIAS_LOOKUP:
            rename_map[column] = ALIAS_LOOKUP[norm]

    df = df.rename(columns=rename_map)
    # Remove duplicate columns if any
    df = df.loc[:, ~df.columns.duplicated(keep="first")]
    return df


def safe_text(value: Any, fallback: str = "") -> str:
    """Safely cleans text values and converts nulls to fallback string."""
    if pd.isna(value):
        return fallback
    text = str(value).strip()
    if text.lower() in ["nan", "none", "nat", "null"]:
        return fallback
    # Remove excessive float formatting like '1.0' for string identifiers
    if text.endswith(".0") and text[:-2].isdigit():
        return text[:-2]
    return text


def numeric_series(series: pd.Series) -> pd.Series:
    """Cleans numeric series by stripping percentage signs, commas, and converting to numeric."""
    cleaned = (
        series.astype(str)
        .str.replace("%", "", regex=False)
        .str.replace(",", "", regex=False)
        .str.strip()
    )
    return pd.to_numeric(cleaned, errors="coerce")


def normalize_percentage_column(series: pd.Series) -> pd.Series:
    """Normalizes percentage columns (converts 0.0-1.0 scale to 0-100%)."""
    numeric = numeric_series(series)
    usable = numeric.dropna()
    if usable.empty:
        return numeric

    # If 75th percentile <= 1.5 and max <= 2.5, it is in 0.0-1.0 format
    if usable.abs().quantile(0.75) <= 1.5 and usable.abs().max() <= 2.5:
        numeric = numeric * 100.0

    return numeric


def format_month(value: Any) -> str:
    """Standardizes month value into full English name."""
    if pd.isna(value):
        return ""
    if isinstance(value, pd.Timestamp):
        return value.strftime("%B")

    text = str(value).strip()
    try:
        numeric_month = float(text)
        if numeric_month.is_integer() and 1 <= int(numeric_month) <= 12:
            months = {
                1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June",
                7: "July", 8: "August", 9: "September", 10: "October", 11: "November", 12: "December"
            }
            return months[int(numeric_month)]
    except Exception:
        pass

    month_map = {
        "jan": "January", "january": "January", "feb": "February", "february": "February",
        "mar": "March", "march": "March", "apr": "April", "april": "April",
        "may": "May", "jun": "June", "june": "June", "jul": "July", "july": "July",
        "aug": "August", "august": "August", "sep": "September", "september": "September",
        "oct": "October", "october": "October", "nov": "November", "november": "November",
        "dec": "December", "december": "December"
    }
    return month_map.get(text.lower(), text)


def get_status(value: float, green_threshold: float, yellow_threshold: float, higher_is_better: bool = True) -> str:
    """Evaluates performance zone status: Green, Yellow, or Red."""
    if pd.isna(value):
        return "Red"
    if higher_is_better:
        if value >= green_threshold:
            return "Green"
        elif value >= yellow_threshold:
            return "Yellow"
        else:
            return "Red"
    else:
        if value <= green_threshold:
            return "Green"
        elif value <= yellow_threshold:
            return "Yellow"
        else:
            return "Red"


def clean_and_transform_dataset(df_raw: pd.DataFrame) -> Tuple[pd.DataFrame, Optional[Dict[str, Any]]]:
    """
    Cleans raw dataframe, isolates individual SMO records from Grand Total summary rows,
    applies data types, and computes calculated dimensions.
    """
    df = standardize_columns(df_raw.copy())
    df = df.dropna(how="all").dropna(axis=1, how="all")

    if "SMO Name" not in df.columns:
        raise ValueError("Missing mandatory 'SMO Name' column in report.")

    # Clean text columns
    text_cols = ["SMO Name", "Route Name", "Region", "Zone", "Territory", "Distribution Name", "Status", "DoJ"]
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].apply(safe_text)

    # Separate Grand Total row if present
    total_summary = None
    # Detect rows where SMO Name is empty or contains "Total" / "Grand Total"
    is_total_row = (
        (df["SMO Name"] == "") |
        (df["SMO Name"].str.lower().str.contains(r"\btotal\b|\bgrand total\b|\bsum\b", na=False))
    )

    if is_total_row.any():
        total_rows = df[is_total_row]
        if not total_rows.empty:
            total_summary = total_rows.iloc[-1].to_dict()
        df = df[~is_total_row].copy()

    # If df is empty after removing total rows
    if df.empty:
        raise ValueError("No valid SMO records found in the dataset.")

    # Standardize numeric columns
    numeric_int_cols = [
        "SR#", "Territory ID", "Route id", "SMO Code", "Report Year",
        "Target", "Route Sale", "Sale (ORD Date) out pjp", "Outlets on Route",
        "H PJP Outlets", "Current PJP Outlets", "Plan Calls Per Week",
        "No. of Productive Unique Outlets", "Actual Call On Unique Outlets",
        "Plan Calls MTD", "Actual Calls MTD", "No. of Actual Un-Planned Calls",
        "No. of Productive Calls MTD", "No. of Ordered Cases", "No. of Delivered Cases",
        "No. of Un-Delivered Cases", "No. of Specific FLV Delivered Cases",
        "No. of Calls (PJP)", "No. of Calls within Radius (PJP)", "No. of Calls Out of Radius (PJP)"
    ]
    for col in numeric_int_cols:
        if col in df.columns:
            df[col] = numeric_series(df[col])

    # Percentage columns
    pct_cols = [
        "Ach.%", "Productive Unique Outlets %", "Call Comp. %",
        "No. of Actual Un-Planned Calls %", "Strike Rate %",
        "Delivered Cases %", "Flavour %", "GPS Accuracy % (PJP)"
    ]
    for col in pct_cols:
        if col in df.columns:
            df[col] = normalize_percentage_column(df[col])

    # Floating point averages
    float_cols = ["Working Days", "SKU Per Invoice", "Drop Size"]
    for col in float_cols:
        if col in df.columns:
            df[col] = numeric_series(df[col])

    # Format Month & Year
    if "Report Month" in df.columns:
        df["Report Month"] = df["Report Month"].apply(format_month)
    if "Report Year" in df.columns:
        df["Report Year"] = df["Report Year"].apply(lambda y: f"{int(y)}" if pd.notna(y) and str(y).replace(".0","").isdigit() else safe_text(y))

    # Calculate Derived Metrics
    if "Route Sale" in df.columns and "Target" in df.columns:
        df["Sales Variance"] = df["Route Sale"] - df["Target"]

    # Calculate Performance Tier
    def assign_tier(row):
        ach = row.get("Ach.%", np.nan)
        strike = row.get("Strike Rate %", np.nan)
        call = row.get("Call Comp. %", np.nan)
        if pd.isna(ach):
            return "Unrated"
        if ach >= 100.0 and (pd.isna(strike) or strike >= 75.0):
            return "Elite Champion"
        elif ach >= 85.0:
            return "On-Track Performer"
        elif ach >= 70.0:
            return "Watchlist"
        else:
            return "Critical Action Needed"

    df["Performance Tier"] = df.apply(assign_tier, axis=1)

    # Sort by Achievement % descending by default
    if "Ach.%" in df.columns:
        df = df.sort_values(by="Ach.%", ascending=False).reset_index(drop=True)

    return df, total_summary


def calculate_team_metrics(df: pd.DataFrame, thresholds: Dict[str, Tuple[float, float]]) -> Dict[str, Any]:
    """Computes comprehensive team rollups, averages, and distribution counts."""
    total_smos = len(df)
    total_target = df["Target"].sum() if "Target" in df.columns else 0
    total_sales = df["Route Sale"].sum() if "Route Sale" in df.columns else 0
    overall_team_ach = (total_sales / total_target * 100.0) if total_target > 0 else (df["Ach.%"].mean() if "Ach.%" in df.columns else 0.0)

    avg_working_days = df["Working Days"].mean() if "Working Days" in df.columns else 0.0
    avg_call_comp = df["Call Comp. %"].mean() if "Call Comp. %" in df.columns else 0.0
    avg_strike_rate = df["Strike Rate %"].mean() if "Strike Rate %" in df.columns else 0.0
    avg_gps_accuracy = df["GPS Accuracy % (PJP)"].mean() if "GPS Accuracy % (PJP)" in df.columns else 0.0
    avg_delivery_pct = df["Delivered Cases %"].mean() if "Delivered Cases %" in df.columns else 0.0
    avg_flavor_pct = df["Flavour %"].mean() if "Flavour %" in df.columns else 0.0
    avg_drop_size = df["Drop Size"].mean() if "Drop Size" in df.columns else 0.0
    avg_sku_invoice = df["SKU Per Invoice"].mean() if "SKU Per Invoice" in df.columns else 0.0

    # Zone distributions for Achievement
    ach_g, ach_y = thresholds.get("Achievement", (100.0, 85.0))
    ach_statuses = df["Ach.%"].apply(lambda v: get_status(v, ach_g, ach_y))
    green_count = (ach_statuses == "Green").sum()
    yellow_count = (ach_statuses == "Yellow").sum()
    red_count = (ach_statuses == "Red").sum()

    # Tier counts
    tier_counts = df["Performance Tier"].value_counts().to_dict()

    return {
        "total_smos": total_smos,
        "total_target": total_target,
        "total_sales": total_sales,
        "overall_team_ach": overall_team_ach,
        "avg_working_days": avg_working_days,
        "avg_call_comp": avg_call_comp,
        "avg_strike_rate": avg_strike_rate,
        "avg_gps_accuracy": avg_gps_accuracy,
        "avg_delivery_pct": avg_delivery_pct,
        "avg_flavor_pct": avg_flavor_pct,
        "avg_drop_size": avg_drop_size,
        "avg_sku_invoice": avg_sku_invoice,
        "green_count": int(green_count),
        "yellow_count": int(yellow_count),
        "red_count": int(red_count),
        "tier_counts": tier_counts
    }


def generate_smo_narrative(smo: pd.Series, team_stats: Dict[str, Any], thresholds: Dict[str, Tuple[float, float]]) -> Dict[str, Any]:
    """Generates exact standardized narrative paragraphs, identified low areas, and enhancement action plan."""
    name = safe_text(smo.get("SMO Name"), "The Sales Officer")
    route = safe_text(smo.get("Route Name"), "assigned route")
    month = safe_text(smo.get("Report Month"), "Reporting Period")
    year = safe_text(smo.get("Report Year"), "")
    period = f"{month} {year}".strip()

    days = float(smo.get("Working Days", 0) or 0)
    ach = float(smo.get("Ach.%", 0.0) or 0.0)
    target = float(smo.get("Target", 0) or 0)
    sales = float(smo.get("Route Sale", 0) or 0)
    calls = float(smo.get("Call Comp. %", 0.0) or 0.0)
    strike = float(smo.get("Strike Rate %", 0.0) or 0.0)
    delivery = float(smo.get("Delivered Cases %", 0.0) or 0.0)
    gps = float(smo.get("GPS Accuracy % (PJP)", 0.0) or 0.0)

    # Threshold values
    g_days, y_days = thresholds.get("Working Days", (18, 15))
    g_ach, y_ach = thresholds.get("Achievement", (100.0, 85.0))
    g_call, y_call = thresholds.get("Call Completion", (95.0, 85.0))
    g_strike, y_strike = thresholds.get("Strike Rate", (80.0, 65.0))
    g_del, y_del = thresholds.get("Delivered Cases", (90.0, 80.0))
    g_gps, y_gps = thresholds.get("GPS Accuracy", (90.0, 75.0))

    # Statuses
    days_st = get_status(days, g_days, y_days)
    ach_st = get_status(ach, g_ach, y_ach)
    call_st = get_status(calls, g_call, y_call)
    strike_st = get_status(strike, g_strike, y_strike)
    deliv_st = get_status(delivery, g_del, y_del)
    gps_st = get_status(gps, g_gps, y_gps)

    # Exact Standardized 6 Paragraphs
    p1 = f"This report summarizes {name}'s performance in {period} while working on the {route} route."
    p2 = f"{name} worked {days:.0f} days during the month, which places them in the {days_st.lower()} performance zone."
    p3 = f"In terms of results, their Achievement stood at {ach:.1f}%, resulting in a {ach_st.lower()} performance classification."
    p4 = f"Their Call Completion reached {calls:.1f}%, which falls within the {call_st.lower()} zone, while their Strike Rate of {strike:.1f}% placed them in the {strike_st.lower()} performance zone."
    p5 = f"On the delivery side, {name}'s Delivered Cases percentage was {delivery:.1f}%, resulting in a {deliv_st.lower()} classification."
    p6 = f"Lastly, their GPS Accuracy was {gps:.1f}%, which falls within the {gps_st.lower()} performance zone."

    narrative_paragraphs = [p1, p2, p3, p4, p5, p6]
    full_narrative = "\n\n".join(narrative_paragraphs)

    # Where are we getting low? (Identified Gaps)
    low_areas = []
    if ach_st == "Red":
        low_areas.append(f"Sales Achievement is critically low at {ach:.1f}% (Deficit: {g_ach - ach:.1f}% below target).")
    elif ach_st == "Yellow":
        low_areas.append(f"Sales Achievement is in yellow zone at {ach:.1f}% (Needs {g_ach - ach:.1f}% boost to reach green).")

    if strike_st == "Red":
        low_areas.append(f"Order Strike Rate is low at {strike:.1f}% (Only {strike:.1f}% of visited shops placed an order).")
    elif strike_st == "Yellow":
        low_areas.append(f"Strike Rate is moderate at {strike:.1f}% (Target: {g_strike:.0f}%).")

    if gps_st == "Red":
        low_areas.append(f"GPS Location Accuracy is critically low at {gps:.1f}% (Most check-ins are occurring outside the shop radius).")
    elif gps_st == "Yellow":
        low_areas.append(f"GPS Accuracy is {gps:.1f}% (Target: {g_gps:.0f}%).")

    if deliv_st == "Red":
        low_areas.append(f"Delivery Fulfillment is low at {delivery:.1f}% (Ordered cases are not getting fully delivered).")
    elif deliv_st == "Yellow":
        low_areas.append(f"Delivery Fulfillment is {delivery:.1f}% (Target: {g_del:.0f}%).")

    if call_st == "Red":
        low_areas.append(f"Shop Visit Completion is lagging at {calls:.1f}% (Scheduled route shops are being missed).")
    elif call_st == "Yellow":
        low_areas.append(f"Shop Visit Completion is {calls:.1f}% (Target: {g_call:.0f}%).")

    if days_st == "Red":
        low_areas.append(f"Field Working Days is low at {days:.0f} days (Required minimum: {g_days} days).")
    elif days_st == "Yellow":
        low_areas.append(f"Field Working Days is {days:.0f} days (Required full attendance: {g_days} days).")

    if not low_areas:
        low_areas.append("All primary metrics are performing within satisfactory green target standards.")

    # What to enhance (Actionable Coaching Plan)
    enhancement_actions = []
    if ach_st != "Green":
        enhancement_actions.append("Drive volume on high-demand core SKUs (Cola Next 1.5L / 500ml) and expand order booking per outlet.")
    if strike_st != "Green":
        enhancement_actions.append("Enhance sales pitch and store merchandising during visits to convert non-buying shops into active buyers.")
    if gps_st != "Green":
        enhancement_actions.append("Strictly ensure mobile GPS is active and complete order check-in directly at the retailer's physical storefront.")
    if deliv_st != "Green":
        enhancement_actions.append("Coordinate closely with distributor dispatch logistics to eliminate delivery drop-offs and out-of-stock cancellations.")
    if call_st != "Green":
        enhancement_actions.append("Follow the daily PJP route sequence systematically to ensure 100% of planned shops are visited.")
    if days_st != "Green":
        enhancement_actions.append("Maintain continuous daily field attendance across all scheduled working days.")

    if not enhancement_actions:
        enhancement_actions.append("Maintain outstanding field discipline and mentor junior sales officers across the territory.")

    # Strengths
    strengths = []
    if call_st == "Green":
        strengths.append(f"Excellent route discipline with {calls:.1f}% scheduled shop visits completed.")
    if ach_st == "Green":
        strengths.append(f"Target achieved successfully at {ach:.1f}% sales realization.")
    if strike_st == "Green":
        strengths.append(f"High conversion efficiency with a {strike:.1f}% strike rate.")
    if gps_st == "Green":
        strengths.append(f"Strong field compliance with {gps:.1f}% GPS radius accuracy.")
    if deliv_st == "Green":
        strengths.append(f"Reliable order fulfillment with {delivery:.1f}% delivered cases.")
    if days_st == "Green":
        strengths.append(f"Full field attendance with {days:.0f} working days.")

    if not strengths:
        strengths.append("Active on assigned route and maintaining regular sales reporting.")

    return {
        "narrative": full_narrative,
        "narrative_paragraphs": narrative_paragraphs,
        "low_areas": low_areas,
        "enhancement_actions": enhancement_actions,
        "strengths": strengths,
        "coaching_points": enhancement_actions,
        "statuses": {
            "Working Days": days_st,
            "Achievement": ach_st,
            "Call Completion": call_st,
            "Strike Rate": strike_st,
            "Delivered Cases": deliv_st,
            "GPS Accuracy": gps_st
        }
    }
