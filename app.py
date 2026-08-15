"""
🎮 Video Game Sales — Interactive Stakeholder Dashboard
Author: Generated with Claude
Run: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from itertools import combinations

# ----------------------------------------------------------------------------
# PAGE CONFIG
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="Video Game Sales Dashboard",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------------------------------------------------------
# THEME-AGNOSTIC STYLING
# Uses Streamlit's CSS variables so it looks good in BOTH light & dark themes.
# We never hardcode white/black backgrounds — we rely on var(--...) tokens.
# ----------------------------------------------------------------------------
st.markdown("""
<style>
    .metric-card {
        background: var(--secondary-background-color);
        border: 1px solid rgba(128,128,128,0.25);
        border-radius: 14px;
        padding: 1.1rem 1.2rem;
        text-align: left;
    }
    .metric-label {
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        opacity: 0.65;
        margin-bottom: 0.25rem;
    }
    .metric-value {
        font-size: 1.7rem;
        font-weight: 700;
        line-height: 1.1;
    }
    .metric-delta {
        font-size: 0.82rem;
        opacity: 0.75;
        margin-top: 0.2rem;
    }
    .insight-card {
        background: var(--secondary-background-color);
        border-left: 4px solid #7C4DFF;
        border-radius: 10px;
        padding: 0.9rem 1.1rem;
        margin-bottom: 0.7rem;
    }
    .insight-title {
        font-weight: 700;
        font-size: 0.95rem;
        margin-bottom: 0.2rem;
    }
    .insight-body {
        font-size: 0.87rem;
        opacity: 0.85;
    }
    .section-header {
        font-size: 1.25rem;
        font-weight: 700;
        margin-top: 1.6rem;
        margin-bottom: 0.4rem;
        border-bottom: 2px solid rgba(128,128,128,0.25);
        padding-bottom: 0.3rem;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.6rem;
    }
</style>
""", unsafe_allow_html=True)

PLOTLY_TEMPLATE = "plotly"  # neutral template that adapts reasonably; colors set via config below

def style_fig(fig, height=420):
    """Apply a theme-agnostic style: transparent backgrounds so the app's
    own light/dark theme shows through, plus a consistent color sequence."""
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="var(--text-color)"),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
        margin=dict(l=10, r=10, t=50, b=10),
        colorway=px.colors.qualitative.Set2,
    )
    fig.update_xaxes(gridcolor="rgba(128,128,128,0.15)")
    fig.update_yaxes(gridcolor="rgba(128,128,128,0.15)")
    return fig

# ----------------------------------------------------------------------------
# DATA LOADING
# ----------------------------------------------------------------------------
@st.cache_data
def load_data(path="data/vgsales.csv"):
    df = pd.read_csv(path)
    df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
    df["Publisher"] = df["Publisher"].fillna("Unknown")
    df = df.dropna(subset=["Global_Sales"])
    return df

df_raw = load_data()

REGION_COLS = ["NA_Sales", "EU_Sales", "JP_Sales", "Other_Sales"]
REGION_LABELS = {"NA_Sales": "North America", "EU_Sales": "Europe",
                  "JP_Sales": "Japan", "Other_Sales": "Rest of World"}

# ----------------------------------------------------------------------------
# SIDEBAR — FILTERS
# ----------------------------------------------------------------------------
st.sidebar.title("🎮 Filters")
st.sidebar.caption("Slice the dataset — every chart & insight below reacts live.")

year_min = int(df_raw["Year"].min())
year_max = int(df_raw["Year"].max())
year_range = st.sidebar.slider("Release Year", year_min, year_max, (year_min, year_max))

all_genres = sorted(df_raw["Genre"].dropna().unique())
sel_genres = st.sidebar.multiselect("Genre", all_genres, default=all_genres)

all_platforms = sorted(df_raw["Platform"].dropna().unique())
sel_platforms = st.sidebar.multiselect("Platform", all_platforms, default=all_platforms)

top_publishers_list = df_raw.groupby("Publisher")["Global_Sales"].sum().sort_values(ascending=False).index.tolist()
sel_publishers = st.sidebar.multiselect("Publisher", top_publishers_list, default=top_publishers_list)

region_focus = st.sidebar.selectbox(
    "Region focus (for region-specific charts)",
    list(REGION_LABELS.values()),
    index=0,
)
region_focus_col = [k for k, v in REGION_LABELS.items() if v == region_focus][0]

min_sales = st.sidebar.slider("Minimum Global Sales (millions)", 0.0, float(df_raw["Global_Sales"].max()), 0.0, 0.1)

st.sidebar.markdown("---")
st.sidebar.caption("Built with Streamlit + Plotly · Data is a realistic synthetic sample modeled on the Kaggle Video Game Sales dataset.")

# apply filters
df = df_raw[
    (df_raw["Year"].between(year_range[0], year_range[1]) | df_raw["Year"].isna())
    & df_raw["Genre"].isin(sel_genres)
    & df_raw["Platform"].isin(sel_platforms)
    & df_raw["Publisher"].isin(sel_publishers)
    & (df_raw["Global_Sales"] >= min_sales)
].copy()

if df.empty:
    st.warning("No data matches the current filters. Try widening your selection.")
    st.stop()

# ----------------------------------------------------------------------------
# HEADER
# ----------------------------------------------------------------------------
st.title("🎮 Video Game Sales — Stakeholder Dashboard")
st.caption(
    f"Analyzing **{len(df):,}** titles across **{df['Platform'].nunique()}** platforms, "
    f"**{df['Genre'].nunique()}** genres and **{df['Publisher'].nunique()}** publishers "
    f"({int(df['Year'].min())}–{int(df['Year'].max())})."
)

# ----------------------------------------------------------------------------
# KPI ROW
# ----------------------------------------------------------------------------
total_global = df["Global_Sales"].sum()
total_titles = len(df)
avg_sales = df["Global_Sales"].mean()
top_game = df.loc[df["Global_Sales"].idxmax()]
top_genre = df.groupby("Genre")["Global_Sales"].sum().idxmax()
top_platform = df.groupby("Platform")["Global_Sales"].sum().idxmax()
top_publisher = df.groupby("Publisher")["Global_Sales"].sum().idxmax()

k1, k2, k3, k4, k5, k6 = st.columns(6)
kpi_data = [
    (k1, "Total Global Sales", f"{total_global:,.1f}M", "units sold"),
    (k2, "Titles Analyzed", f"{total_titles:,}", "games"),
    (k3, "Avg Sales / Title", f"{avg_sales:,.2f}M", "per game"),
    (k4, "Top Genre", top_genre, f"{df.groupby('Genre')['Global_Sales'].sum().max():,.1f}M"),
    (k5, "Top Platform", top_platform, f"{df.groupby('Platform')['Global_Sales'].sum().max():,.1f}M"),
    (k6, "Top Publisher", top_publisher[:16], f"{df.groupby('Publisher')['Global_Sales'].sum().max():,.1f}M"),
]
for col, label, value, delta in kpi_data:
    with col:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-delta">{delta}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown(f"🏆 **Best-selling title in current selection:** *{top_game['Name']}* "
            f"({top_game['Platform']}, {int(top_game['Year']) if pd.notna(top_game['Year']) else 'N/A'}) "
            f"— {top_game['Global_Sales']:.2f}M units")

# ----------------------------------------------------------------------------
# AUTOMATED INSIGHT ENGINE
# Calculates a battery of comparisons/permutations across Genre x Platform x
# Region x Year and surfaces the most notable findings for stakeholders.
# ----------------------------------------------------------------------------
def build_insights(data: pd.DataFrame) -> list[dict]:
    insights = []

    # 1. Fastest growing genre (year-over-year over last 5 available years)
    yearly_genre = data.dropna(subset=["Year"]).groupby(["Year", "Genre"])["Global_Sales"].sum().reset_index()
    if not yearly_genre.empty:
        years_sorted = sorted(yearly_genre["Year"].unique())
        if len(years_sorted) >= 2:
            recent_years = years_sorted[-5:] if len(years_sorted) >= 5 else years_sorted
            recent = yearly_genre[yearly_genre["Year"].isin(recent_years)]
            growth = []
            for genre, grp in recent.groupby("Genre"):
                grp = grp.sort_values("Year")
                if len(grp) >= 2 and grp["Global_Sales"].iloc[0] > 0:
                    pct = (grp["Global_Sales"].iloc[-1] - grp["Global_Sales"].iloc[0]) / grp["Global_Sales"].iloc[0] * 100
                    growth.append((genre, pct))
            if growth:
                growth.sort(key=lambda x: x[1], reverse=True)
                g, pct = growth[0]
                insights.append({
                    "title": f"📈 {g} is the fastest-growing genre",
                    "body": f"Sales for {g} changed by {pct:+.0f}% between {int(recent_years[0])} and {int(recent_years[-1])} — worth prioritizing in upcoming release planning."
                })
                g2, pct2 = growth[-1]
                if pct2 < 0:
                    insights.append({
                        "title": f"📉 {g2} is declining",
                        "body": f"{g2} sales fell {pct2:.0f}% over the same window — consider whether to keep investing here or pivot."
                    })

    # 2. Regional genre mismatch — where JP differs most from NA/EU
    region_genre = data.groupby("Genre")[REGION_COLS].sum()
    if not region_genre.empty:
        region_genre_share = region_genre.div(region_genre.sum(axis=0), axis=1)
        if "JP_Sales" in region_genre_share and "NA_Sales" in region_genre_share:
            diff = (region_genre_share["JP_Sales"] - region_genre_share["NA_Sales"]).sort_values()
            if len(diff) > 0:
                over_index_jp = diff.idxmax()
                under_index_jp = diff.idxmin()
                insights.append({
                    "title": f"🌏 Japan over-indexes on {over_index_jp}",
                    "body": f"{over_index_jp} claims a much larger share of Japan's sales mix than North America's — localize marketing/regional allocation accordingly."
                })
                insights.append({
                    "title": f"🌎 North America over-indexes on {under_index_jp}",
                    "body": f"{under_index_jp} sells disproportionately better in North America than in Japan — a strong candidate for NA-focused marketing spend."
                })

    # 3. Best platform-genre combination (permutation scan)
    combo = data.groupby(["Platform", "Genre"])["Global_Sales"].agg(["sum", "count"]).reset_index()
    combo = combo[combo["count"] >= 3]  # avoid noise from tiny samples
    if not combo.empty:
        combo["avg"] = combo["sum"] / combo["count"]
        best_combo = combo.sort_values("avg", ascending=False).iloc[0]
        insights.append({
            "title": f"🎯 Best-performing combo: {best_combo['Genre']} on {best_combo['Platform']}",
            "body": f"Averages {best_combo['avg']:.2f}M units/title across {int(best_combo['count'])} titles — the strongest platform-genre fit in the current filter."
        })

    # 4. Publisher concentration (market share / Pareto check)
    pub_sales = data.groupby("Publisher")["Global_Sales"].sum().sort_values(ascending=False)
    if len(pub_sales) >= 3:
        top3_share = pub_sales.head(3).sum() / pub_sales.sum() * 100
        insights.append({
            "title": "🏢 Publisher concentration",
            "body": f"The top 3 publishers ({', '.join(pub_sales.head(3).index)}) account for {top3_share:.0f}% of total sales in this selection — a highly concentrated market."
        })

    # 5. Platform lifecycle peak
    plat_year = data.dropna(subset=["Year"]).groupby(["Platform", "Year"])["Global_Sales"].sum().reset_index()
    if not plat_year.empty:
        idx = plat_year.groupby("Platform")["Global_Sales"].idxmax()
        peaks = plat_year.loc[idx]
        if not peaks.empty:
            latest_peak = peaks.sort_values("Year", ascending=False).iloc[0]
            insights.append({
                "title": f"🕹️ {latest_peak['Platform']} peaked in {int(latest_peak['Year'])}",
                "body": f"That year generated {latest_peak['Global_Sales']:.1f}M in sales — the platform's strongest year in the current filter."
            })

    # 6. Region pair correlation (do regions move together?)
    region_totals = data.groupby("Year")[REGION_COLS].sum().dropna()
    if len(region_totals) >= 4:
        corr = region_totals.corr()
        pairs = list(combinations(REGION_COLS, 2))
        best_pair = max(pairs, key=lambda p: corr.loc[p[0], p[1]])
        worst_pair = min(pairs, key=lambda p: corr.loc[p[0], p[1]])
        insights.append({
            "title": f"🔗 {REGION_LABELS[best_pair[0]]} & {REGION_LABELS[best_pair[1]]} trend together",
            "body": f"Year-over-year sales correlation of {corr.loc[best_pair[0], best_pair[1]]:.2f} — demand patterns move in sync, useful for joint forecasting."
        })
        insights.append({
            "title": f"↔️ {REGION_LABELS[worst_pair[0]]} & {REGION_LABELS[worst_pair[1]]} diverge most",
            "body": f"Correlation of only {corr.loc[worst_pair[0], worst_pair[1]]:.2f} — these markets need independent regional strategies rather than a one-size-fits-all release plan."
        })

    # 7. Sales concentration (Pareto: what % of titles drive 80% of sales)
    sorted_sales = data["Global_Sales"].sort_values(ascending=False).reset_index(drop=True)
    cum = sorted_sales.cumsum() / sorted_sales.sum()
    if len(cum) > 0:
        n_titles_80 = (cum <= 0.8).sum() + 1
        pct_titles = n_titles_80 / len(sorted_sales) * 100
        insights.append({
            "title": "📊 Sales are highly concentrated",
            "body": f"Just {pct_titles:.0f}% of titles ({n_titles_80} games) generate 80% of total sales in this selection — a classic long-tail / hits-driven market."
        })

    return insights

insights = build_insights(df)

st.markdown('<div class="section-header">💡 Auto-Generated Insights</div>', unsafe_allow_html=True)
st.caption("Calculated live from the current filter selection across genre × platform × region × year permutations.")

if insights:
    ic1, ic2 = st.columns(2)
    for i, ins in enumerate(insights):
        target = ic1 if i % 2 == 0 else ic2
        with target:
            st.markdown(f"""
            <div class="insight-card">
                <div class="insight-title">{ins['title']}</div>
                <div class="insight-body">{ins['body']}</div>
            </div>
            """, unsafe_allow_html=True)
else:
    st.info("Not enough data in the current filter to generate insights. Try widening the filters.")

# ----------------------------------------------------------------------------
# TABS FOR DEEP DIVES
# ----------------------------------------------------------------------------
tab_overview, tab_region, tab_platform_genre, tab_publisher, tab_explorer = st.tabs(
    ["📈 Trends Over Time", "🌍 Regional Breakdown", "🎯 Platform × Genre", "🏢 Publishers", "🔍 Data Explorer"]
)

# --- TAB 1: TRENDS -----------------------------------------------------------
with tab_overview:
    c1, c2 = st.columns([2, 1])

    with c1:
        yearly = df.dropna(subset=["Year"]).groupby("Year")["Global_Sales"].sum().reset_index()
        fig = px.area(yearly, x="Year", y="Global_Sales", title="Global Sales Over Time",
                      labels={"Global_Sales": "Sales (millions)"})
        fig.update_traces(line_color="#7C4DFF", fillcolor="rgba(124,77,255,0.25)")
        st.plotly_chart(style_fig(fig), use_container_width=True)

    with c2:
        yearly_count = df.dropna(subset=["Year"]).groupby("Year").size().reset_index(name="Titles Released")
        fig2 = px.bar(yearly_count, x="Year", y="Titles Released", title="Titles Released per Year")
        fig2.update_traces(marker_color="#26A69A")
        st.plotly_chart(style_fig(fig2), use_container_width=True)

    genre_year = df.dropna(subset=["Year"]).groupby(["Year", "Genre"])["Global_Sales"].sum().reset_index()
    fig3 = px.line(genre_year, x="Year", y="Global_Sales", color="Genre",
                    title="Genre Sales Trends Over Time", labels={"Global_Sales": "Sales (millions)"})
    st.plotly_chart(style_fig(fig3, height=480), use_container_width=True)

    st.markdown("**Moving average smoothing** (helps spot true trend vs. noise)")
    window = st.slider("Smoothing window (years)", 1, 5, 3)
    smoothed = yearly.set_index("Year")["Global_Sales"].rolling(window, min_periods=1).mean().reset_index()
    fig4 = px.line(smoothed, x="Year", y="Global_Sales", title=f"{window}-Year Moving Average — Global Sales")
    fig4.update_traces(line_color="#FF7043", line_width=3)
    st.plotly_chart(style_fig(fig4), use_container_width=True)

# --- TAB 2: REGIONAL ----------------------------------------------------------
with tab_region:
    c1, c2 = st.columns(2)

    with c1:
        region_totals = df[REGION_COLS].sum().rename(index=REGION_LABELS).reset_index()
        region_totals.columns = ["Region", "Sales"]
        fig = px.pie(region_totals, names="Region", values="Sales", title="Global Sales Share by Region", hole=0.45)
        st.plotly_chart(style_fig(fig), use_container_width=True)

    with c2:
        region_genre = df.groupby("Genre")[REGION_COLS].sum().rename(columns=REGION_LABELS)
        region_genre_pct = region_genre.div(region_genre.sum(axis=1), axis=0) * 100
        fig = px.bar(region_genre_pct.reset_index().melt(id_vars="Genre", var_name="Region", value_name="Share %"),
                     x="Genre", y="Share %", color="Region", title="Regional Share of Sales by Genre (%)",
                     barmode="stack")
        fig.update_xaxes(tickangle=-40)
        st.plotly_chart(style_fig(fig), use_container_width=True)

    st.markdown(f"**Deep dive: {region_focus}**")
    c3, c4 = st.columns(2)
    with c3:
        top_in_region = df.groupby("Genre")[region_focus_col].sum().sort_values(ascending=False).reset_index()
        fig = px.bar(top_in_region, x="Genre", y=region_focus_col, title=f"Genre Ranking in {region_focus}",
                     labels={region_focus_col: "Sales (millions)"})
        fig.update_xaxes(tickangle=-40)
        st.plotly_chart(style_fig(fig), use_container_width=True)
    with c4:
        top_games_region = df.sort_values(region_focus_col, ascending=False).head(10)
        fig = px.bar(top_games_region, x=region_focus_col, y="Name", orientation="h",
                     title=f"Top 10 Titles in {region_focus}", labels={region_focus_col: "Sales (millions)"})
        fig.update_yaxes(autorange="reversed")
        st.plotly_chart(style_fig(fig), use_container_width=True)

    # region correlation heatmap
    st.markdown("**Regional demand correlation (year-over-year)**")
    region_totals_by_year = df.dropna(subset=["Year"]).groupby("Year")[REGION_COLS].sum()
    if len(region_totals_by_year) >= 3:
        corr = region_totals_by_year.rename(columns=REGION_LABELS).corr()
        fig = px.imshow(corr, text_auto=".2f", color_continuous_scale="Purples", title="Region Correlation Matrix")
        st.plotly_chart(style_fig(fig), use_container_width=True)
    else:
        st.info("Need more years in the current filter to compute correlation.")

# --- TAB 3: PLATFORM x GENRE (permutation matrix) ------------------------------
with tab_platform_genre:
    st.markdown("**Every Platform × Genre combination** — darker cells = higher total sales")
    matrix = df.pivot_table(index="Platform", columns="Genre", values="Global_Sales", aggfunc="sum", fill_value=0)
    fig = px.imshow(matrix, text_auto=".1f", aspect="auto", color_continuous_scale="Viridis",
                    title="Sales Heatmap: Platform × Genre (millions)")
    st.plotly_chart(style_fig(fig, height=560), use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        platform_totals = df.groupby("Platform")["Global_Sales"].sum().sort_values(ascending=False).reset_index()
        fig = px.bar(platform_totals, x="Platform", y="Global_Sales", title="Total Sales by Platform",
                     labels={"Global_Sales": "Sales (millions)"})
        st.plotly_chart(style_fig(fig), use_container_width=True)
    with c2:
        genre_totals = df.groupby("Genre")["Global_Sales"].sum().sort_values(ascending=False).reset_index()
        fig = px.bar(genre_totals, x="Genre", y="Global_Sales", title="Total Sales by Genre",
                     labels={"Global_Sales": "Sales (millions)"}, color_discrete_sequence=["#26A69A"])
        fig.update_xaxes(tickangle=-40)
        st.plotly_chart(style_fig(fig), use_container_width=True)

    st.markdown("**Best average performance per title** (min. 3 titles in combo, avoids small-sample noise)")
    combo = df.groupby(["Platform", "Genre"])["Global_Sales"].agg(["sum", "count", "mean"]).reset_index()
    combo = combo[combo["count"] >= 3].sort_values("mean", ascending=False).head(15)
    combo.columns = ["Platform", "Genre", "Total Sales", "Title Count", "Avg Sales/Title"]
    st.dataframe(combo.style.format({"Total Sales": "{:.2f}", "Avg Sales/Title": "{:.2f}"}), use_container_width=True)

# --- TAB 4: PUBLISHERS ---------------------------------------------------------
with tab_publisher:
    top_n = st.slider("Show top N publishers", 5, 20, 10)
    pub_sales = df.groupby("Publisher")["Global_Sales"].sum().sort_values(ascending=False).head(top_n).reset_index()
    fig = px.bar(pub_sales, x="Global_Sales", y="Publisher", orientation="h",
                 title=f"Top {top_n} Publishers by Global Sales", labels={"Global_Sales": "Sales (millions)"})
    fig.update_yaxes(autorange="reversed")
    st.plotly_chart(style_fig(fig, height=500), use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        pub_titles = df.groupby("Publisher").size().sort_values(ascending=False).head(top_n).reset_index(name="Titles")
        fig = px.bar(pub_titles, x="Titles", y="Publisher", orientation="h", title=f"Top {top_n} Publishers by Title Count")
        fig.update_yaxes(autorange="reversed")
        st.plotly_chart(style_fig(fig), use_container_width=True)
    with c2:
        pub_avg = df.groupby("Publisher").agg(total=("Global_Sales", "sum"), count=("Global_Sales", "size"))
        pub_avg = pub_avg[pub_avg["count"] >= 3]
        pub_avg["avg"] = pub_avg["total"] / pub_avg["count"]
        pub_avg = pub_avg.sort_values("avg", ascending=False).head(top_n).reset_index()
        fig = px.bar(pub_avg, x="avg", y="Publisher", orientation="h",
                     title=f"Top {top_n} Publishers by Avg Sales/Title (min 3 titles)",
                     labels={"avg": "Avg Sales/Title (millions)"})
        fig.update_yaxes(autorange="reversed")
        st.plotly_chart(style_fig(fig), use_container_width=True)

    st.markdown("**Publisher genre focus** — where does each top publisher concentrate?")
    pub_genre = df[df["Publisher"].isin(pub_sales["Publisher"])].pivot_table(
        index="Publisher", columns="Genre", values="Global_Sales", aggfunc="sum", fill_value=0)
    fig = px.imshow(pub_genre, text_auto=".1f", aspect="auto", color_continuous_scale="Oranges",
                    title="Publisher × Genre Sales Heatmap")
    st.plotly_chart(style_fig(fig, height=500), use_container_width=True)

# --- TAB 5: DATA EXPLORER -------------------------------------------------------
with tab_explorer:
    st.markdown("**Full filtered dataset** — sortable, searchable")
    search = st.text_input("Search by title")
    display_df = df.sort_values("Global_Sales", ascending=False)
    if search:
        display_df = display_df[display_df["Name"].str.contains(search, case=False, na=False)]
    st.dataframe(
        display_df[["Rank", "Name", "Platform", "Year", "Genre", "Publisher"] + REGION_COLS + ["Global_Sales"]],
        use_container_width=True, height=450
    )
    st.download_button(
        "⬇️ Download filtered data as CSV",
        data=display_df.to_csv(index=False).encode("utf-8"),
        file_name="vgsales_filtered.csv",
        mime="text/csv",
    )

    st.markdown("**Correlation across numeric fields**")
    num_cols = REGION_COLS + ["Global_Sales", "Year"]
    corr = df[num_cols].corr()
    fig = px.imshow(corr, text_auto=".2f", color_continuous_scale="RdBu_r", zmin=-1, zmax=1,
                    title="Correlation Matrix (numeric fields)")
    st.plotly_chart(style_fig(fig), use_container_width=True)

    st.markdown("**Distribution of Global Sales** (log scale, since sales are long-tailed)")
    fig = px.histogram(df, x="Global_Sales", nbins=60, title="Global Sales Distribution")
    fig.update_yaxes(type="log")
    st.plotly_chart(style_fig(fig), use_container_width=True)

st.markdown("---")
st.caption("Dashboard built with Streamlit & Plotly. Dataset is a realistic synthetic sample modeled on the structure "
           "of Kaggle's 'Video Game Sales' dataset — swap in `data/vgsales.csv` with the real Kaggle file "
           "(same column names) to use live data.")
