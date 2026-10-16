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

#DEAL ECONOMIC
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

# CATEGORY SIGNALS
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

# ---- FORECAST Screenshot
st.markdown("### 2030 Revenue Outlook Screenshot (Watches & Jewelry)")
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

# RECOMMENDATIONS
st.markdown("### Executive Recommendations")
recs = [
    ("1. Focus more on Watches & Jewelry than the other divisions.",
     "This division has the highest long-term growth among LVMH’s businesses and Tiffany + Bulgari have both been called out by LVMH as strong performers. High jewelry in particular seems to be doing well."),

    ("2. Don’t assume margins will stay as high as 2021–2023.",
     "Operating margin was unusually strong after COVID and the Tiffany deal. It has already come down a bit. Planning around the longer-term average (around 18–21%) seems more realistic."),

    ("3. The Tiffany and Loro Piana deals look more successful than Belmond.",
     "LVMH has been able to talk about clear growth stories for Tiffany and Loro Piana. Belmond doesn’t have the same kind of public success story, so that difference is worth noticing for future deals."),

    ("4. Treat the 2030 forecast as a range, not a single number.",
     "The three methods (linear regression, CAGR, ARIMA) give different answers. With only about 15 years of data, a single point estimate would look more precise than the data really supports."),

    ("5. Keep an eye on Fashion & Leather Goods.",
     "It’s still LVMH’s biggest division by a long way, but it’s been the weakest recently. Even small changes there will move the whole group more than what happens in Watches & Jewelry."),
]


for title, body in recs:
    with st.container(border=True):
        st.markdown(f"**{title}**")
        st.write(body)
