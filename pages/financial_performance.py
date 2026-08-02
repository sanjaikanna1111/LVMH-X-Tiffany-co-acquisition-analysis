"""Page 2: Financial Performance Analysis"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

import analysis_engine as ae

st.set_page_config(page_title="Financial Performance | LVMH x Tiffany", page_icon="\U0001F4CA", layout="wide")

NAVY = "#1F2937"
GOLD = "#8A6D3B"

st.title("Financial Performance Analysis")
st.caption("YoY revenue growth by division \u00b7 operating & net margin trends \u00b7 rolling CAGR")


@st.cache_data
def load():
    div = ae.load_division_revenue()
    group = ae.load_group_financials()
    return div, group


div, group = load()
yoy_long = ae.yoy_long_format(div)
margins = ae.compute_margin_trends(group)

tab1, tab2, tab3 = st.tabs(["YoY Revenue Growth by Division", "Margin Trends", "Rolling CAGR"])

with tab1:
    st.markdown("#### Year-over-Year Revenue Growth, Every Division")
    divisions = sorted(yoy_long.division.unique())
    selected = st.multiselect("Divisions to show", divisions, default=divisions)
    filtered = yoy_long[yoy_long.division.isin(selected)].dropna(subset=["yoy_growth_pct"])

    fig = px.line(filtered, x="year", y="yoy_growth_pct", color="division", markers=True,
                  color_discrete_sequence=px.colors.qualitative.Set2)
    fig.add_hline(y=0, line_color="gray", line_dash="dot")
    fig.update_layout(height=450, plot_bgcolor="white", yaxis_title="YoY growth (%)",
                       legend_title="Division")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("##### Full YoY Growth Table (%)")
    pivot = filtered.pivot(index="year", columns="division", values="yoy_growth_pct").round(1)
    st.dataframe(pivot, use_container_width=True)

    st.markdown("""
    **Reading this chart:** Watches & Jewelry shows the two sharpest spikes in the whole
    dataset \u2014 2011 (Bulgari) and 2021 (Tiffany, though partly a COVID base-effect rebound).
    It also shows the deepest 2020 decline of any division (\u221223.8%), consistent with jewelry
    and watches being more discretionary purchases than, say, Perfumes & Cosmetics during a crisis.
    """)

with tab2:
    st.markdown("#### Operating Margin & Net Profit Margin, 2010\u20132025")
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=margins.calendar_year, y=margins.operating_margin_pct,
                               name="Operating margin", mode="lines+markers", line=dict(color=NAVY, width=3)))
    fig2.add_trace(go.Scatter(x=margins.calendar_year, y=margins.net_margin_pct,
                               name="Net margin", mode="lines+markers", line=dict(color=GOLD, width=3)))
    fig2.add_vrect(x0=2020.5, x1=2025.5, fillcolor=GOLD, opacity=0.08, line_width=0,
                   annotation_text="After Tiffany", annotation_position="top left")
    fig2.update_layout(height=420, plot_bgcolor="white", yaxis_title="Margin (%)")
    st.plotly_chart(fig2, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        st.metric("Peak operating margin", f"{margins.operating_margin_pct.max():.1f}%",
                   f"{int(margins.loc[margins.operating_margin_pct.idxmax(), 'calendar_year'])}")
    with c2:
        st.metric("2025 operating margin", f"{margins[margins.calendar_year==2025].operating_margin_pct.values[0]:.1f}%",
                   f"{margins[margins.calendar_year==2025].operating_margin_pct.values[0] - margins.operating_margin_pct.max():.1f}pp vs peak")

    st.markdown("""
    Margins peaked in 2021\u20132023 (the post-COVID reopening + Tiffany-integration window) and
    have compressed since \u2014 22.0% operating margin in 2025 vs. a 26.7% peak in 2021. This is a
    reversion toward the pre-COVID 2018\u20132019 range (~21%), not a collapse.
    """)

with tab3:
    st.markdown("#### Rolling 3-Year Revenue CAGR")
    roll = ae.rolling_cagr(group, "group_revenue_eur_billions", window=3)
    fig3 = px.bar(roll, x="end_year", y="cagr_pct", color="cagr_pct",
                  color_continuous_scale=["#B3453D", "#F2EFE9", "#2E7D5B"])
    fig3.update_layout(height=380, plot_bgcolor="white", yaxis_title="3-yr rolling CAGR (%)", coloraxis_showscale=False)
    st.plotly_chart(fig3, use_container_width=True)
    st.dataframe(roll, hide_index=True, use_container_width=True)
    st.caption("Each bar shows the CAGR of group revenue over the 3 years ending in that year. "
               "This smooths single-year noise (like the COVID crash or the Tiffany step-change) "
               "into a clearer momentum read.")