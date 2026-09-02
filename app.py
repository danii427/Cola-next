"""
app.py - Cola Next SMO KPI Analyzer (Layman-Friendly & Intuitive)
Simple, clear sales performance intelligence designed for easy understanding by anyone.
"""

import streamlit as st
import pandas as pd
import numpy as np
import os
import re

# Import modular components
from theme import apply_custom_theme, render_hero_banner, render_kpi_card
from data_processor import (
    find_excel_header,
    clean_and_transform_dataset,
    calculate_team_metrics,
    generate_smo_narrative,
    get_status,
    safe_text
)
from visualizations import (
    create_smo_kpi_bar_chart,
    create_top_performers_bar,
    create_bottom_performers_bar,
    create_target_vs_sales_bar,
    create_zone_health_bar,
    create_order_delivery_bar,
    create_calls_bar
)
from pdf_generator import create_smo_pdf, generate_batch_pdf_zip
from excel_exporter import create_executive_excel_workbook


# ============================================================
# 1. APPLICATION SETUP & THEME
# ============================================================

st.set_page_config(
    page_title="Cola Next SMO KPI Analyzer",
    page_icon="🥤",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_custom_theme()


# ============================================================
# 2. STATE MANAGEMENT FOR FILE UPLOAD
# ============================================================

if "loaded_file" not in st.session_state:
    st.session_state["loaded_file"] = None
if "data_source_name" not in st.session_state:
    st.session_state["data_source_name"] = None


# ============================================================
# 3. SIDEBAR CONTROLS & THRESHOLDS
# ============================================================

with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 10px 0 16px 0;">
        <div style="font-size: 24px; font-weight: 800; color: #0b1e36;">🥤 COLA NEXT</div>
        <div style="font-size: 12px; font-weight: 600; color: #d8232a; text-transform: uppercase; letter-spacing: 1px;">SMO KPI Analyzer</div>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("📂 Upload Excel Report")
    
    sidebar_file = st.file_uploader(
        "Choose an SMO Excel file (.xlsx / .xls)",
        type=["xlsx", "xls"],
        key="sidebar_uploader",
        help="Upload your monthly sales Excel report."
    )

    if sidebar_file is not None:
        st.session_state["loaded_file"] = sidebar_file
        st.session_state["data_source_name"] = sidebar_file.name

    # Reset button if file is loaded
    if st.session_state["loaded_file"] is not None:
        if st.button("🔄 Clear / Upload Different File", use_container_width=True):
            st.session_state["loaded_file"] = None
            st.session_state["data_source_name"] = None
            st.rerun()

    st.divider()

    # ============================================================
    # SIDEBAR - KPI THRESHOLDS
    # ============================================================

    st.sidebar.header("KPI Performance Thresholds")
    st.sidebar.caption("Set the minimum values required for Green and Yellow performance.")

    # -------------------------
    # ACHIEVEMENT
    # -------------------------
    st.sidebar.subheader("Achievement %")
    achievement_green = st.sidebar.number_input(
        "Green ≥",
        min_value=0.0,
        max_value=200.0,
        value=100.0,
        step=1.0,
        key="achievement_green"
    )
    achievement_yellow = st.sidebar.number_input(
        "Yellow ≥",
        min_value=0.0,
        max_value=200.0,
        value=85.0,
        step=1.0,
        key="achievement_yellow"
    )

    # -------------------------
    # CALL COMPLETION
    # -------------------------
    st.sidebar.subheader("Call Completion %")
    call_green = st.sidebar.number_input(
        "Green ≥",
        min_value=0.0,
        max_value=100.0,
        value=95.0,
        step=1.0,
        key="call_green"
    )
    call_yellow = st.sidebar.number_input(
        "Yellow ≥",
        min_value=0.0,
        max_value=100.0,
        value=85.0,
        step=1.0,
        key="call_yellow"
    )

    # -------------------------
    # STRIKE RATE
    # -------------------------
    st.sidebar.subheader("Strike Rate %")
    strike_green = st.sidebar.number_input(
        "Green ≥",
        min_value=0.0,
        max_value=100.0,
        value=80.0,
        step=1.0,
        key="strike_green"
    )
    strike_yellow = st.sidebar.number_input(
        "Yellow ≥",
        min_value=0.0,
        max_value=100.0,
        value=65.0,
        step=1.0,
        key="strike_yellow"
    )

    # -------------------------
    # GPS ACCURACY
    # -------------------------
    st.sidebar.subheader("GPS Accuracy %")
    gps_green = st.sidebar.number_input(
        "Green ≥",
        min_value=0.0,
        max_value=100.0,
        value=90.0,
        step=1.0,
        key="gps_green"
    )
    gps_yellow = st.sidebar.number_input(
        "Yellow ≥",
        min_value=0.0,
        max_value=100.0,
        value=75.0,
        step=1.0,
        key="gps_yellow"
    )

    # -------------------------
    # DELIVERED CASES
    # -------------------------
    st.sidebar.subheader("Delivered Cases %")
    delivery_green = st.sidebar.number_input(
        "Green ≥",
        min_value=0.0,
        max_value=150.0,
        value=90.0,
        step=1.0,
        key="delivery_green"
    )
    delivery_yellow = st.sidebar.number_input(
        "Yellow ≥",
        min_value=0.0,
        max_value=150.0,
        value=80.0,
        step=1.0,
        key="delivery_yellow"
    )

    # -------------------------
    # WORKING DAYS
    # -------------------------
    st.sidebar.subheader("Working Days")
    days_green = st.sidebar.number_input(
        "Green ≥",
        min_value=0,
        max_value=31,
        value=18,
        step=1,
        key="days_green"
    )
    days_yellow = st.sidebar.number_input(
        "Yellow ≥",
        min_value=0,
        max_value=31,
        value=15,
        step=1,
        key="days_yellow"
    )

    thresholds = {
        "Achievement": (achievement_green, achievement_yellow),
        "Call Completion": (call_green, call_yellow),
        "Strike Rate": (strike_green, strike_yellow),
        "GPS Accuracy": (gps_green, gps_yellow),
        "Delivered Cases": (delivery_green, delivery_yellow),
        "Working Days": (days_green, days_yellow)
    }

    # Validate thresholds
    threshold_pairs = [
        ("Achievement", achievement_green, achievement_yellow),
        ("Call Completion", call_green, call_yellow),
        ("Strike Rate", strike_green, strike_yellow),
        ("GPS Accuracy", gps_green, gps_yellow),
        ("Delivered Cases", delivery_green, delivery_yellow),
        ("Working Days", days_green, days_yellow)
    ]

    threshold_error = False
    for name, green_th, yellow_th in threshold_pairs:
        if yellow_th > green_th:
            st.sidebar.error(f"{name}: Yellow threshold cannot be higher than Green.")
            threshold_error = True

    ach_green, ach_yellow = achievement_green, achievement_yellow
    del_green, del_yellow = delivery_green, delivery_yellow

    if threshold_error:
        st.stop()


# ============================================================
# 4. INITIAL SCREEN: ASK FOR EXCEL UPLOAD
# ============================================================

if st.session_state["loaded_file"] is None:
    # Display friendly welcome & upload prompt
    st.markdown("""
    <div style="background: linear-gradient(135deg, #0b1e36 0%, #16365c 100%); border-radius: 16px; padding: 36px; color: white; text-align: center; margin: 20px 0 30px 0; box-shadow: 0 10px 25px rgba(11,30,54,0.25);">
        <div style="font-size: 32px; font-weight: 800; margin-bottom: 8px;">🥤 Cola Next SMO KPI Analyzer</div>
        <div style="font-size: 16px; color: #94a3b8; max-width: 650px; margin: 0 auto 24px auto;">
            Easily analyze your Sales Management Officers (SMOs), track monthly targets, shop visits, delivery rates, and download executive PDF reports.
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_up1, col_up2 = st.columns([1.3, 0.9])

    with col_up1:
        st.markdown("### 📤 Step 1: Upload Your Excel KPI Report")
        st.markdown("Please upload your sales Excel file to generate the analysis.")

        main_uploader = st.file_uploader(
            "Drag and drop your Excel report here (.xlsx, .xls)",
            type=["xlsx", "xls"],
            key="main_page_uploader"
        )

        if main_uploader is not None:
            st.session_state["loaded_file"] = main_uploader
            st.session_state["data_source_name"] = main_uploader.name
            st.rerun()

    with col_up2:
        st.markdown("### ⚡ Quick Demo / Test")
        st.markdown("Don't have an Excel file ready? You can test the analyzer with the sample July report.")
        
        sample_path = "SMO July Report.xlsx"
        if os.path.exists(sample_path):
            if st.button("▶️ Load Sample July Report", type="primary", use_container_width=True):
                st.session_state["loaded_file"] = sample_path
                st.session_state["data_source_name"] = "Sample July Report.xlsx"
                st.rerun()
        else:
            st.info("Upload an Excel file to see the analysis.")

    st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)
    
    # What the analyzer provides (Layman Guide)
    st.markdown("### 📖 What this tool analyzes for you:")
    g1, g2, g3 = st.columns(3)
    with g1:
        st.markdown("""
        **🎯 Sales Target Achievement**
        - Shows whether each salesperson met their monthly sales target.
        - Compares Target vs Actual Cases sold in simple bar charts.
        """)
    with g2:
        st.markdown("""
        **📞 Shop Visits & Orders**
        - Tracks how many scheduled shops were visited.
        - Shows the Strike Rate (percentage of visits resulting in orders).
        """)
    with g3:
        st.markdown("""
        **🚚 Delivery & Field Discipline**
        - Tracks successful order deliveries.
        - Verifies GPS check-ins at shop locations.
        - Generates 1-page printable PDF report cards.
        """)

    # STOP HERE until user provides file
    st.stop()


# ============================================================
# 5. PROCESS LOADED EXCEL FILE
# ============================================================

active_file = st.session_state["loaded_file"]

@st.cache_data(show_spinner="Reading and processing Excel file...")
def process_data(file_obj):
    try:
        excel_file = pd.ExcelFile(file_obj)
        detected_sheet, header_row = find_excel_header(excel_file)
        if detected_sheet is None or header_row is None:
            return None, "Could not find standard sales columns (like SMO Name, Target, Route Sale) in the uploaded Excel file."

        df_raw = pd.read_excel(excel_file, sheet_name=detected_sheet, header=header_row)
        df_clean, total_summary = clean_and_transform_dataset(df_raw)
        return df_clean, None
    except Exception as e:
        return None, str(e)

df_data, error_msg = process_data(active_file)

if error_msg or df_data is None:
    st.error(f"❌ Error loading Excel report: {error_msg}")
    st.info("Please make sure your Excel file contains recognizable sales headers such as 'SMO Name', 'Target', 'Route Sale', etc.")
    if st.button("Try Uploading Another File"):
        st.session_state["loaded_file"] = None
        st.rerun()
    st.stop()


# ============================================================
# 6. HEADER BANNER & GLOBAL FILTERS
# ============================================================

sample_row = df_data.iloc[0]
report_period = f"{sample_row.get('Report Month', '')} {sample_row.get('Report Year', '')}".strip() or "Monthly Report"
region_zone = f"{sample_row.get('Region', 'Lahore')} - {sample_row.get('Zone', 'New')}"

# Render Top Executive Banner
render_hero_banner(report_period=report_period, region_zone=region_zone, total_smos=len(df_data))

# Global Filters
with st.container():
    f1, f2, f3 = st.columns(3)
    with f1:
        dists = ["All Distributors"] + sorted([d for d in df_data["Distribution Name"].dropna().unique() if str(d).strip()])
        selected_dist = st.selectbox("Filter by Distributor:", dists, index=0)
    with f2:
        tiers = ["All Performance Levels"] + list(df_data["Performance Tier"].dropna().unique())
        selected_tier = st.selectbox("Filter by Performance Level:", tiers, index=0)
    with f3:
        sort_by = st.selectbox("Sort Table/Charts by:", ["Achievement % (High to Low)", "Sales Cases (High to Low)", "Strike Rate %", "Call Completion %"])

# Apply filters
filtered_df = df_data.copy()
if selected_dist != "All Distributors":
    filtered_df = filtered_df[filtered_df["Distribution Name"] == selected_dist]
if selected_tier != "All Performance Levels":
    filtered_df = filtered_df[filtered_df["Performance Tier"] == selected_tier]

if sort_by == "Achievement % (High to Low)":
    filtered_df = filtered_df.sort_values(by="Ach.%", ascending=False)
elif sort_by == "Sales Cases (High to Low)":
    filtered_df = filtered_df.sort_values(by="Route Sale", ascending=False)
elif sort_by == "Strike Rate %":
    filtered_df = filtered_df.sort_values(by="Strike Rate %", ascending=False)
elif sort_by == "Call Completion %":
    filtered_df = filtered_df.sort_values(by="Call Comp. %", ascending=False)

team_stats = calculate_team_metrics(filtered_df, thresholds)


# ============================================================
# 7. MULTI-TAB SIMPLE DASHBOARD
# ============================================================

tab_overview, tab_smo, tab_leaderboard, tab_distributor, tab_export = st.tabs([
    "🌟 1. Team Overview",
    "👤 2. Single SMO Performance",
    "🏆 3. All SMOs Ranking",
    "🗺️ 4. Distributor Sales",
    "📦 5. Download Reports (PDF & Excel)"
])


# ============================================================
# TAB 1: TEAM OVERVIEW (SIMPLE & EXPLAINED)
# ============================================================

with tab_overview:
    st.markdown("### 📊 Team Performance Summary")
    st.caption("Here is how the overall sales team performed during this period.")

    # 4 Main Cards
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(render_kpi_card(
            title="Total Sales Made",
            value=f"{team_stats['total_sales']:,} Cases",
            status="green" if team_stats["overall_team_ach"] >= ach_green else ("yellow" if team_stats["overall_team_ach"] >= ach_yellow else "red"),
            subtitle=f"Target: {team_stats['total_target']:,} Cases",
            icon="💰",
            target_text=f"Achieved: {team_stats['overall_team_ach']:.1f}%"
        ), unsafe_allow_html=True)

    with c2:
        st.markdown(render_kpi_card(
            title="Avg Shop Visits Done",
            value=f"{team_stats['avg_call_comp']:.1f}%",
            status="green" if team_stats["avg_call_comp"] >= call_green else ("yellow" if team_stats["avg_call_comp"] >= call_yellow else "red"),
            subtitle="Of Scheduled Shop Visits",
            icon="📞",
            target_text=f"Target: {call_green:.0f}%"
        ), unsafe_allow_html=True)

    with c3:
        st.markdown(render_kpi_card(
            title="Avg Order Success Rate",
            value=f"{team_stats['avg_strike_rate']:.1f}%",
            status="green" if team_stats["avg_strike_rate"] >= strike_green else ("yellow" if team_stats["avg_strike_rate"] >= strike_yellow else "red"),
            subtitle="Visits that got orders",
            icon="🎯",
            target_text=f"Target: {strike_green:.0f}%"
        ), unsafe_allow_html=True)

    with c4:
        st.markdown(render_kpi_card(
            title="Avg GPS Accuracy",
            value=f"{team_stats['avg_gps_accuracy']:.1f}%",
            status="green" if team_stats["avg_gps_accuracy"] >= gps_green else ("yellow" if team_stats["avg_gps_accuracy"] >= gps_yellow else "red"),
            subtitle="In-radius shop check-ins",
            icon="📍",
            target_text=f"Target: {gps_green:.0f}%"
        ), unsafe_allow_html=True)

    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

    # Simple Bar Charts with Explanations
    ch_col1, ch_col2 = st.columns(2)

    with ch_col1:
        st.plotly_chart(create_zone_health_bar(team_stats), key="chart_team_health_overview")
        st.info("""
        💡 **What this bar chart represents:**
        - **Green Bar:** Sales officers who **met or beat** their sales target (≥ 100%).
        - **Yellow Bar:** Sales officers with **average** achievement (85% to 99%).
        - **Red Bar:** Sales officers who are **below target** (< 85%) and need coaching support.
        """)

    with ch_col2:
        st.plotly_chart(create_target_vs_sales_bar(filtered_df), key="chart_team_target_vs_sales_bar")
        st.info("""
        💡 **What this bar chart represents:**
        - **Light Gray Bar:** The target sales quota (Goal).
        - **Dark Blue Bar:** Actual sales delivered/sold.
        - If the **blue bar is longer than the gray bar**, the territory achieved its target!
        """)

    st.divider()

    # Top & Bottom Performers Bar Charts
    st.markdown("### 🏆 Top Stars vs SMOs Needing Coaching")
    
    p_col1, p_col2 = st.columns(2)
    with p_col1:
        st.plotly_chart(create_top_performers_bar(filtered_df, top_n=8), key="chart_top_stars_bar")
        st.caption("🟢 **Green bars** = Met or exceeded 100% target. 🟡 **Yellow bars** = 85% to 99%.")
    with p_col2:
        st.plotly_chart(create_bottom_performers_bar(filtered_df, bot_n=8), key="chart_bottom_needs_coaching_bar")
        st.caption("🔴 **Red bars** = Below 85%. These officers need field help to improve sales.")


# ============================================================
# TAB 2: INDIVIDUAL SMO PERFORMANCE (CLEAR BAR CHARTS & EXPLANATIONS)
# ============================================================

with tab_smo:
    st.markdown("### 👤 Individual Sales Officer Performance")
    st.caption("Select any salesperson from the dropdown list below to see their detailed report and simple bar chart.")

    # Selector
    smo_options = []
    for idx, row in filtered_df.iterrows():
        name = safe_text(row.get("SMO Name", "Unknown"))
        r_name = safe_text(row.get("Route Name", ""))
        smo_options.append((f"{name} — Route: {r_name}", idx))

    smo_labels = [opt[0] for opt in smo_options]
    smo_map = {opt[0]: opt[1] for opt in smo_options}

    selected_label = st.selectbox("Select Sales Officer (SMO):", smo_labels, index=0, key="smo_profile_selector")
    selected_idx = smo_map[selected_label]
    smo_row = filtered_df.loc[selected_idx]

    # Generate narrative & statuses
    smo_narrative = generate_smo_narrative(smo_row, team_stats, thresholds)
    smo_statuses = smo_narrative["statuses"]

    smo_name = safe_text(smo_row.get("SMO Name"))
    r_name = safe_text(smo_row.get("Route Name"))
    smo_dist = safe_text(smo_row.get("Distribution Name"))
    smo_tier = safe_text(smo_row.get("Performance Tier", "Active"))
    smo_days = float(smo_row.get("Working Days", 0) or 0)

    # Clean Header Card
    st.markdown(f"""
    <div style="background: #f8fafc; border-radius: 12px; padding: 16px 20px; border: 1px solid #e2e8f0; margin: 10px 0 16px 0;">
        <div style="font-size: 20px; font-weight: 800; color: #0b1e36;">👤 {smo_name}</div>
        <div style="font-size: 13px; color: #64748b; margin-top: 4px;">
            <b>Assigned Route:</b> {r_name} &nbsp;|&nbsp; <b>Distributor:</b> {smo_dist} &nbsp;|&nbsp; <b>Active Field Days:</b> {smo_days:.0f} Days &nbsp;|&nbsp; <b>Status:</b> {smo_tier}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Simple Horizontal Bar Chart for this SMO
    st.plotly_chart(create_smo_kpi_bar_chart(smo_row, thresholds), key="chart_single_smo_scorecard")
    
    st.info("""
    💡 **What this bar chart represents:**
    - Each bar represents one key performance area for this sales officer.
    - **Green Bar:** Good performance (Met or exceeded target).
    - **Yellow Bar:** Acceptable performance (Close to target).
    - **Red Bar:** Underperforming (Needs improvement).
    - The vertical dashed line shows the standard **100% goal**.
    """)

    st.divider()

    # Two Simple Comparison Bar Charts for this SMO
    smo_c1, smo_c2 = st.columns(2)
    with smo_c1:
        st.plotly_chart(create_calls_bar(smo_row), key="chart_single_smo_calls")
        st.caption("Shows how many shop visits were planned (Gray), actually visited (Blue), and resulted in booked orders (Green).")
    with smo_c2:
        st.plotly_chart(create_order_delivery_bar(smo_row), key="chart_single_smo_delivery")
        st.caption("Shows total boxes ordered (Blue), successfully delivered (Green), and undelivered (Red).")

    st.divider()

    # Simple Plain English Summary & Coaching Tips
    st.markdown("### 📝 Diagnostic Performance Report & Action Plan")
    
    sum_c1, sum_c2 = st.columns([1.2, 0.8])
    with sum_c1:
        st.markdown("#### 📋 Performance Narrative")
        # Format the 6 paragraphs in clean, readable native Markdown
        for p in smo_narrative["narrative_paragraphs"]:
            st.markdown(f"> {p}")
            
        with st.expander("📄 View / Copy Plain Text Summary", expanded=False):
            st.text_area(
                "Full Performance Narrative Text:",
                value=smo_narrative["narrative"],
                height=180,
                key=f"text_summary_{selected_idx}"
            )

    with sum_c2:
        st.markdown("#### 🎯 Gaps & Action Plan")
        # Where are we getting low
        st.markdown("**📉 Where We Are Getting Low:**")
        for item in smo_narrative["low_areas"]:
            st.error(item, icon="🚨")

        # What to enhance
        st.markdown("**⚡ What To Enhance (Action Plan):**")
        for item in smo_narrative["enhancement_actions"]:
            st.success(item, icon="✅")

        # Key strengths if any
        if smo_narrative.get("strengths"):
            st.markdown("**🌟 Key Strengths:**")
            for item in smo_narrative["strengths"][:2]:
                st.info(item, icon="⭐")

    # Download 1-Page PDF
    try:
        pdf_bytes = create_smo_pdf(smo_row, smo_narrative, thresholds)
        safe_name = re.sub(r"[^A-Za-z0-9_-]+", "_", f"{smo_name}".strip("_"))
        st.download_button(
            label=f"📄 Download 1-Page PDF Report Card ({smo_name})",
            data=pdf_bytes,
            file_name=f"ColaNext_Report_{safe_name}.pdf",
            mime="application/pdf",
            key=f"btn_pdf_{selected_idx}"
        )
    except Exception as e:
        st.error(f"Could not generate PDF: {e}")


# ============================================================
# TAB 3: ALL SMOS RANKING TABLE
# ============================================================

with tab_leaderboard:
    st.markdown("### 🏆 Full Team Ranking Table")
    st.caption("Browse and compare all sales officers in a clean table.")

    display_df = filtered_df.copy().reset_index(drop=True)
    display_df["Rank"] = display_df.index + 1

    st.dataframe(
        display_df[[
            "Rank", "SMO Name", "Route Name", "Distribution Name",
            "Target", "Route Sale", "Ach.%", "Call Comp. %", "Strike Rate %",
            "Delivered Cases %", "GPS Accuracy % (PJP)", "Working Days", "Performance Tier"
        ]],
        column_config={
            "Rank": st.column_config.NumberColumn("Rank", format="#%d"),
            "Target": st.column_config.NumberColumn("Target (Cases)", format="%d"),
            "Route Sale": st.column_config.NumberColumn("Actual Sales (Cases)", format="%d"),
            "Ach.%": st.column_config.ProgressColumn("Achieved %", format="%.1f%%", min_value=0, max_value=150),
            "Call Comp. %": st.column_config.NumberColumn("Shop Visits %", format="%.1f%%"),
            "Strike Rate %": st.column_config.NumberColumn("Order Success %", format="%.1f%%"),
            "Delivered Cases %": st.column_config.NumberColumn("Delivery %", format="%.1f%%"),
            "GPS Accuracy % (PJP)": st.column_config.NumberColumn("GPS %", format="%.1f%%")
        },
        hide_index=True
    )


# ============================================================
# TAB 4: DISTRIBUTOR SALES
# ============================================================

with tab_distributor:
    st.markdown("### 🗺️ Distributor Sales Comparison")
    st.caption("Shows Target vs Actual Sales for each distributor.")

    st.plotly_chart(create_target_vs_sales_bar(filtered_df), key="chart_distributor_sales_target")

    if "Distribution Name" in filtered_df.columns:
        dist_table = filtered_df.groupby("Distribution Name").agg(
            Total_SMOs=("SMO Name", "count"),
            Target_Cases=("Target", "sum"),
            Actual_Sales_Cases=("Route Sale", "sum"),
            Avg_Achievement_Pct=("Ach.%", "mean"),
            Avg_Shop_Visits_Pct=("Call Comp. %", "mean")
        ).reset_index()

        st.dataframe(
            dist_table,
            column_config={
                "Target_Cases": st.column_config.NumberColumn("Target Cases", format="%d"),
                "Actual_Sales_Cases": st.column_config.NumberColumn("Actual Sales Cases", format="%d"),
                "Avg_Achievement_Pct": st.column_config.ProgressColumn("Avg Achievement %", format="%.1f%%", min_value=0, max_value=150),
                "Avg_Shop_Visits_Pct": st.column_config.NumberColumn("Avg Shop Visits %", format="%.1f%%")
            },
            hide_index=True
        )


# ============================================================
# TAB 5: DOWNLOAD REPORTS
# ============================================================

with tab_export:
    st.markdown("### 📦 Download Reports")
    st.caption("Export your reports in standard PDF or Excel formats.")

    exp_c1, exp_c2 = st.columns(2)

    with exp_c1:
        st.markdown("""
        <div class="section-box">
            <div style="font-size: 17px; font-weight: 700; color: #0b1e36; margin-bottom: 6px;">📄 Download All PDF Report Cards (ZIP)</div>
            <div style="font-size: 13px; color: #64748b; margin-bottom: 14px;">
                Generates a single ZIP file containing 1-page printable PDF report cards for all sales officers.
            </div>
        """, unsafe_allow_html=True)

        if st.button("Generate All PDFs (ZIP Archive)", type="primary", key="btn_gen_all_pdfs"):
            with st.spinner(f"Creating PDF report cards for {len(filtered_df)} sales officers..."):
                zip_data = generate_batch_pdf_zip(filtered_df, thresholds, team_stats)
                st.download_button(
                    label="⬇️ Click to Download All PDFs (.zip)",
                    data=zip_data,
                    file_name="ColaNext_All_SMO_Reports.zip",
                    mime="application/zip",
                    key="btn_download_all_zip"
                )
        st.markdown("</div>", unsafe_allow_html=True)

    with exp_c2:
        st.markdown("""
        <div class="section-box">
            <div style="font-size: 17px; font-weight: 700; color: #0b1e36; margin-bottom: 6px;">📊 Download Excel Workbook (.xlsx)</div>
            <div style="font-size: 13px; color: #64748b; margin-bottom: 14px;">
                Download a clean, organized Excel file containing the summary dashboard, rankings, and full dataset.
            </div>
        """, unsafe_allow_html=True)

        try:
            excel_bytes = create_executive_excel_workbook(filtered_df, team_stats, thresholds)
            st.download_button(
                label="⬇️ Click to Download Excel Workbook (.xlsx)",
                data=excel_bytes,
                file_name="ColaNext_Executive_Summary.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="btn_download_excel_sheet"
            )
        except Exception as ex_err:
            st.error(f"Excel export error: {ex_err}")

        st.markdown("</div>", unsafe_allow_html=True)