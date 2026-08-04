# LVMH × Tiffany & Co. Acquisition Impact Analysis

A data-driven business analytics case study evaluating the financial and strategic impact of **LVMH's US$15.8 billion acquisition of Tiffany & Co.**

This project combines **financial analysis, statistical hypothesis testing, competitor benchmarking, and time-series forecasting** to answer one key question:

> **Did the Tiffany acquisition create measurable value for LVMH?**

---

## Project Overview

LVMH completed the acquisition of Tiffany & Co. on **7 January 2021**, making it the largest acquisition in the company's history.

This project analyses financial performance before and after the acquisition using historical data from **2008–2025**, supported by statistical testing and forecasting techniques. The findings are presented in an interactive **Streamlit dashboard**.

---

## Key Objectives

- Evaluate LVMH's financial performance before and after the acquisition.
- Measure the impact on the Watches & Jewellery division.
- Test whether observed improvements are statistically significant.
- Benchmark LVMH against Richemont and Kering.
- Forecast Watches & Jewellery revenue through 2030.
- Provide strategic recommendations for investors.

---

# Dashboard

The dashboard consists of five analytical pages.
Access the dashboard using this link:
http://localhost:8501/

| Page | Description |
|------|-------------|
| Executive Overview | Acquisition summary, KPIs, revenue trends, Watches & Jewellery contribution |
| Financial Performance | Revenue growth, margin analysis, rolling CAGR |
| Acquisition Impact | Acquisition comparison, statistical testing, competitor benchmarking |
| Forecasting | Revenue forecasts using Linear Regression, CAGR and ARIMA |
| Investor View | Deal economics, category signals and strategic recommendations |

---

# Key Findings

- Group revenue increased from **€44.7B (2020)** to **€80.8B (2025)**.
- Watches & Jewellery contribution increased from approximately **7.5% to 14%** of group revenue.
- Operating margin improved from **20.17%** before acquisition to **24.99%** after acquisition.
- Statistical testing confirmed the operating margin improvement (**Welch's t-test, p = 0.0056**).
- Revenue growth improved but was **not statistically significant**, largely due to the exceptional post-COVID recovery in 2021.
- Forecasts suggest Watches & Jewellery revenue could reach **€12.5–13.3 billion by 2030**.

---

# Datasets

The project combines multiple datasets covering financial performance, acquisitions, competitors and forecasting.

| Dataset | Purpose |
|---------|---------|
| `lvmh_group_financials_2010_2025.csv` | Group revenue, operating profit and net profit |
| `lvmh_division_revenue_2008_2025.csv` | Revenue by business division |
| `lvmh_watches_jewelry_segment_2008_2025.csv` | Watches & Jewellery revenue |
| `tiffany_pnl_detail_2011_2020.csv` | Tiffany pre-acquisition financial statements |
| `lvmh_major_acquisitions.csv` | Major acquisition details |
| `acquisition_performance_summary.csv` | Post-acquisition comparison |
| `pre_acquisition_financials.csv` | Historical financial performance of acquisition targets |
| `competitor_group_comparison.csv` | LVMH vs Richemont vs Kering |
| `category_brand_mapping.csv` | Brand and category mapping |
| `category_performance_signals.csv` | Luxury category performance indicators |

---

# Methodology

The analysis combines descriptive, statistical and predictive techniques.

### Financial Analysis

- Revenue growth
- Operating margin
- Net profit margin
- Rolling 3-year CAGR

### Statistical Testing

- Welch's t-test
- Mann–Whitney U test

### Forecasting

- Linear Regression
- CAGR Extrapolation
- ARIMA (1,1,1)

---

# Libraries used

- Python
- Pandas
- NumPy
- SciPy
- Statsmodels
- Streamlit
- Plotly
- Matplotlib

# software's used
- Excel
- Python(Jupyter Notebook)
---

# Repository Structure

```
LVMH-X-Tiffany-co-acquisition-analysis/
│
├── app.py
├── analysis_engine.py
├── requirements.txt
│
├── pages/
│   ├── 2_Financial_Performance_Analysis.py
│   ├── 3_Acquisition_Impact_Analysis.py
│   ├── 4_Forecasting.py
│   └── 5_Investor_View.py
│
├── data/
│
└── README.md
```

---

# Run Locally

Clone the repository:

```bash
git clone https://github.com/sanjaikanna1111/LVMH-X-Tiffany-co-acquisition-analysis.git
```

Install dependencies:

```bash
pip install -r requirements.txt
```
Run the dashboard:

```bash
streamlit run app.py

# Limitations

- Limited post-acquisition observations (2021–2025).
- COVID-19 influenced post-acquisition performance.
- Some acquisition-level financial information is not publicly disclosed.
- Forecasts are based on historical trends and should be interpreted as scenarios rather than precise predictions.

---

# Author

**Sanjai Kanna**
a built in portfolio project using data analysis,business analysis and financial analysis
This project was developed as a portfolio case study demonstrating business analytics, financial analysis, statistical testing and forecasting using Python and Streamlit.
