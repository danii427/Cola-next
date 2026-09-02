"""
pdf_generator.py - High-Resolution Executive PDF Engine for Cola Next SMO KPI Analyzer
Generates branded, print-ready A4 executive performance reports and bulk ZIP archives using ReportLab.
"""

from io import BytesIO
import zipfile
import re
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import Paragraph, SimpleDocTemplate, Table, TableStyle, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


def pdf_safe_text(value: Any) -> str:
    """Sanitizes text strings for ReportLab Latin-1 Helvetica font."""
    if pd.isna(value):
        return ""
    text = str(value).strip()
    if text.lower() in ["nan", "none", "nat", "null"]:
        return ""

    replacements = {
        "’": "'", "‘": "'", "“": '"', "”": '"',
        "–": "-", "—": "-", "•": "-", "…": "...",
        "₹": "Rs.", "€": "EUR", "£": "GBP", "\xa0": " "
    }
    for old, new in replacements.items():
        text = text.replace(old, new)

    return text.encode("latin-1", errors="replace").decode("latin-1")


def draw_fitted_text(
    pdf: canvas.Canvas,
    text: str,
    x: float,
    y: float,
    max_width: float,
    font_name: str,
    start_size: float,
    minimum_size: float = 7.0
) -> float:
    """Draws text scaled down if necessary to fit strictly within max_width."""
    text = pdf_safe_text(text)
    font_size = start_size
    while font_size > minimum_size:
        width = pdf.stringWidth(text, font_name, font_size)
        if width <= max_width:
            break
        font_size -= 0.5

    pdf.setFont(font_name, font_size)
    pdf.drawString(x, y, text)
    return font_size


def get_status_color(status: str) -> colors.HexColor:
    """Maps status zone to ReportLab HexColor."""
    if status == "Green":
        return colors.HexColor("#10B981")
    elif status == "Yellow":
        return colors.HexColor("#F59E0B")
    else:
        return colors.HexColor("#EF4444")


def create_smo_pdf(
    smo: pd.Series,
    narrative_data: Dict[str, Any],
    thresholds: Dict[str, Tuple[float, float]]
) -> bytes:
    """
    Generates a high-resolution, pixel-perfect A4 Executive KPI Report PDF for an SMO.
    """
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    page_width, page_height = A4

    # Palette
    c_navy = colors.HexColor("#0B1E36")
    c_crimson = colors.HexColor("#D8232A")
    c_dark_text = colors.HexColor("#1E293B")
    c_slate = colors.HexColor("#64748B")
    c_light_bg = colors.HexColor("#F8FAFC")
    c_border = colors.HexColor("#E2E8F0")

    # Margins
    margin_x = 36.0
    margin_top = 36.0
    usable_width = page_width - (margin_x * 2)

    # -------------------------------------------------------------
    # 1. HEADER BANNER
    # -------------------------------------------------------------
    banner_height = 68.0
    banner_y = page_height - margin_top - banner_height

    # Top Navy Banner Box
    pdf.setFillColor(c_navy)
    pdf.roundRect(margin_x, banner_y, usable_width, banner_height, 6, stroke=0, fill=1)

    # Crimson Accent Bar
    pdf.setFillColor(c_crimson)
    pdf.roundRect(margin_x, banner_y, 6, banner_height, 3, stroke=0, fill=1)

    # Brand Title
    pdf.setFillColor(colors.white)
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(margin_x + 18, banner_y + 42, "COLA NEXT - SMO PERFORMANCE DOSSIER")

    # Subtitle / Region & Period
    region = pdf_safe_text(smo.get("Region", "Lahore"))
    zone = pdf_safe_text(smo.get("Zone", "New"))
    dist = pdf_safe_text(smo.get("Distribution Name", "Distribution"))
    month = pdf_safe_text(smo.get("Report Month", "Monthly"))
    year = pdf_safe_text(smo.get("Report Year", ""))
    period = f"{month} {year}".strip()

    pdf.setFillColor(colors.HexColor("#94A3B8"))
    pdf.setFont("Helvetica", 9.5)
    pdf.drawString(margin_x + 18, banner_y + 24, f"Territory: {region} - {zone}  |  Distributor: {dist}")
    pdf.drawRightString(margin_x + usable_width - 18, banner_y + 24, f"Report Period: {period}")

    # -------------------------------------------------------------
    # 2. SMO PROFILE SUMMARY CARD
    # -------------------------------------------------------------
    profile_top = banner_y - 12.0
    profile_height = 58.0
    profile_y = profile_top - profile_height

    pdf.setFillColor(c_light_bg)
    pdf.setStrokeColor(c_border)
    pdf.setLineWidth(1)
    pdf.roundRect(margin_x, profile_y, usable_width, profile_height, 6, stroke=1, fill=1)

    smo_name = pdf_safe_text(smo.get("SMO Name", "N/A"))
    route_id = pdf_safe_text(smo.get("Route id", "N/A"))
    route_name = pdf_safe_text(smo.get("Route Name", "N/A"))
    tier = pdf_safe_text(smo.get("Performance Tier", "Active"))
    working_days = float(smo.get("Working Days", 0) or 0)

    # Name & Route
    pdf.setFillColor(c_navy)
    pdf.setFont("Helvetica-Bold", 13)
    pdf.drawString(margin_x + 14, profile_y + 36, f"{smo_name} (Route ID: {route_id})")

    pdf.setFillColor(c_slate)
    pdf.setFont("Helvetica", 9)
    pdf.drawString(margin_x + 14, profile_y + 18, f"Assigned Route: {route_name}  |  Active Working Days: {working_days:.0f} days")

    # Tier Badge on the right
    badge_width = 135.0
    badge_x = margin_x + usable_width - badge_width - 14
    pdf.setFillColor(colors.HexColor("#0B1E36"))
    pdf.roundRect(badge_x, profile_y + 16, badge_width, 26, 4, stroke=0, fill=1)
    pdf.setFillColor(colors.white)
    pdf.setFont("Helvetica-Bold", 9)
    pdf.drawCentredString(badge_x + (badge_width / 2), profile_y + 24, f"TIER: {tier.upper()}")

    # -------------------------------------------------------------
    # 3. SPLIT COLUMN LAYOUT (LEFT: Analysis & Coaching | RIGHT: KPIs)
    # -------------------------------------------------------------
    split_top = profile_y - 14.0
    left_width = usable_width * 0.52
    right_x = margin_x + left_width + 14.0
    right_width = usable_width - left_width - 14.0

    # ---------------- LEFT PANEL: NARRATIVE & COACHING ----------------
    pdf.setFillColor(c_navy)
    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(margin_x, split_top - 12, "PERFORMANCE ANALYSIS & DIAGNOSTICS")

    analysis_box_top = split_top - 20
    analysis_box_height = 145.0
    pdf.setFillColor(c_light_bg)
    pdf.setStrokeColor(c_border)
    pdf.roundRect(margin_x, analysis_box_top - analysis_box_height, left_width, analysis_box_height, 6, stroke=1, fill=1)

    # Draw Narrative Text Wrapped
    narrative_text = narrative_data.get("narrative", "")
    pdf.setFillColor(c_dark_text)
    pdf.setFont("Helvetica", 8.5)

    text_obj = pdf.beginText(margin_x + 10, analysis_box_top - 16)
    text_obj.setLeading(12)

    words = narrative_text.split()
    line = ""
    max_line_width = left_width - 20
    for w in words:
        test = f"{line} {w}".strip()
        if pdf.stringWidth(test, "Helvetica", 8.5) <= max_line_width:
            line = test
        else:
            text_obj.textLine(line)
            line = w
    if line:
        text_obj.textLine(line)
    pdf.drawText(text_obj)

    # Coaching Recommendations Box below Narrative
    coaching_top = analysis_box_top - analysis_box_height - 10.0
    coaching_height = 135.0

    pdf.setFillColor(c_navy)
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(margin_x, coaching_top - 10, "DIAGNOSTIC GAPS & ENHANCEMENT ACTION PLAN")

    pdf.setFillColor(colors.HexColor("#F0FDF4"))
    pdf.setStrokeColor(colors.HexColor("#BBF7D0"))
    pdf.roundRect(margin_x, coaching_top - 18 - coaching_height, left_width, coaching_height, 6, stroke=1, fill=1)

    coach_text_obj = pdf.beginText(margin_x + 10, coaching_top - 30)
    coach_text_obj.setLeading(11.5)

    # Where We Are Getting Low
    pdf.setFillColor(colors.HexColor("#991B1B"))
    coach_text_obj.setFont("Helvetica-Bold", 8)
    coach_text_obj.textLine("Where We Are Getting Low (Identified Deficits):")
    coach_text_obj.setFont("Helvetica", 7.5)
    for low_item in narrative_data.get("low_areas", [])[:2]:
        coach_text_obj.textLine(f"- {pdf_safe_text(low_item)}")

    coach_text_obj.textLine("")
    # What To Enhance
    pdf.setFillColor(colors.HexColor("#065F46"))
    coach_text_obj.setFont("Helvetica-Bold", 8)
    coach_text_obj.textLine("What To Enhance (Action Plan):")
    coach_text_obj.setFont("Helvetica", 7.5)
    for act_item in narrative_data.get("enhancement_actions", [])[:2]:
        coach_text_obj.textLine(f"+ {pdf_safe_text(act_item)}")

    pdf.drawText(coach_text_obj)

    # ---------------- RIGHT PANEL: CORE 6 KPI SCORECARDS ----------------
    pdf.setFillColor(c_navy)
    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(right_x, split_top - 12, "CORE KPI SCORECARDS")

    kpis_to_show = [
        ("Achievement %", f"{float(smo.get('Ach.%', 0) or 0):.1f}%", narrative_data["statuses"].get("Achievement", "Red"), f"Target: {smo.get('Target',0):,.0f} | Sales: {smo.get('Route Sale',0):,.0f}"),
        ("Call Completion %", f"{float(smo.get('Call Comp. %', 0) or 0):.1f}%", narrative_data["statuses"].get("Call Completion", "Red"), f"Planned: {smo.get('Plan Calls MTD',0):.0f} | Actual: {smo.get('Actual Calls MTD',0):.0f}"),
        ("Strike Rate %", f"{float(smo.get('Strike Rate %', 0) or 0):.1f}%", narrative_data["statuses"].get("Strike Rate", "Red"), f"Productive Calls: {smo.get('No. of Productive Calls MTD',0):.0f}"),
        ("Delivered Cases %", f"{float(smo.get('Delivered Cases %', 0) or 0):.1f}%", narrative_data["statuses"].get("Delivered Cases", "Red"), f"Delivered: {smo.get('No. of Delivered Cases',0):.0f} / {smo.get('No. of Ordered Cases',0):.0f}"),
        ("GPS Accuracy % (PJP)", f"{float(smo.get('GPS Accuracy % (PJP)', 0) or 0):.1f}%", narrative_data["statuses"].get("GPS Accuracy", "Red"), f"In Radius: {smo.get('No. of Calls within Radius (PJP)',0):.0f}"),
        ("Working Days", f"{working_days:.0f} Days", narrative_data["statuses"].get("Working Days", "Red"), f"Threshold Min: 18 Days")
    ]

    card_h = 44.0
    card_gap = 6.0
    curr_card_y = split_top - 20 - card_h

    for title, val_str, status, subtext in kpis_to_show:
        stat_color = get_status_color(status)

        # Card BG
        pdf.setFillColor(c_light_bg)
        pdf.setStrokeColor(c_border)
        pdf.roundRect(right_x, curr_card_y, right_width, card_h, 5, stroke=1, fill=1)

        # Left status indicator strip
        pdf.setFillColor(stat_color)
        pdf.roundRect(right_x, curr_card_y, 4.5, card_h, 2, stroke=0, fill=1)

        # Title
        pdf.setFillColor(c_slate)
        pdf.setFont("Helvetica-Bold", 8)
        pdf.drawString(right_x + 12, curr_card_y + 30, title.upper())

        # Subtext
        pdf.setFont("Helvetica", 7.5)
        pdf.drawString(right_x + 12, curr_card_y + 12, subtext)

        # Value & Status Badge on Right
        pdf.setFillColor(stat_color)
        pdf.setFont("Helvetica-Bold", 13)
        pdf.drawRightString(right_x + right_width - 12, curr_card_y + 24, val_str)

        pdf.setFont("Helvetica-Bold", 7.5)
        pdf.drawRightString(right_x + right_width - 12, curr_card_y + 12, f"[{status.upper()} ZONE]")

        curr_card_y -= (card_h + card_gap)

    # -------------------------------------------------------------
    # 4. FIELD EXECUTION & BASKET MATRIX (BOTTOM TABLE)
    # -------------------------------------------------------------
    bottom_y = 120.0
    bottom_height = 68.0

    pdf.setFillColor(c_navy)
    pdf.setFont("Helvetica-Bold", 10.5)
    pdf.drawString(margin_x, bottom_y + bottom_height + 4, "ROUTE EXECUTION & BASKET METRICS")

    # Table Grid
    pdf.setFillColor(c_light_bg)
    pdf.setStrokeColor(c_border)
    pdf.roundRect(margin_x, bottom_y, usable_width, bottom_height, 6, stroke=1, fill=1)

    exec_cols = [
        ("SKU Per Invoice", f"{float(smo.get('SKU Per Invoice', 0) or 0):.2f}"),
        ("Drop Size", f"{float(smo.get('Drop Size', 0) or 0):.1f}"),
        ("Outlets on Route", f"{smo.get('Outlets on Route', 0):.0f}"),
        ("Prod. Outlets %", f"{float(smo.get('Productive Unique Outlets %', 0) or 0):.1f}%"),
        ("Unplanned Calls %", f"{float(smo.get('No. of Actual Un-Planned Calls %', 0) or 0):.1f}%"),
        ("Market Time", pdf_safe_text(smo.get("AVG. Time in Market", "N/A"))[:8])
    ]

    col_w = usable_width / len(exec_cols)
    for i, (col_label, col_val) in enumerate(exec_cols):
        cx = margin_x + (i * col_w)
        pdf.setFillColor(c_slate)
        pdf.setFont("Helvetica-Bold", 7.5)
        pdf.drawCentredString(cx + (col_w / 2), bottom_y + 44, col_label.upper())

        pdf.setFillColor(c_navy)
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawCentredString(cx + (col_w / 2), bottom_y + 22, col_val)

        if i > 0:
            pdf.setStrokeColor(c_border)
            pdf.line(cx, bottom_y + 8, cx, bottom_y + bottom_height - 8)

    # -------------------------------------------------------------
    # 5. FOOTER & COMPLIANCE DISCLAIMER
    # -------------------------------------------------------------
    footer_y = 32.0
    pdf.setStrokeColor(c_border)
    pdf.line(margin_x, footer_y + 16, margin_x + usable_width, footer_y + 16)

    pdf.setFillColor(c_slate)
    pdf.setFont("Helvetica", 7.5)
    pdf.drawString(margin_x, footer_y + 4, "Confidential - Generated automatically by Cola Next SMO Performance Intelligence Platform.")
    pdf.drawRightString(margin_x + usable_width, footer_y + 4, "Cola Next Sales Management")

    pdf.showPage()
    pdf.save()
    buffer.seek(0)
    return buffer.getvalue()


def generate_batch_pdf_zip(
    df: pd.DataFrame,
    thresholds: Dict[str, Tuple[float, float]],
    team_stats: Dict[str, Any],
    selected_indices: Optional[List[int]] = None
) -> bytes:
    """
    Generates individual PDF dossiers for multiple SMOs and packages them into a ZIP archive.
    """
    if selected_indices is None:
        target_df = df
    else:
        target_df = df.loc[selected_indices]

    zip_buffer = BytesIO()

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for idx, row in target_df.iterrows():
            try:
                from data_processor import generate_smo_narrative
                narrative_data = generate_smo_narrative(row, team_stats, thresholds)
                pdf_bytes = create_smo_pdf(row, narrative_data, thresholds)

                smo_name = pdf_safe_text(row.get("SMO Name", f"SMO_{idx}"))
                route_id = pdf_safe_text(row.get("Route id", ""))
                clean_name = re.sub(r"[^A-Za-z0-9_-]+", "_", f"{smo_name}_{route_id}".strip("_"))
                filename = f"ColaNext_KPI_{clean_name}.pdf"

                zip_file.writestr(filename, pdf_bytes)
            except Exception as e:
                continue

    zip_buffer.seek(0)
    return zip_buffer.getvalue()
