"""Page 5: Investor View"""

import streamlit as st
import plotly.graph_objects as go

import analysis_engine as ae

st.set_page_config(page_title="Investor View | LVMH x Tiffany", page_icon="\U0001F4BC", layout="wide")

NAVY = "#1F2937"
GOLD = "#8A6D3B"
GREEN = "#2E7D5B"

st.title("Investor View")
st.caption("Deal economics \u00b7 category signals \u00b7 executive recommendations")


@st.cache_data
def load():
    div = ae.load_division_revenue()
    group = ae.load_group_financials()
    cat = ae.load_category_signals()
    catmap = ae.load_category_mapping()
    return div, group, cat, catmap


div, group, cat, catmap = load()
forecast_df, meta = ae.forecast_watches_jewelry(div)

# ---- DEAL ECONOMICS ----
st.markdown("### Deal Economics")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Original agreement (Nov 2019)", "$16.2B", "$135/share")
c2.metric("Final price (Oct 2020 renegotiation)", "$15.8B", "$131.50/share")
c3.metric("Closed", "7 Jan 2021")
c4.metric("Rank among LVMH deals", "#1 largest ever")

st.markdown("""
Financing was partly debt-funded \u2014 secondary reporting cites roughly \u20149\u201310bn in bonds issued
in 2020 at historically low rates (~2% average in 2021, rising toward ~3.6% by 2022 as rates
normalized).
""")

st.divider()

# ---- CATEGORY SIGNALS ----
st.markdown("### Category-Level Performance Signals")
st.caption("Only genuinely disclosed data points are shown here \u2014 no invented category splits.")
st.dataframe(cat[["category", "signal", "figure_or_direction"]], hide_index=True, use_container_width=True)

with st.expander("Category \u2192 Brand Mapping (which acquired brand sells what)"):
    st.dataframe(catmap[["category", "relevant_lvmh_division", "brands_in_this_category"]],
                 hide_index=True, use_container_width=True)
    st.caption("Correction worth keeping in mind: Tiffany, Bulgari, Loro Piana and Belmond do NOT "
               "sell skincare or makeup \u2014 those categories belong to different LVMH brands (Dior "
               "Beauty, Guerlain, Fenty) in a different division (Perfumes & Cosmetics).")

st.divider()

# ---- FORECAST SNAPSHOT ----
st.markdown("### 2030 Revenue Outlook Snapshot (Watches & Jewelry)")
final_row = forecast_df.iloc[-1]
method_cols = [c for c in ["linear_regression", "cagr_extrapolation", "arima"] if c in forecast_df.columns]
c1, c2 = st.columns([1, 2])
with c1:
    st.metric("Central 2030 estimate", f"\u20ac{final_row.average_forecast:,.0f}m",
               f"{(final_row.average_forecast / meta['last_actual_value'] - 1) * 100:+.1f}% vs 2025")
    st.caption(f"Range: \u20ac{final_row[method_cols].min():,.0f}m \u2013 \u20ac{final_row[method_cols].max():,.0f}m")
with c2:
    st.info("Full forecast detail, all methods, and the underlying reasoning is on the "
            "**Forecasting** page.")

st.divider()

# ---- EXECUTIVE RECOMMENDATIONS ----
st.markdown("### Executive Recommendations")

recs = [
    ("1. Back Watches & Jewelry specifically \u2014 not an even spread across divisions.",
     "It carries the highest 15-year CAGR of any LVMH division and the clearest repeated "
     "LVMH-disclosed brand success stories (Tiffany, Bulgari). Prioritize high jewelry lines "
     "within it, since that's the sub-category with the most explicit growth claims."),
    ("2. Don't budget off the 2021\u20132023 margin peak.",
     "Operating margin has already compressed ~5 points from its 2023 high toward pre-COVID "
     "norms (18\u201321%). Plan and guide toward that longer-run band, not the unusually strong "
     "post-COVID/Tiffany-integration window."),
    ("3. Repeat the Loro Piana / Tiffany acquisition playbook; reconsider the Belmond one.",
     "The clearest differentiator across LVMH's major deals is whether the company can later "
     "disclose a credible standalone growth story. Screen future M&A targets on that basis, "
     "alongside fit with the outperforming hard-luxury category."),
    ("4. Present any forecast as a range, not a point estimate.",
     "The three forecasting methods span a meaningful spread by 2030. A single confident "
     "number invites false precision that a ~15-point annual series cannot actually support."),
    ("5. Watch Fashion & Leather Goods as the bigger swing risk.",
     "It remains LVMH's largest division by far but is currently its weakest. Given its size, "
     "even a modest continued decline there would outweigh strong Watches & Jewelry growth at "
     "the total-group level \u2014 a bigger factor for LVMH's 2026\u20132030 trajectory than the "
     "acquisition this dashboard focuses on."),
]

for title, body in recs:
    with st.container(border=True):
        st.markdown(f"**{title}**")
        st.write(body)