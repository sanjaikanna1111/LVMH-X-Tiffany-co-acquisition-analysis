import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import analysis_engine as ae

st.set_page_config(
    page_title="LVMH x Tiffany | Executive Overview",
    page_icon="\U0001F48E",
    layout="wide",
)

NAVY = "#1F2937"
GOLD = "#8A6D3B"
CREAM = "#F2EFE9"
GREEN = "#2E7D5B"
RED = "#B3453D"

st.markdown(f"""
<style>
    .main {{ background-color: #FFFFFF; }}
    h1, h2, h3 {{ color: {NAVY}; }}
    .kpi-box {{
        background-color: {CREAM};
        border-left: 4px solid {GOLD};
        padding: 14px 18px;
        border-radius: 4px;
    }}
    .kpi-label {{ font-size: 13px; color: #555; text-transform: uppercase; letter-spacing: 0.5px; }}
    .kpi-value {{ font-size: 28px; font-weight: 700; color: {NAVY}; }}
    .kpi-sub {{ font-size: 13px; color: {GOLD}; }}
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_all():
    div = ae.load_division_revenue()
    group = ae.load_group_financials()
    acq = ae.load_acquisition_summary()
    seg = ae.load_watches_jewelry_segment()
    return div, group, acq, seg


div, group, acq, seg = load_all()
ba = ae.before_after_summary(group)

st.title("LVMH \u00d7 Tiffany & Co.")
st.subheader("Executive Overview \u2014 Acquisition Impact at a Glance")
st.caption("Data: LVMH annual results releases, Tiffany SEC 10-Ks (2017\u20132020), LVMH segment disclosures (2016\u20132025). "
           "Before = 2010\u20132020 \u00b7 After = 2021\u20132025, split at the 7 Jan 2021 deal close.")

st.divider()

# ---- KPI ROW ----
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f"""<div class="kpi-box"><div class="kpi-label">Deal Price</div>
    <div class="kpi-value">$15.8B</div>
    <div class="kpi-sub">Closed 7 Jan 2021 \u00b7 originally $16.2B (Nov 2019)</div></div>""", unsafe_allow_html=True)
with c2:
    latest_rev = group[group.calendar_year == 2025].group_revenue_eur_billions.values[0]
    st.markdown(f"""<div class="kpi-box"><div class="kpi-label">LVMH Group Revenue 2025</div>
    <div class="kpi-value">\u20ac{latest_rev:.1f}B</div>
    <div class="kpi-sub">vs \u20ac44.7B in 2020 (pre-deal)</div></div>""", unsafe_allow_html=True)
with c3:
    wj_share_2020 = 3356 / 44651 * 100
    wj_share_2021 = 8964 / 64215 * 100
    st.markdown(f"""<div class="kpi-box"><div class="kpi-label">W&J Share of Group Revenue</div>
    <div class="kpi-value">{wj_share_2020:.1f}% \u2192 {wj_share_2021:.1f}%</div>
    <div class="kpi-sub">Roughly doubled the year Tiffany joined</div></div>""", unsafe_allow_html=True)
with c4:
    st.markdown(f"""<div class="kpi-box"><div class="kpi-label">Tiffany High Jewelry (LVMH-disclosed)</div>
    <div class="kpi-value">Quadrupled</div>
    <div class="kpi-sub">Operating profit doubled \u00b7 LVMH FY2024 release</div></div>""", unsafe_allow_html=True)

st.write("")

# ---- BEFORE / AFTER SNAPSHOT ----
col_a, col_b = st.columns([2, 1])

with col_a:
    st.markdown("#### LVMH Group Revenue, 2010\u20132025")
    fig = go.Figure()
    before_df = group[group.period == "Before"]
    after_df = group[group.period == "After"]
    fig.add_trace(go.Bar(x=before_df.calendar_year, y=before_df.group_revenue_eur_billions,
                          name="Before Tiffany", marker_color=NAVY))
    fig.add_trace(go.Bar(x=after_df.calendar_year, y=after_df.group_revenue_eur_billions,
                          name="After Tiffany", marker_color=GOLD))
    fig.add_vline(x=2020.5, line_dash="dash", line_color=RED,
                  annotation_text="Deal closes 7 Jan 2021", annotation_position="top")
    fig.update_layout(height=380, showlegend=True, plot_bgcolor="white",
                       yaxis_title="Revenue (\u20acbn)", margin=dict(t=30, l=10, r=10, b=10))
    st.plotly_chart(fig, use_container_width=True)

with col_b:
    st.markdown("#### Before vs After \u2014 Averages")
    summary_df = pd.DataFrame({
        "Metric": ["Avg. revenue growth", "Avg. operating margin", "Avg. net margin"],
        "Before": [f"{ba['before']['avg_revenue_growth_pct']}%",
                    f"{ba['before']['avg_operating_margin_pct']}%",
                    f"{ba['before']['avg_net_margin_pct']}%"],
        "After": [f"{ba['after']['avg_revenue_growth_pct']}%",
                  f"{ba['after']['avg_operating_margin_pct']}%",
                  f"{ba['after']['avg_net_margin_pct']}%"],
    })
    st.dataframe(summary_df, hide_index=True, use_container_width=True)
    st.caption("Full statistical significance testing on these differences is on the "
               "**Acquisition Impact** page \u2014 the margin difference is statistically "
               "significant; the revenue growth difference is not, given the small sample.")

st.divider()

#Watches&jewelry segment trend
st.markdown("#### Watches & Jewelry Segment Revenue \u2014 Tiffany Joins in 2021")
fig2 = go.Figure()
colors = [RED if not incl or incl == "No" else (GOLD if incl == "Partial (from 7 Jan)" else GREEN)
          for incl in seg.tiffany_included]
fig2.add_trace(go.Bar(x=seg.calendar_year, y=seg.segment_revenue_eur_millions,
                       marker_color=colors,
                       text=seg.tiffany_included, textposition="none"))
fig2.update_layout(height=320, plot_bgcolor="white", yaxis_title="Segment revenue (\u20acm)",
                    margin=dict(t=20, l=10, r=10, b=10))
st.plotly_chart(fig2, use_container_width=True)
st.caption("Red = Tiffany not yet included \u00b7 Gold = partial year (deal closed 7 Jan 2021) \u00b7 "
           "Green = full year including Tiffany. Segment also includes Bulgari, TAG Heuer, Hublot, Zenith, Chaumet, Fred.")

st.divider()

#Acquisition_impcat_screenshot
st.markdown("#### How Tiffany Ranks Among LVMH's Major Acquisitions")
ranked = acq.dropna(subset=["performance_rank"]).sort_values("performance_rank")
cols = st.columns(len(ranked))
medals = ["\U0001F947", "\U0001F948", "\U0001F949", "4\uFE0F\u20E3"]
for i, (col, (_, row)) in enumerate(zip(cols, ranked.iterrows())):
    with col:
        st.markdown(f"### {medals[i]}")
        st.markdown(f"**{row.target}**")
        st.caption(f"Acquired {row.acquisition_year}")
        st.caption(row.verdict[:110] + "...")

st.info("Full acquisition-by-acquisition comparison, competitor benchmarking, and statistical "
        "testing is on the **Acquisition Impact Analysis** page. Forecasts are on the "
        "**Forecasting** page. Deal economics and category signals are on the **Investor View** page.")