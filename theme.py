"""
theme.py - Premium UI/UX Design System for Cola Next SMO KPI Analyzer
Provides modern styles, CSS injection, custom metric cards, badges, and layout helpers.
"""

import streamlit as st

def apply_custom_theme():
    """Injects high-end modern CSS styling into the Streamlit application."""
    custom_css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* Main Container & Padding */
    .block-container {
        padding-top: 1.8rem;
        padding-bottom: 3.5rem;
        padding-left: 2.5rem;
        padding-right: 2.5rem;
        max-width: 100%;
    }

    /* Header Banner */
    .cola-hero-banner {
        background: linear-gradient(135deg, #0b1e36 0%, #16365c 50%, #0d233e 100%);
        border-radius: 16px;
        padding: 24px 32px;
        margin-bottom: 24px;
        color: #ffffff;
        box-shadow: 0 10px 25px -5px rgba(11, 30, 54, 0.3), 0 8px 10px -6px rgba(11, 30, 54, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.08);
        position: relative;
        overflow: hidden;
    }

    .cola-hero-banner::after {
        content: '';
        position: absolute;
        top: -50%;
        right: -10%;
        width: 300px;
        height: 300px;
        background: radial-gradient(circle, rgba(216, 35, 42, 0.25) 0%, rgba(216, 35, 42, 0) 70%);
        border-radius: 50%;
        pointer-events: none;
    }

    .cola-hero-title {
        font-size: 28px;
        font-weight: 800;
        letter-spacing: -0.5px;
        margin: 0;
        color: #ffffff;
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .cola-hero-subtitle {
        font-size: 14px;
        color: #94a3b8;
        margin-top: 6px;
        font-weight: 400;
    }

    .cola-tag {
        background: rgba(216, 35, 42, 0.2);
        color: #ff6b6b;
        border: 1px solid rgba(216, 35, 42, 0.4);
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* Metric Cards */
    .kpi-card {
        background: #ffffff;
        border-radius: 14px;
        padding: 18px 20px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.04), 0 1px 3px rgba(0, 0, 0, 0.02);
        border: 1px solid #e2e8f0;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        position: relative;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }

    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.08);
    }

    .kpi-card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;
    }

    .kpi-card-title {
        font-size: 13px;
        font-weight: 600;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .kpi-card-value {
        font-size: 32px;
        font-weight: 800;
        color: #0f172a;
        line-height: 1.1;
        margin-bottom: 8px;
    }

    .kpi-card-footer {
        display: flex;
        align-items: center;
        justify-content: space-between;
        font-size: 12px;
        color: #64748b;
        margin-top: auto;
        padding-top: 8px;
        border-top: 1px solid #f1f5f9;
    }

    /* Badges */
    .badge {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 0.3px;
    }

    .badge-green {
        background-color: #ecfdf5;
        color: #059669;
        border: 1px solid #a7f3d0;
    }

    .badge-yellow {
        background-color: #fffbeb;
        color: #d97706;
        border: 1px solid #fde68a;
    }

    .badge-red {
        background-color: #fef2f2;
        color: #dc2626;
        border: 1px solid #fecaca;
    }

    /* Tier Badges */
    .tier-badge {
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
    }

    .tier-elite {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
    }

    .tier-ontrack {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white;
    }

    .tier-watchlist {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        color: white;
    }

    .tier-critical {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        color: white;
    }

    /* Section Container */
    .section-box {
        background: #ffffff;
        border-radius: 14px;
        padding: 22px;
        margin-bottom: 20px;
        border: 1px solid #cbd5e1;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
        color: #0f172a;
    }

    /* Diagnostics Callout Box */
    .diagnostic-box {
        background-color: #ffffff;
        border-left: 6px solid #0b1e36;
        border-radius: 12px;
        padding: 20px 24px;
        margin: 14px 0;
        border-top: 1px solid #e2e8f0;
        border-right: 1px solid #e2e8f0;
        border-bottom: 1px solid #e2e8f0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.04);
        color: #0f172a;
    }

    .diagnostic-box p {
        color: #1e293b !important;
        font-size: 14px !important;
        line-height: 1.7 !important;
        margin-bottom: 14px !important;
    }

    .coaching-box {
        background-color: #f0fdf4;
        border-left: 6px solid #10b981;
        border-radius: 12px;
        padding: 16px 20px;
        margin: 12px 0;
        border-top: 1px solid #bbf7d0;
        border-right: 1px solid #bbf7d0;
        border-bottom: 1px solid #bbf7d0;
        color: #064e3b !important;
    }

    .alert-action-box {
        background-color: #fef2f2;
        border-left: 6px solid #ef4444;
        border-radius: 12px;
        padding: 16px 20px;
        margin: 12px 0;
        border-top: 1px solid #fecaca;
        border-right: 1px solid #fecaca;
        border-bottom: 1px solid #fecaca;
        color: #7f1d1d !important;
    }

    /* Dark Mode Compatibility */
    @media (prefers-color-scheme: dark) {
        .kpi-card, .section-box {
            background-color: #1e293b !important;
            border-color: #475569 !important;
            color: #f8fafc !important;
        }
        .kpi-card-value {
            color: #f8fafc !important;
        }
        .kpi-card-title, .kpi-card-footer {
            color: #cbd5e1 !important;
        }
        .stTabs [data-baseweb="tab-list"] {
            background-color: #1e293b !important;
        }
        .stTabs [data-baseweb="tab"] {
            color: #cbd5e1 !important;
        }
        .diagnostic-box {
            background-color: #1e293b !important;
            border-left-color: #60a5fa !important;
            border-color: #475569 !important;
            color: #f8fafc !important;
        }
        .diagnostic-box p {
            color: #f1f5f9 !important;
        }
        .coaching-box {
            background-color: #064e3b !important;
            border-left-color: #34d399 !important;
            border-color: #047857 !important;
            color: #ecfdf5 !important;
        }
        .coaching-box li, .coaching-box div {
            color: #ecfdf5 !important;
        }
        .alert-action-box {
            background-color: #7f1d1d !important;
            border-left-color: #f87171 !important;
            border-color: #991b1b !important;
            color: #fef2f2 !important;
        }
        .alert-action-box li, .alert-action-box div {
            color: #fef2f2 !important;
        }
    }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)


def render_hero_banner(report_period="July 2026", region_zone="LAHORE NEW", total_smos=43):
    """Renders the top executive brand banner."""
    st.markdown(f"""
    <div class="cola-hero-banner">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 16px;">
            <div>
                <div class="cola-hero-title">
                    <span>🥤 Cola Next SMO KPI Analyzer</span>
                    <span class="cola-tag">Enterprise Intelligence</span>
                </div>
                <div class="cola-hero-subtitle">
                    Target-Driven Sales Management & Route Execution Analytics • <b>{report_period}</b> • <b>{region_zone}</b>
                </div>
            </div>
            <div style="display: flex; gap: 12px; align-items: center;">
                <div style="background: rgba(255,255,255,0.1); backdrop-filter: blur(8px); padding: 8px 18px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.15); text-align: center;">
                    <div style="font-size: 11px; text-transform: uppercase; color: #94a3b8; font-weight: 600;">Active SMOs</div>
                    <div style="font-size: 20px; font-weight: 800; color: #ffffff;">{total_smos}</div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_kpi_card(title, value, status, subtitle="", icon="📊", target_text=""):
    """Returns HTML for a modern KPI scorecard card with status badge."""
    status_lower = status.lower()
    badge_class = f"badge-{status_lower}"
    
    color_map = {
        "green": "#10b981",
        "yellow": "#f59e0b",
        "red": "#ef4444"
    }
    color = color_map.get(status_lower, "#64748b")
    
    html = f"""
    <div class="kpi-card" style="border-top: 4px solid {color};">
        <div class="kpi-card-header">
            <span class="kpi-card-title">{icon} {title}</span>
            <span class="badge {badge_class}">{status.upper()}</span>
        </div>
        <div class="kpi-card-value" style="color: {color};">
            {value}
        </div>
        <div class="kpi-card-footer">
            <span>{subtitle}</span>
            <span style="font-weight: 600;">{target_text}</span>
        </div>
    </div>
    """
    return html
