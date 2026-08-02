import numpy as np
import pandas as pd
from scipy import stats
from sklearn.linear_model import LinearRegression

try:
    from statsmodels.tsa.arima.model import ARIMA
    ARIMA_AVAILABLE = True
except ImportError:
    ARIMA_AVAILABLE = False

DATA_DIR = "Data"

DIVISION_COLS = {
    "fashion_leather_goods": "Fashion & Leather Goods",
    "selective_retailing": "Selective Retailing",
    "perfumes_cosmetics": "Perfumes & Cosmetics",
    "wines_spirits": "Wines & Spirits",
    "watches_jewelry": "Watches & Jewelry",
}

TIFFANY_CLOSE_YEAR = 2021  # 7 Jan 2021


# ------------------------------------------------------------------
# DATA LOADING
# ------------------------------------------------------------------
def load_division_revenue(data_dir=DATA_DIR):
    df = pd.read_csv(f"{data_dir}/lvmh_division_revenue_2008_2025.csv")
    return df.sort_values("calendar_year").reset_index(drop=True)


def load_group_financials(data_dir=DATA_DIR):
    df = pd.read_csv(f"{data_dir}/lvmh_group_financials_2010_2025.csv")
    return df.sort_values("calendar_year").reset_index(drop=True)


def load_acquisition_summary(data_dir=DATA_DIR):
    return pd.read_csv(f"{data_dir}/acquisition_performance_summary.csv")


def load_pre_acquisition(data_dir=DATA_DIR):
    return pd.read_csv(f"{data_dir}/pre_acquisition_financials.csv")


def load_competitor_comparison(data_dir=DATA_DIR):
    return pd.read_csv(f"{data_dir}/competitor_group_comparison.csv")


def load_category_signals(data_dir=DATA_DIR):
    return pd.read_csv(f"{data_dir}/category_performance_signals.csv")


def load_category_mapping(data_dir=DATA_DIR):
    return pd.read_csv(f"{data_dir}/category_brand_mapping.csv")


def load_watches_jewelry_segment(data_dir=DATA_DIR):
    return pd.read_csv(f"{data_dir}/lvmh_watches_jewelry_segment_2008_2025.csv")


def load_tiffany_pnl(data_dir=DATA_DIR):
    return pd.read_csv(f"{data_dir}/tiffany_pnl_detail_2011_2020.csv")


def load_major_acquisitions(data_dir=DATA_DIR):
    return pd.read_csv(f"{data_dir}/lvmh_major_acquisitions.csv")
# ------------------------------------------------------------------
# 1. YoY REVENUE GROWTH, EVERY DIVISION
# ------------------------------------------------------------------
def compute_division_yoy_growth(div_df):
    """Returns a copy of div_df with a *_yoy_pct column for every division
    plus total_revenue_yoy_pct."""
    out = div_df.copy()
    cols = list(DIVISION_COLS.keys()) + ["total_revenue"]
    for col in cols:
        out[f"{col}_yoy_pct"] = out[col].pct_change().round(4) * 100
    return out


def yoy_long_format(div_df):
    """Long/tidy format for charting: year, division, revenue, yoy_pct."""
    yoy = compute_division_yoy_growth(div_df)
    rows = []
    for col, label in DIVISION_COLS.items():
        for _, r in yoy.iterrows():
            rows.append({
                "year": int(r.calendar_year),
                "division": label,
                "revenue_eur_m": r[col],
                "yoy_growth_pct": r[f"{col}_yoy_pct"],
            })
    return pd.DataFrame(rows)


# ------------------------------------------------------------------
# 2. OPERATING MARGIN / NET PROFIT MARGIN TRENDS
# ------------------------------------------------------------------
def compute_margin_trends(group_df):
    out = group_df.copy()
    out["operating_margin_pct"] = (
        out.operating_income_eur_billions / out.group_revenue_eur_billions * 100
    ).round(2)
    out["net_margin_pct"] = (
        out.net_profit_eur_billions / out.group_revenue_eur_billions * 100
    ).round(2)
    out["revenue_growth_pct"] = out.group_revenue_eur_billions.pct_change().round(4) * 100
    out["operating_profit_growth_pct"] = out.operating_income_eur_billions.pct_change().round(4) * 100
    out["net_profit_growth_pct"] = out.net_profit_eur_billions.pct_change().round(4) * 100
    return out


# ------------------------------------------------------------------
# 3. BEFORE vs AFTER TIFFANY — AVERAGE GROWTH COMPARISON
# ------------------------------------------------------------------
def before_after_summary(group_df):
    m = compute_margin_trends(group_df)
    before = m[m.period == "Before"].dropna(subset=["revenue_growth_pct"])
    after = m[m.period == "After"].dropna(subset=["revenue_growth_pct"])

    def block(d):
        return {
            "avg_revenue_growth_pct": round(d.revenue_growth_pct.mean(), 2),
            "avg_operating_margin_pct": round(d.operating_margin_pct.mean(skipna=True), 2),
            "avg_net_margin_pct": round(d.net_margin_pct.mean(skipna=True), 2),
            "avg_operating_profit_growth_pct": round(d.operating_profit_growth_pct.mean(skipna=True), 2),
            "avg_net_profit_growth_pct": round(d.net_profit_growth_pct.mean(skipna=True), 2),
            "n_years": len(d),
        }

    return {"before": block(before), "after": block(after)}


def watches_jewelry_before_after(div_df):
    """Same comparison, but specifically for the Watches & Jewelry division,
    split at the Tiffany close year."""
    yoy = compute_division_yoy_growth(div_df)
    before = yoy[(yoy.calendar_year < TIFFANY_CLOSE_YEAR) & (yoy.calendar_year >= 2011)]
    after = yoy[yoy.calendar_year >= TIFFANY_CLOSE_YEAR]
    before_g = before["watches_jewelry_yoy_pct"].dropna()
    after_g = after["watches_jewelry_yoy_pct"].dropna()
    return before_g, after_g


# ------------------------------------------------------------------
# 4. STATISTICAL TESTING — PRE vs POST PERFORMANCE
# ------------------------------------------------------------------
def run_statistical_tests(group_df, div_df):
    """
    Runs Welch's t-test (unequal variance, appropriate for small/unequal-n samples)
    and the non-parametric Mann-Whitney U test (robust to the non-normality you'd
    expect from an 9-vs-5-year annual series) on:
      (a) LVMH group revenue growth, Before vs After
      (b) LVMH operating margin, Before vs After
      (c) Watches & Jewelry YoY revenue growth, Before vs After Tiffany close

    Small-sample caveat: n=9 (Before) vs n=5 (After) for group-level tests, and
    similarly small for the division test. These results indicate directional
    signal, not statistical proof - said explicitly in every result dict below.
    """
    m = compute_margin_trends(group_df)
    before_rev = m[m.period == "Before"]["revenue_growth_pct"].dropna()
    after_rev = m[m.period == "After"]["revenue_growth_pct"].dropna()
    before_margin = m[m.period == "Before"]["operating_margin_pct"].dropna()
    after_margin = m[m.period == "After"]["operating_margin_pct"].dropna()
    wj_before, wj_after = watches_jewelry_before_after(div_df)

    def test_pair(a, b, label):
        if len(a) < 2 or len(b) < 2:
            return {"metric": label, "note": "insufficient sample size for testing", "n_before": len(a), "n_after": len(b)}
        t_stat, t_p = stats.ttest_ind(a, b, equal_var=False)
        try:
            u_stat, u_p = stats.mannwhitneyu(a, b, alternative="two-sided")
        except ValueError:
            u_stat, u_p = np.nan, np.nan
        return {
            "metric": label,
            "n_before": len(a), "n_after": len(b),
            "mean_before": round(a.mean(), 2), "mean_after": round(b.mean(), 2),
            "welch_t_stat": round(t_stat, 3), "welch_p_value": round(t_p, 4),
            "mannwhitney_u_stat": round(u_stat, 3) if not np.isnan(u_stat) else None,
            "mannwhitney_p_value": round(u_p, 4) if not np.isnan(u_p) else None,
            "significant_at_5pct": bool(t_p < 0.05),
            "caveat": "Small annual sample (n<10 per group) - treat as directional evidence, not proof.",
        }

    return {
        "group_revenue_growth": test_pair(before_rev, after_rev, "LVMH Group Revenue Growth (%)"),
        "group_operating_margin": test_pair(before_margin, after_margin, "LVMH Group Operating Margin (%)"),
        "watches_jewelry_yoy_growth": test_pair(wj_before, wj_after, "Watches & Jewelry YoY Revenue Growth (%)"),
    }


# ------------------------------------------------------------------
# 5. FORECASTING — WATCHES & JEWELRY REVENUE
# ------------------------------------------------------------------
def forecast_watches_jewelry(div_df, forecast_years=(2026, 2027, 2028, 2029, 2030)):
    """
    Two independent forecast methods, returned side by side:
      - Linear regression on the full 2008-2025 series
      - ARIMA(1,1,1) on the same series (falls back to (1,1,0) then (0,1,0) if the
        richer model fails to converge on this short series)
    Also returns a simple 5-year-CAGR extrapolation as a third reference point.
    """
    wj = div_df[["calendar_year", "watches_jewelry"]].dropna().sort_values("calendar_year")
    years = wj.calendar_year.values.astype(float)
    revenue = wj.watches_jewelry.values.astype(float)
    fy = np.array(forecast_years, dtype=float)

    # Linear regression
    lin = LinearRegression().fit(years.reshape(-1, 1), revenue)
    lin_forecast = lin.predict(fy.reshape(-1, 1))

    # CAGR extrapolation (last 5 actual years)
    last5 = wj.tail(5)
    cagr = (last5.watches_jewelry.iloc[-1] / last5.watches_jewelry.iloc[0]) ** (1 / (len(last5) - 1)) - 1
    cagr_forecast = [revenue[-1] * (1 + cagr) ** i for i in range(1, len(forecast_years) + 1)]

    # ARIMA
    arima_forecast = None
    arima_order_used = None
    if ARIMA_AVAILABLE:
        for order in [(1, 1, 1), (1, 1, 0), (0, 1, 0)]:
            try:
                model = ARIMA(revenue, order=order).fit()
                arima_forecast = model.forecast(steps=len(forecast_years))
                arima_order_used = order
                break
            except Exception:
                continue

    result = pd.DataFrame({
        "year": forecast_years,
        "linear_regression": np.round(lin_forecast, 0),
        "cagr_extrapolation": np.round(cagr_forecast, 0),
    })
    if arima_forecast is not None:
        result["arima"] = np.round(arima_forecast, 0)
        result["average_forecast"] = result[["linear_regression", "cagr_extrapolation", "arima"]].mean(axis=1).round(0)
    else:
        result["average_forecast"] = result[["linear_regression", "cagr_extrapolation"]].mean(axis=1).round(0)

    meta = {
        "arima_order": arima_order_used,
        "cagr_used_pct": round(cagr * 100, 2),
        "last_actual_year": int(wj.calendar_year.iloc[-1]),
        "last_actual_value": float(revenue[-1]),
    }
    return result, meta


# ------------------------------------------------------------------
# CONVENIENCE: rolling CAGR windows (used on Financial Performance page)
# ------------------------------------------------------------------
def rolling_cagr(series_df, value_col, year_col="calendar_year", window=3):
    df = series_df.dropna(subset=[value_col]).sort_values(year_col).reset_index(drop=True)
    records = []
    for i in range(window, len(df)):
        start, end = df.iloc[i - window], df.iloc[i]
        gap = end[year_col] - start[year_col]
        if gap <= 0:
            continue
        c = ((end[value_col] / start[value_col]) ** (1 / gap) - 1) * 100
        records.append({"end_year": int(end[year_col]), "cagr_pct": round(c, 2)})
    return pd.DataFrame(records)