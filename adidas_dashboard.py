import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Adidas US Sales Dashboard",
    page_icon="🏃",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── IBM Carbon-inspired CSS ───────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif;
}
.stApp { background-color: #161616; }

/* Top header band */
.dash-header {
    background: #262626;
    border-bottom: 1px solid #393939;
    padding: 1.25rem 0 1rem;
    margin-bottom: 1.5rem;
}
.dash-title {
    font-size: 22px;
    font-weight: 300;
    color: #f4f4f4;
    letter-spacing: 0.2px;
    margin: 0;
}
.dash-sub {
    font-size: 12px;
    color: #8d8d8d;
    margin-top: 4px;
}

/* KPI cards */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1px;
    background: #393939;
    border: 1px solid #393939;
    margin-bottom: 1.5rem;
}
.kpi-card {
    background: #262626;
    padding: 1rem 1.25rem;
    position: relative;
    overflow: hidden;
}
.kpi-accent {
    position: absolute;
    top: 0; left: 0;
    width: 3px; height: 100%;
}
.kpi-label {
    font-size: 11px;
    font-weight: 600;
    color: #8d8d8d;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 6px;
}
.kpi-value {
    font-size: 26px;
    font-weight: 300;
    color: #f4f4f4;
    letter-spacing: -0.5px;
    line-height: 1;
}
.kpi-unit {
    font-size: 12px;
    color: #8d8d8d;
    margin-top: 4px;
}
.kpi-delta-up { font-size: 12px; color: #42be65; margin-top: 5px; }
.kpi-delta-down { font-size: 12px; color: #fa4d56; margin-top: 5px; }

/* Section labels */
.section-label {
    font-size: 11px;
    font-weight: 600;
    color: #8d8d8d;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 10px;
    margin-top: 0;
}

/* Streamlit widget overrides */
div[data-testid="stHorizontalBlock"] { gap: 1px; }

/* Tabs styling */
.stTabs [data-baseweb="tab-list"] {
    background: #262626;
    border-bottom: 1px solid #393939;
    gap: 0;
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    color: #8d8d8d;
    font-size: 13px;
    font-weight: 500;
    letter-spacing: 0.3px;
    padding: 10px 20px;
    border-bottom: 2px solid transparent;
}
.stTabs [aria-selected="true"] {
    background: #262626 !important;
    color: #78a9ff !important;
    border-bottom: 2px solid #78a9ff !important;
}
.stTabs [data-baseweb="tab-panel"] {
    background: #161616;
    padding: 1.5rem 0 0;
}

/* Metric overrides */
[data-testid="metric-container"] {
    background: #262626;
    border: 1px solid #393939;
    padding: 1rem 1.25rem;
}
[data-testid="metric-container"] label {
    font-size: 11px !important;
    font-weight: 600 !important;
    color: #8d8d8d !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-size: 24px !important;
    font-weight: 300 !important;
    color: #f4f4f4 !important;
}
[data-testid="metric-container"] [data-testid="stMetricDelta"] {
    font-size: 12px !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #262626 !important;
    border-right: 1px solid #393939;
}
section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] .stRadio label {
    color: #c6c6c6 !important;
    font-size: 12px !important;
    letter-spacing: 0.5px;
}

/* Selectbox / radio */
div[data-baseweb="select"] > div {
    background: #262626 !important;
    border-color: #525252 !important;
    color: #f4f4f4 !important;
}
div[data-testid="stRadio"] > div {
    gap: 6px;
}
div[data-testid="stRadio"] label {
    color: #c6c6c6 !important;
    font-size: 13px !important;
}

/* Dataframe */
[data-testid="stDataFrame"] {
    border: 1px solid #393939 !important;
}
</style>
""", unsafe_allow_html=True)

# ── Carbon Plotly theme ───────────────────────────────────────────────────────
CARBON_COLORS = ["#0f62fe", "#1192e8", "#009d9a", "#198038", "#8a3ffc", "#ee538b", "#f1c21b", "#ff832b"]
PLOTLY_LAYOUT = dict(
    paper_bgcolor="#262626",
    plot_bgcolor="#262626",
    font=dict(family="IBM Plex Sans, sans-serif", color="#c6c6c6", size=11),
    margin=dict(l=12, r=12, t=32, b=12),
    legend=dict(
        bgcolor="#262626", bordercolor="#393939", borderwidth=1,
        font=dict(color="#c6c6c6", size=11),
    ),
    xaxis=dict(gridcolor="#393939", linecolor="#525252", tickcolor="#525252", zerolinecolor="#393939"),
    yaxis=dict(gridcolor="#393939", linecolor="#525252", tickcolor="#525252", zerolinecolor="#393939"),
    colorway=CARBON_COLORS,
)

def apply_carbon(fig, **overrides):
    layout = {**PLOTLY_LAYOUT, **overrides}
    fig.update_layout(**layout)
    return fig

# ── Load data ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("adidas_us_sales_cleaned.csv", parse_dates=["Invoice Date"])
    df["Year"] = df["Invoice Date"].dt.year
    df["Month"] = df["Invoice Date"].dt.month
    df["Month Name"] = df["Invoice Date"].dt.strftime("%b")
    df["Quarter"] = df["Invoice Date"].dt.to_period("Q").astype(str)
    return df

df = load_data()

# ── Sidebar filters ───────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🎛 Filters")
    st.markdown("---")

    years = sorted(df["Year"].unique())
    year_options = ["All Years"] + [str(y) for y in years]
    selected_year_label = st.selectbox("Year", year_options, index=1)

    regions = ["All Regions"] + sorted(df["Region"].unique())
    selected_region = st.selectbox("Region", regions)

    retailers = ["All Retailers"] + sorted(df["Retailer"].unique())
    selected_retailer = st.selectbox("Retailer", retailers)

    st.markdown("---")
    st.caption("Adidas US Sales · 2020–2021")

# ── Apply filters ─────────────────────────────────────────────────────────────
dff = df.copy()
if selected_year_label != "All Years":
    dff = dff[dff["Year"] == int(selected_year_label)]
if selected_region != "All Regions":
    dff = dff[dff["Region"] == selected_region]
if selected_retailer != "All Retailers":
    dff = dff[dff["Retailer"] == selected_retailer]

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="dash-header">
  <p class="dash-title">Adidas US Sales Analytics</p>
  <p class="dash-sub">IBM Carbon Design · All figures in USD · Source: Adidas US Sales Dataset</p>
</div>
""", unsafe_allow_html=True)

# ── KPI row ───────────────────────────────────────────────────────────────────
total_sales = dff["Total Sales"].sum()
total_profit = dff["Operating Profit"].sum()
total_units = dff["Units Sold"].sum()
avg_margin = dff["Operating Margin"].mean()

# Delta vs prior year (only when a single year is selected)
def get_delta(col, year):
    if selected_year_label == "All Years":
        return None
    prev = df[df["Year"] == year - 1]
    if selected_region != "All Regions":
        prev = prev[prev["Region"] == selected_region]
    if selected_retailer != "All Retailers":
        prev = prev[prev["Retailer"] == selected_retailer]
    if prev.empty or prev[col].sum() == 0:
        return None
    return (dff[col].sum() - prev[col].sum()) / prev[col].sum()

yr = int(selected_year_label) if selected_year_label != "All Years" else None
sales_delta = get_delta("Total Sales", yr) if yr else None
profit_delta = get_delta("Operating Profit", yr) if yr else None

def fmt_delta(v):
    if v is None:
        return None
    return f"{'+' if v >= 0 else ''}{v*100:.1f}%"

k1, k2, k3, k4 = st.columns(4)
with k1:
    st.metric("Total Revenue", f"${total_sales/1e6:.1f}M", delta=fmt_delta(sales_delta))
with k2:
    st.metric("Operating Profit", f"${total_profit/1e6:.1f}M", delta=fmt_delta(profit_delta))
with k3:
    st.metric("Units Sold", f"{total_units/1e3:.0f}K")
with k4:
    st.metric("Avg Op. Margin", f"{avg_margin*100:.1f}%")

st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

# ── Page tabs ─────────────────────────────────────────────────────────────────
tab_overview, tab_products, tab_channels, tab_geo = st.tabs(
    ["Overview", "Products", "Channels", "Geography"]
)

# ═══════════════════════════════════════════════════════════
# TAB 1 — OVERVIEW
# ═══════════════════════════════════════════════════════════
with tab_overview:

    # Monthly trend
    st.markdown('<p class="section-label">Monthly Revenue Trend</p>', unsafe_allow_html=True)

    metric_choice = st.radio(
        "Metric", ["Total Sales", "Operating Profit", "Units Sold"],
        horizontal=True, label_visibility="collapsed"
    )
    monthly = (
        dff.groupby(["Year", "Month", "Month Name"])[metric_choice]
        .sum().reset_index()
        .sort_values(["Year", "Month"])
    )
    monthly["Period"] = monthly["Month Name"] + " " + monthly["Year"].astype(str)

    fig_trend = px.line(
        monthly, x="Period", y=metric_choice,
        color="Year" if selected_year_label == "All Years" else None,
        markers=True,
        color_discrete_sequence=CARBON_COLORS,
    )
    fig_trend.update_traces(line_width=2, marker_size=5)
    fig_trend.update_xaxes(tickangle=45, tickfont_size=10)
    fig_trend.update_yaxes(tickprefix="" if metric_choice == "Units Sold" else "$",
                            tickformat=".2s")
    apply_carbon(fig_trend, height=280, margin=dict(l=12, r=12, t=12, b=60))
    st.plotly_chart(fig_trend, use_container_width=True)

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown('<p class="section-label">Revenue by Region</p>', unsafe_allow_html=True)
        region_df = dff.groupby("Region")["Total Sales"].sum().reset_index().sort_values("Total Sales", ascending=True)
        fig_reg = px.bar(
            region_df, x="Total Sales", y="Region", orientation="h",
            color="Region", color_discrete_sequence=CARBON_COLORS,
        )
        fig_reg.update_traces(width=0.55)
        fig_reg.update_xaxes(tickprefix="$", tickformat=".2s")
        fig_reg.update_layout(showlegend=False)
        apply_carbon(fig_reg, height=260)
        st.plotly_chart(fig_reg, use_container_width=True)

    with col_r:
        st.markdown('<p class="section-label">Revenue by Retailer</p>', unsafe_allow_html=True)
        retailer_df = dff.groupby("Retailer")["Total Sales"].sum().reset_index().sort_values("Total Sales", ascending=True)
        fig_ret = px.bar(
            retailer_df, x="Total Sales", y="Retailer", orientation="h",
            color="Retailer", color_discrete_sequence=CARBON_COLORS,
        )
        fig_ret.update_traces(width=0.55)
        fig_ret.update_xaxes(tickprefix="$", tickformat=".2s")
        fig_ret.update_layout(showlegend=False)
        apply_carbon(fig_ret, height=260)
        st.plotly_chart(fig_ret, use_container_width=True)

    # Quarterly heatmap
    st.markdown('<p class="section-label">Quarterly Revenue Heatmap</p>', unsafe_allow_html=True)
    q_df = dff.groupby(["Year", "Month"])["Total Sales"].sum().reset_index()
    q_pivot = q_df.pivot(index="Year", columns="Month", values="Total Sales").fillna(0)
    month_labels = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    fig_heat = go.Figure(go.Heatmap(
        z=q_pivot.values,
        x=[month_labels[m-1] for m in q_pivot.columns],
        y=[str(y) for y in q_pivot.index],
        colorscale=[[0,"#1a2a4a"],[0.5,"#0f62fe"],[1,"#78a9ff"]],
        hovertemplate="<b>%{x} %{y}</b><br>Revenue: $%{z:,.0f}<extra></extra>",
        showscale=True,
        colorbar=dict(tickprefix="$", tickformat=".2s", tickfont=dict(color="#8d8d8d")),
    ))
    apply_carbon(fig_heat, height=160, margin=dict(l=12, r=80, t=12, b=12))
    st.plotly_chart(fig_heat, use_container_width=True)


# ═══════════════════════════════════════════════════════════
# TAB 2 — PRODUCTS
# ═══════════════════════════════════════════════════════════
with tab_products:

    prod_df = (
        dff.groupby("Product")
        .agg(Revenue=("Total Sales","sum"), Profit=("Operating Profit","sum"), Units=("Units Sold","sum"))
        .reset_index()
        .sort_values("Revenue", ascending=False)
    )
    prod_df["Margin"] = prod_df["Profit"] / prod_df["Revenue"]
    prod_df["Revenue/Unit"] = prod_df["Revenue"] / prod_df["Units"]

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<p class="section-label">Revenue vs Profit by Product</p>', unsafe_allow_html=True)
        fig_prod = go.Figure()
        short = [p.replace("Men's","M's").replace("Women's","W's") for p in prod_df["Product"]]
        fig_prod.add_trace(go.Bar(
            name="Revenue", x=short, y=prod_df["Revenue"],
            marker_color="#0f62fe", opacity=0.85, width=0.35,
            offset=-0.2,
        ))
        fig_prod.add_trace(go.Bar(
            name="Profit", x=short, y=prod_df["Profit"],
            marker_color="#009d9a", opacity=0.85, width=0.35,
            offset=0.2,
        ))
        fig_prod.update_yaxes(tickprefix="$", tickformat=".2s")
        fig_prod.update_xaxes(tickangle=30, tickfont_size=10)
        apply_carbon(fig_prod, height=300, barmode="overlay")
        st.plotly_chart(fig_prod, use_container_width=True)

    with col2:
        st.markdown('<p class="section-label">Revenue Share by Product</p>', unsafe_allow_html=True)
        fig_donut = px.pie(
            prod_df, names="Product", values="Revenue",
            hole=0.62, color_discrete_sequence=CARBON_COLORS,
        )
        fig_donut.update_traces(
            textinfo="none",
            hovertemplate="<b>%{label}</b><br>$%{value:,.0f}<br>%{percent}<extra></extra>",
        )
        apply_carbon(fig_donut, height=300)
        st.plotly_chart(fig_donut, use_container_width=True)

    # Product detail table
    st.markdown('<p class="section-label">Product Detail</p>', unsafe_allow_html=True)
    display_df = prod_df.copy()
    display_df["Revenue"] = display_df["Revenue"].apply(lambda x: f"${x/1e6:.2f}M")
    display_df["Profit"] = display_df["Profit"].apply(lambda x: f"${x/1e6:.2f}M")
    display_df["Units"] = display_df["Units"].apply(lambda x: f"{x:,.0f}")
    display_df["Margin"] = display_df["Margin"].apply(lambda x: f"{x*100:.1f}%")
    display_df["Revenue/Unit"] = display_df["Revenue/Unit"].apply(lambda x: f"${x:.0f}")
    st.dataframe(
        display_df[["Product","Revenue","Profit","Units","Margin","Revenue/Unit"]],
        use_container_width=True, hide_index=True
    )

    # Margin bubble chart
    st.markdown('<p class="section-label">Margin vs Revenue/Unit (bubble = total units sold)</p>', unsafe_allow_html=True)
    raw_prod = (
        dff.groupby("Product")
        .agg(Revenue=("Total Sales","sum"), Profit=("Operating Profit","sum"), Units=("Units Sold","sum"))
        .reset_index()
    )
    raw_prod["Margin"] = raw_prod["Profit"] / raw_prod["Revenue"] * 100
    raw_prod["RevPerUnit"] = raw_prod["Revenue"] / raw_prod["Units"]
    fig_bubble = px.scatter(
        raw_prod, x="RevPerUnit", y="Margin", size="Units", color="Product",
        color_discrete_sequence=CARBON_COLORS,
        hover_data={"Revenue": ":,.0f", "Units": ":,.0f"},
        labels={"RevPerUnit": "Revenue per Unit ($)", "Margin": "Operating Margin (%)"},
    )
    fig_bubble.update_traces(marker_opacity=0.8)
    apply_carbon(fig_bubble, height=300)
    st.plotly_chart(fig_bubble, use_container_width=True)


# ═══════════════════════════════════════════════════════════
# TAB 3 — CHANNELS
# ═══════════════════════════════════════════════════════════
with tab_channels:

    ch_df = (
        dff.groupby("Sales Method")
        .agg(Revenue=("Total Sales","sum"), Profit=("Operating Profit","sum"), Units=("Units Sold","sum"))
        .reset_index()
    )
    ch_df["Margin"] = ch_df["Profit"] / ch_df["Revenue"]
    ch_df["RevPerUnit"] = ch_df["Revenue"] / ch_df["Units"]

    m1, m2, m3 = st.columns(3)
    for col_widget, row in zip([m1, m2, m3], ch_df.itertuples()):
        with col_widget:
            st.metric(
                row._1,
                f"${row.Revenue/1e6:.1f}M",
                f"{row.Units/1e3:.0f}K units · ${row.RevPerUnit:.0f}/unit"
            )

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown('<p class="section-label">Revenue & Profit by Channel</p>', unsafe_allow_html=True)
        fig_ch2 = px.bar(
            ch_df.melt(id_vars="Sales Method", value_vars=["Revenue","Profit"], var_name="Metric", value_name="USD"),
            x="Sales Method", y="USD", color="Metric", barmode="group",
            color_discrete_sequence=["#0f62fe","#009d9a"],
        )
        fig_ch2.update_yaxes(tickprefix="$", tickformat=".2s")
        apply_carbon(fig_ch2, height=260)
        st.plotly_chart(fig_ch2, use_container_width=True)

    with col_b:
        st.markdown('<p class="section-label">Units Sold by Channel</p>', unsafe_allow_html=True)
        fig_pie = px.pie(
            ch_df, names="Sales Method", values="Units",
            hole=0.55, color_discrete_sequence=["#0f62fe","#009d9a","#8a3ffc"],
        )
        fig_pie.update_traces(textinfo="none",
                              hovertemplate="<b>%{label}</b><br>%{value:,.0f} units<br>%{percent}<extra></extra>")
        apply_carbon(fig_pie, height=260)
        st.plotly_chart(fig_pie, use_container_width=True)

    # Channel over time
    st.markdown('<p class="section-label">Monthly Revenue by Channel</p>', unsafe_allow_html=True)
    ch_time = (
        dff.groupby(["Month","Month Name","Year","Sales Method"])["Total Sales"]
        .sum().reset_index().sort_values(["Year","Month"])
    )
    ch_time["Period"] = ch_time["Month Name"] + " " + ch_time["Year"].astype(str)
    fig_cht = px.line(
        ch_time, x="Period", y="Total Sales", color="Sales Method",
        markers=True, color_discrete_sequence=["#0f62fe","#009d9a","#8a3ffc"],
    )
    fig_cht.update_traces(line_width=2, marker_size=4)
    fig_cht.update_xaxes(tickangle=45, tickfont_size=9)
    fig_cht.update_yaxes(tickprefix="$", tickformat=".2s")
    apply_carbon(fig_cht, height=280, margin=dict(l=12,r=12,t=12,b=60))
    st.plotly_chart(fig_cht, use_container_width=True)


# ═══════════════════════════════════════════════════════════
# TAB 4 — GEOGRAPHY
# ═══════════════════════════════════════════════════════════
with tab_geo:

    col_g1, col_g2 = st.columns([3, 2])

    with col_g1:
        st.markdown('<p class="section-label">Revenue by State</p>', unsafe_allow_html=True)
        state_df = (
            dff.groupby("State")["Total Sales"].sum().reset_index()
            .sort_values("Total Sales", ascending=False)
        )
        fig_map = px.choropleth(
            state_df,
            locations="State",
            locationmode="USA-states",
            color="Total Sales",
            scope="usa",
            color_continuous_scale=[[0,"#1a2a4a"],[0.5,"#0f62fe"],[1,"#78a9ff"]],
            hover_data={"Total Sales": ":$,.0f"},
            labels={"Total Sales": "Revenue"},
        )
        fig_map.update_geos(
            bgcolor="#262626",
            landcolor="#353535",
            lakecolor="#262626",
            subunitcolor="#525252",
        )
        fig_map.update_coloraxes(colorbar=dict(
            tickprefix="$", tickformat=".2s",
            tickfont=dict(color="#8d8d8d"),
            bgcolor="#262626", bordercolor="#393939",
        ))
        apply_carbon(fig_map, height=340, geo=dict(bgcolor="#262626"))
        st.plotly_chart(fig_map, use_container_width=True)

    with col_g2:
        st.markdown('<p class="section-label">Top 10 States</p>', unsafe_allow_html=True)
        top10 = state_df.head(10).sort_values("Total Sales", ascending=True)
        fig_s = px.bar(
            top10, x="Total Sales", y="State", orientation="h",
            color="Total Sales",
            color_continuous_scale=[[0,"#1a2a4a"],[1,"#0f62fe"]],
        )
        fig_s.update_traces(width=0.6)
        fig_s.update_xaxes(tickprefix="$", tickformat=".2s")
        fig_s.update_coloraxes(showscale=False)
        apply_carbon(fig_s, height=340)
        st.plotly_chart(fig_s, use_container_width=True)

    # Region breakdown
    st.markdown('<p class="section-label">Region — Revenue, Profit & Units</p>', unsafe_allow_html=True)
    reg_full = (
        dff.groupby("Region")
        .agg(Revenue=("Total Sales","sum"), Profit=("Operating Profit","sum"), Units=("Units Sold","sum"))
        .reset_index()
    )
    reg_full["Margin"] = reg_full["Profit"] / reg_full["Revenue"]

    col_r1, col_r2 = st.columns(2)
    with col_r1:
        fig_rbar = px.bar(
            reg_full.sort_values("Revenue", ascending=False),
            x="Region", y=["Revenue","Profit"], barmode="group",
            color_discrete_sequence=["#0f62fe","#009d9a"],
        )
        fig_rbar.update_yaxes(tickprefix="$", tickformat=".2s")
        apply_carbon(fig_rbar, height=260)
        st.plotly_chart(fig_rbar, use_container_width=True)

    with col_r2:
        fig_rm = px.bar(
            reg_full.sort_values("Margin", ascending=False),
            x="Region", y="Margin",
            color="Region", color_discrete_sequence=CARBON_COLORS,
        )
        fig_rm.update_yaxes(tickformat=".1%", title="Operating Margin")
        fig_rm.update_layout(showlegend=False)
        apply_carbon(fig_rm, height=260)
        st.plotly_chart(fig_rm, use_container_width=True)

    # City breakdown
    st.markdown('<p class="section-label">Top 15 Cities by Revenue</p>', unsafe_allow_html=True)
    city_df = (
        dff.groupby(["City","State"])["Total Sales"].sum().reset_index()
        .sort_values("Total Sales", ascending=False).head(15)
    )
    city_df["City Label"] = city_df["City"] + ", " + city_df["State"]
    fig_city = px.bar(
        city_df.sort_values("Total Sales"),
        x="Total Sales", y="City Label", orientation="h",
        color="Total Sales",
        color_continuous_scale=[[0,"#1a2a4a"],[1,"#0f62fe"]],
    )
    fig_city.update_coloraxes(showscale=False)
    fig_city.update_xaxes(tickprefix="$", tickformat=".2s")
    apply_carbon(fig_city, height=400)
    st.plotly_chart(fig_city, use_container_width=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style='border-top:1px solid #393939;margin-top:2rem;padding-top:1rem;
text-align:center;font-size:11px;color:#525252;letter-spacing:.5px'>
ADIDAS US SALES DASHBOARD · IBM CARBON DESIGN SYSTEM · 2020–2021
</div>
""", unsafe_allow_html=True)