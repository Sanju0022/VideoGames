# 🎮 Video Game Sales — Interactive Stakeholder Dashboard

An interactive Streamlit dashboard analyzing video game sales across genre, platform,
publisher, region and time — with an automated insight engine that scans genre × platform
× region × year permutations and surfaces the most stakeholder-relevant findings.

## ✨ Features

- **Live filters**: year range, genre, platform, publisher, region focus, min sales threshold
- **KPI row**: total sales, titles, top genre/platform/publisher, best-selling title
- **Auto-generated insights**: fastest-growing genre, regional genre mismatches (e.g. Japan vs
  North America), best platform×genre combo, publisher market concentration, platform
  lifecycle peaks, region correlation, Pareto (80/20) concentration of sales
- **5 tabs**:
  1. Trends Over Time (with moving-average smoothing)
  2. Regional Breakdown (share by region, genre×region stacked bars, correlation heatmap)
  3. Platform × Genre permutation heatmap + best avg-performing combos
  4. Publishers (top N by sales / title count / avg performance, genre focus heatmap)
  5. Data Explorer (searchable table, CSV export, correlation matrix, sales distribution)
- **Light & dark theme friendly**: no hardcoded backgrounds — all custom CSS uses
  Streamlit's theme CSS variables, and all Plotly charts use transparent backgrounds so
  they adapt automatically when you switch themes (⋮ menu → Settings → Theme).

## 📁 Project structure

```
vgsales-dashboard/
├── app.py                   # Main Streamlit app
├── generate_data.py          # Script that generated the sample dataset
├── data/
│   └── vgsales.csv           # Sample dataset (swap with the real Kaggle file if you want)
├── .streamlit/
│   └── config.toml           # Theme config
├── requirements.txt
├── .gitignore
└── README.md
```

## 🗂️ About the dataset

`data/vgsales.csv` is a **realistic synthetic dataset** (6,500 rows) generated to match
the structure and statistical patterns of Kaggle's popular
["Video Game Sales" dataset](https://www.kaggle.com/datasets/gregorut/videogamesales)
(same columns: `Rank, Name, Platform, Year, Genre, Publisher, NA_Sales, EU_Sales,
JP_Sales, Other_Sales, Global_Sales`). It includes realistic touches like heavy-tailed
sales distributions, platform release-year windows, publisher-genre affinities, and a
small amount of missing data.

**To use the real Kaggle data instead:**
1. Download `vgsales.csv` from Kaggle.
2. Replace `data/vgsales.csv` with the downloaded file (keep the same filename/columns).
3. Re-run the app — no code changes needed.

## 🚀 Run locally

```bash
git clone https://github.com/<your-username>/vgsales-dashboard.git
cd vgsales-dashboard
pip install -r requirements.txt
streamlit run app.py
```

The app will open at `http://localhost:8501`.

## ☁️ Deploy for free (Streamlit Community Cloud)

1. Push this repo to GitHub (see below).
2. Go to [share.streamlit.io](https://share.streamlit.io), sign in with GitHub.
3. Click **New app**, select this repo, branch `main`, main file path `app.py`.
4. Click **Deploy** — you'll get a public URL to share.

## 📤 Push to GitHub

```bash
cd vgsales-dashboard
git init
git add .
git commit -m "Initial commit: interactive video game sales dashboard"
git branch -M main
git remote add origin https://github.com/<your-username>/vgsales-dashboard.git
git push -u origin main
```

## 🛠️ Tech stack

- [Streamlit](https://streamlit.io/) — app framework
- [Plotly Express](https://plotly.com/python/plotly-express/) — interactive charts
- [pandas](https://pandas.pydata.org/) / [numpy](https://numpy.org/) — data wrangling & synthetic data generation

## 📌 Notes

- The insight engine (`build_insights()` in `app.py`) recalculates on every filter change —
  it's not hardcoded text, it's derived live from whatever slice of data you select.
- All charts use `min. sample size` guards (e.g. ≥3 titles per platform×genre combo) to
  avoid misleading spikes from tiny samples.
