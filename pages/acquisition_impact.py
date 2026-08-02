"""Page 3: Acquisition Impact Analysis"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

import analysis_engine as ae

st.set_page_config(page_title="Acquisition Impact | LVMH x Tiffany", page_icon="\U0001F3AF", layout="wide")

NAVY = "#1F2937"
GOLD = "#8A6D3B"
GREEN = "#2E7D5B"
RED = "#B3453D"

st.title("Acquisition Impact Analysis")
st.caption("Cross-acquisition comparison \u00b7 statistical testing \u00b7 competitor benchmarking")


@st.cache_data
def load():
    div = ae.load_division_revenue()
    group = ae.load_group_financials()
    acq = ae.load_acquisition_summary()
    comp = ae.load_competitor_comparison()
    pre = ae.load_pre_acquisition()
    return div, group, acq, comp, pre


div, group, acq, comp, pre = load()

tab1, tab2, tab3 = st.tabs(["Acquisition Ranking", "Statistical Testing", "Competitor Benchmarking"])

with tab1:
    st.markdown("#### Post-Deal Performance, Ranked")
    ranked = acq.dropna(subset=["performance_rank"]).sort_values("performance_rank")

    fig = go.Figure(go.Bar(
        y=ranked.target, x=ranked.revenue_multiple, orientation="h",
        marker_color=[GREEN, GOLD, NAVY, RED],
        text=[f"{x}x" for x in ranked.revenue_multiple], textposition="outside",
    ))
    fig.update_layout(height=320, plot_bgcolor="white", xaxis_title="Disclosed / estimated revenue multiple since acquisition",
                       margin=dict(t=20, l=10, r=60, b=10))
    st.plotly_chart(fig, use_container_width=True)

    for _, row in ranked.iterrows():
        with st.expander(f"#{int(row.performance_rank)} \u2014 {row.target} (acquired {row.acquisition_year})"):
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"**Revenue:** {row.pre_deal_revenue} \u2192 {row.post_deal_revenue}")
                st.markdown(f"**Stores:** {row.pre_deal_stores} \u2192 {row.post_deal_stores} "
                            f"({row.store_change_pct:+.1f}%)" if pd.notna(row.store_change_pct) else "**Stores:** n/a")
            with c2:
                st.markdown(f"**Competitors:** {row.key_competitors}")
            st.write(row.verdict)

    dior = acq[acq.target == "Christian Dior Couture"].iloc[0]
    st.warning(f"**Not ranked \u2014 {dior.target} (2017):** {dior.verdict}")

with tab2:
    st.markdown("#### Statistical Testing: Pre- vs Post-Acquisition Performance")
    st.caption("Welch's t-test (unequal variance) + Mann-Whitney U (non-parametric, robust to small/non-normal samples). "
               "Both are shown because with n\u226410 per group, no single test should be trusted alone.")

    tests = ae.run_statistical_tests(group, div)

    for key, result in tests.items():
        st.markdown(f"##### {result['metric']}")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Mean, Before", f"{result['mean_before']}%")
        c2.metric("Mean, After", f"{result['mean_after']}%",
                   f"{result['mean_after'] - result['mean_before']:+.2f}pp")
        c3.metric("Welch's t-test p-value", f"{result['welch_p_value']}")
        c4.metric("Mann-Whitney p-value", f"{result['mannwhitney_p_value']}")

        if result["significant_at_5pct"]:
            st.success(f"Statistically significant at the 5% level (t = {result['welch_t_stat']}, "
                       f"n_before={result['n_before']}, n_after={result['n_after']}).")
        else:
            st.info(f"Not statistically significant at the 5% level (t = {result['welch_t_stat']}, "
                    f"n_before={result['n_before']}, n_after={result['n_after']}). "
                    "The directional difference may still be real, but the sample is too small "
                    "to rule out chance.")
        st.caption(result["caveat"])
        st.divider()

    st.markdown("""
    **Headline result:** the operating margin improvement (Before 20.3% \u2192 After 25.0%) IS
    statistically significant by both tests. Revenue growth and Watches & Jewelry YoY growth
    differences are directionally positive but **not** statistically significant \u2014 the 2021
    Tiffany-integration spike (+167%) is such a large outlier that it inflates the variance of
    the "After" sample enough to prevent significance despite a higher mean. This is an honest
    and fairly common result in small-sample M&A event studies, and it's a more defensible claim
    than reporting only the mean difference without testing it.
    """)

with tab3:
    st.markdown("#### LVMH vs Richemont vs Kering")
    st.dataframe(comp, hide_index=True, use_container_width=True)

    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        x=["LVMH (Watches & Jewelry)", "Richemont (Jewellery Maisons)"],
        y=[13.0, 71.5],
        marker_color=[NAVY, GOLD],
        text=["13.0%", "71.5%"], textposition="outside",
    ))
    fig2.update_layout(height=350, plot_bgcolor="white", yaxis_title="% of conglomerate total revenue",
                        title="Hard Luxury as Share of Total Revenue")
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("""
    Richemont is the sharper competitor comparison for the jewelry-specific question, since it
    is almost entirely a hard-luxury business. Richemont's Jewellery Maisons (Cartier, Van Cleef
    & Arpels) have compounded at roughly **+13% CAGR since 2010** \u2014 a real benchmark for
    whether LVMH's jewelry acquisitions are keeping pace with the category leader, not just
    growing in isolation.
    """)

    st.markdown("#### Pre-Acquisition Financial History (per target)")
    st.dataframe(pre, hide_index=True, use_container_width=True)
    st.caption("Tiffany is the only target with a clean, audited, multi-year pre-deal history "
               "(SEC 10-Ks are public). The others were private or thinly covered at deal time.")