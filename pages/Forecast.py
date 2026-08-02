"""Page 4: Forecasting — Watches & Jewelry Revenue"""

import streamlit as st
import plotly.graph_objects as go

import analysis_engine as ae

st.set_page_config(page_title="Forecasting | LVMH x Tiffany", page_icon="\U0001F52E", layout="wide")

NAVY = "#1F2937"
GOLD = "#8A6D3B"
GREEN = "#2E7D5B"
RED = "#B3453D"

st.title("Forecasting: Watches & Jewelry Revenue")
st.caption("Three independent methods, shown side by side \u2014 the spread between them IS the finding, "
           "not a modeling failure to hide.")


@st.cache_data
def load():
    return ae.load_division_revenue()


div = load()
forecast_df, meta = ae.forecast_watches_jewelry(div)
wj_actual = div[["calendar_year", "watches_jewelry"]].dropna()

years_out = st.slider("Forecast horizon (years)", 3, 5, 5)
forecast_display = forecast_df.head(years_out)

# ---- CHART ----
fig = go.Figure()
fig.add_trace(go.Scatter(x=wj_actual.calendar_year, y=wj_actual.watches_jewelry,
                          name="Actual", mode="lines+markers", line=dict(color=NAVY, width=3)))
fig.add_trace(go.Scatter(x=forecast_display.year, y=forecast_display.linear_regression,
                          name="Linear regression", mode="lines+markers", line=dict(color=GOLD, dash="dash")))
fig.add_trace(go.Scatter(x=forecast_display.year, y=forecast_display.cagr_extrapolation,
                          name="5-yr CAGR extrapolation", mode="lines+markers", line=dict(color=GREEN, dash="dot")))
if "arima" in forecast_display.columns:
    fig.add_trace(go.Scatter(x=forecast_display.year, y=forecast_display.arima,
                              name=f"ARIMA{meta['arima_order']}", mode="lines+markers", line=dict(color=RED, dash="dashdot")))
fig.add_trace(go.Scatter(x=forecast_display.year, y=forecast_display.average_forecast,
                          name="Average of methods", mode="lines+markers",
                          line=dict(color="black", width=3)))
fig.update_layout(height=480, plot_bgcolor="white", yaxis_title="Watches & Jewelry revenue (\u20acm)",
                   legend=dict(orientation="h", yanchor="bottom", y=1.02))
st.plotly_chart(fig, use_container_width=True)

# ---- TABLE ----
st.markdown("#### Forecast Table (EUR millions)")
st.dataframe(forecast_display, hide_index=True, use_container_width=True)

# ---- SPREAD METRICS ----
final_row = forecast_display.iloc[-1]
method_cols = [c for c in ["linear_regression", "cagr_extrapolation", "arima"] if c in forecast_display.columns]
spread_min = final_row[method_cols].min()
spread_max = final_row[method_cols].max()

c1, c2, c3 = st.columns(3)
c1.metric(f"{int(final_row.year)} \u2014 Low estimate", f"\u20ac{spread_min:,.0f}m")
c2.metric(f"{int(final_row.year)} \u2014 Central estimate", f"\u20ac{final_row.average_forecast:,.0f}m")
c3.metric(f"{int(final_row.year)} \u2014 High estimate", f"\u20ac{spread_max:,.0f}m")

st.markdown(f"""
**Method notes:**
- **Linear regression** fits the full {int(wj_actual.calendar_year.min())}\u2013{int(wj_actual.calendar_year.max())}
  trend, so the 2021 Tiffany step-change pulls this line up \u2014 the most bullish method here.
- **5-year CAGR extrapolation** uses only the last 5 actual years ({meta['cagr_used_pct']:+.1f}% CAGR),
  which includes the 2023\u20132025 flattening \u2014 a more moderate path.
- **ARIMA{meta['arima_order']}** models the series' own autocorrelation structure directly rather
  than assuming a fixed trend or growth rate \u2014 often the most conservative of the three on a
  series that has recently flattened.

This is a **10\u201318 point annual series** \u2014 genuinely small for time-series forecasting. Present
the range, not the average, in any board-facing material. The direction (continued growth) is
reasonably confident; the exact pace by {int(final_row.year)} is not.
""")

st.divider()
st.markdown("#### Underlying Data")
st.dataframe(wj_actual.rename(columns={"calendar_year": "Year", "watches_jewelry": "Revenue (\u20acm)"}),
             hide_index=True, use_container_width=True)