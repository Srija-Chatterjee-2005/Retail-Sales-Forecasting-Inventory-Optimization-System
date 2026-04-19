import os
import sys
import pandas as pd
import streamlit as st
import plotly.express as px

# Allow imports from project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.forecasting import recursive_forecast_for_sku_store
from src.inventory import compute_inventory_table
from src.utils import ensure_directories

ensure_directories()

st.set_page_config(
    page_title="Retail Control Center",
    page_icon="🛒",
    layout="wide"
)

# ---------- Custom UI ----------
st.markdown("""
<style>
    /* ===== APP BACKGROUND ===== */
    .stApp {
        background: linear-gradient(135deg, #020617 0%, #0F172A 55%, #111827 100%);
        color: #FFFFFF;
    }

    .main {
        color: #FFFFFF;
    }

    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 1.2rem;
        max-width: 1450px;
    }

    /* ===== GLOBAL TEXT ===== */
    h1, h2, h3, h4, h5, h6, p, label, div, span {
        color: #FFFFFF;
    }

    /* ===== HEADER ===== */
    .hero {
        background: linear-gradient(135deg, #2563EB, #7C3AED);
        padding: 22px 26px;
        border-radius: 22px;
        color: white;
        margin-bottom: 18px;
        box-shadow: 0 10px 28px rgba(37, 99, 235, 0.35);
    }

    .hero h1 {
        margin: 0;
        font-size: 34px;
        font-weight: 800;
        color: #FFFFFF;
    }

    .hero p {
        margin-top: 8px;
        font-size: 15px;
        color: #E0E7FF;
    }

    /* ===== SECTION TITLES ===== */
    .section-title {
        font-size: 24px;
        font-weight: 750;
        margin: 12px 0;
        color: #F8FAFC !important;
    }

    /* ===== SECTION PANELS ===== */
    .glass {
        background: rgba(15, 23, 42, 0.82);
        border: 1px solid rgba(148, 163, 184, 0.18);
        border-radius: 18px;
        padding: 16px;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.35);
        color: #FFFFFF;
    }

    .blue-card {
        background: linear-gradient(135deg, rgba(37,99,235,0.22), rgba(29,78,216,0.18));
    }

    .pink-card {
        background: linear-gradient(135deg, rgba(244,114,182,0.20), rgba(190,24,93,0.16));
    }

    .purple-card {
        background: linear-gradient(135deg, rgba(139,92,246,0.22), rgba(79,70,229,0.18));
    }

    .yellow-card {
        background: linear-gradient(135deg, rgba(245,158,11,0.20), rgba(202,138,4,0.16));
    }

    .orange-card {
        background: linear-gradient(135deg, rgba(249,115,22,0.20), rgba(194,65,12,0.16));
    }

    .cyan-card {
        background: linear-gradient(135deg, rgba(34,211,238,0.20), rgba(14,165,233,0.16));
    }

    /* ===== METRIC CARDS ===== */
    div[data-testid="stMetric"] {
        background: linear-gradient(180deg, rgba(30,41,59,0.96), rgba(15,23,42,0.96)) !important;
        border: 1px solid rgba(148,163,184,0.22) !important;
        padding: 14px !important;
        border-radius: 18px !important;
        box-shadow: 0 6px 18px rgba(0,0,0,0.35) !important;
    }

    div[data-testid="stMetricLabel"] {
        color: #94A3B8 !important;
        font-weight: 600 !important;
    }

    div[data-testid="stMetricValue"] {
        color: #FFFFFF !important;
        font-weight: 800 !important;
    }

    /* ===== INPUTS / SELECTBOX ===== */
    div[data-baseweb="select"] > div {
        background-color: rgba(15, 23, 42, 0.95) !important;
        border: 1px solid rgba(148,163,184,0.22) !important;
        color: #FFFFFF !important;
        border-radius: 12px !important;
    }

    div[data-baseweb="select"] * {
        color: #FFFFFF !important;
    }

    input, textarea {
        background-color: rgba(15, 23, 42, 0.95) !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(148,163,184,0.22) !important;
        border-radius: 12px !important;
    }

    /* ===== LABELS ABOVE INPUTS ===== */
    .stSelectbox label, .stTextInput label, .stNumberInput label {
        color: #E2E8F0 !important;
        font-weight: 600 !important;
    }

    /* ===== MINI CUSTOM CARDS ===== */
    .mini-card {
        border-radius: 16px;
        padding: 14px;
        border: 1px solid rgba(148,163,184,0.22);
        box-shadow: 0 6px 16px rgba(0,0,0,0.28);
        color: #FFFFFF;
        background: rgba(15, 23, 42, 0.78);
    }

    .mini-label {
        font-size: 13px;
        color: #CBD5E1;
        margin-bottom: 6px;
        font-weight: 600;
    }

    .mini-value {
        font-size: 28px;
        font-weight: 800;
        color: #FFFFFF;
        line-height: 1.1;
    }

    .subtle {
        color: #94A3B8;
        font-size: 12px;
    }

    /* ===== EXPANDER ===== */
    details {
        background: rgba(15, 23, 42, 0.72) !important;
        border: 1px solid rgba(148,163,184,0.18) !important;
        border-radius: 12px !important;
        padding: 6px 10px !important;
    }

    summary {
        color: #FFFFFF !important;
        font-weight: 600 !important;
    }

    /* ===== ALERTS ===== */
    .ok-box {
        background: rgba(34,197,94,0.18);
        border: 1px solid rgba(34,197,94,0.42);
        color: #BBF7D0;
        padding: 12px;
        border-radius: 12px;
    }

    .warn-box {
        background: rgba(245,158,11,0.18);
        border: 1px solid rgba(245,158,11,0.42);
        color: #FDE68A;
        padding: 12px;
        border-radius: 12px;
    }

    .danger-box {
        background: rgba(239,68,68,0.18);
        border: 1px solid rgba(239,68,68,0.42);
        color: #FCA5A5;
        padding: 12px;
        border-radius: 12px;
    }

    /* ===== DATAFRAME ===== */
    div[data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid rgba(148,163,184,0.18);
    }

    /* ===== CAPTION / NOTES ===== */
    .small-note {
        color: #94A3B8 !important;
        font-size: 13px;
    }

    /* ===== HORIZONTAL RULE FIX ===== */
    hr {
        border: none !important;
        height: 1px !important;
        background: rgba(148,163,184,0.18) !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------- Load artifacts ----------
sales_path = "outputs/final_sales_data.csv"
metrics_path = "outputs/model_metrics.csv"

if not os.path.exists(sales_path) or not os.path.exists(metrics_path):
    st.error("Required output files not found. Run `python main.py` first.")
    st.stop()

sales_df = pd.read_csv(sales_path, parse_dates=["date"])
metrics_df = pd.read_csv(metrics_path)

# ---------- Header ----------
st.markdown("""
<div class="hero">
    <h1>📊 Retail Sales Forecasting & Inventory Optimization System</h1>
    <p>Analyze sales trends, forecast demand, and optimize inventory decisions in real time.</p>
</div>
""", unsafe_allow_html=True)

# ---------- Global KPIs ----------
total_sales = int(sales_df["qty_sold"].sum())
avg_daily_sales = round(sales_df["qty_sold"].mean(), 2)
total_revenue = round((sales_df["qty_sold"] * sales_df["price"]).sum(), 2)
sku_count = sales_df["item_id"].nunique()

st.markdown('<div class="section-title">📊 Business Snapshot</div>', unsafe_allow_html=True)
k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Units Sold", f"{total_sales:,}")
k2.metric("Average Daily Sales", avg_daily_sales)
k3.metric("Total Revenue", f"₹ {total_revenue:,.0f}")
k4.metric("Unique SKUs", sku_count)

# ---------- Filter Bar ----------
# ---------- Filter Bar ----------
st.markdown('<div class="section-title">🔎 Filters</div>', unsafe_allow_html=True)
st.markdown('<div class="glass blue-card">', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns([1, 1, 1, 0.8])

categories = sorted(sales_df["category"].unique().tolist())
stores = sorted(sales_df["store_id"].unique().tolist())

with c1:
    selected_category = st.selectbox("Category", categories, key="category_filter_new")

filtered_items = sorted(
    sales_df.loc[sales_df["category"] == selected_category, "item_id"].unique().tolist()
)

with c2:
    selected_item = st.selectbox("Item", filtered_items, key="item_filter_new")

with c3:
    selected_store = st.selectbox("Store", stores, key="store_filter_new")

with c4:
    horizon = st.selectbox("Forecast Horizon", [7, 14], index=0, key="horizon_filter")

st.markdown('</div>', unsafe_allow_html=True)

# Filter data according to selected options
filtered = sales_df[
    (sales_df["category"] == selected_category) &
    (sales_df["item_id"] == selected_item) &
    (sales_df["store_id"] == selected_store)
].sort_values("date")

if filtered.empty:
    st.warning("No sales rows found for the selected category, item, and store.")
    st.stop()

# ---------- Selected Snapshot ----------
# ---------- Selected Snapshot ----------
latest_row = filtered.iloc[-1]
current_stock = int(latest_row["stock_on_hand"])

st.markdown('<div class="section-title">📦 Selected Segment Snapshot</div>', unsafe_allow_html=True)
s1, s2, s3, s4 = st.columns(4)
s1.metric("Selected Category", selected_category)
s2.metric("Selected Item", selected_item)
s3.metric("Selected Store", selected_store)
s4.metric("Current Stock", current_stock)

# ---------- Forecast ----------
forecast_df = recursive_forecast_for_sku_store(
    sales_df,
    selected_store,
    selected_item,
    horizon
)

# ---------- Main Analytics Layout ----------
left, right = st.columns([1.35, 1], gap="large")

with left:
    st.markdown('<div class="section-title">📈 Historical Sales Trend</div>', unsafe_allow_html=True)
    st.markdown('<div class="glass pink-card">', unsafe_allow_html=True)

    fig_sales = px.line(
        filtered,
        x="date",
        y="qty_sold",
        markers=True
    )
    fig_sales.update_layout(
        title=f"{selected_store} | {selected_item} Historical Demand",
        template="plotly_dark",
        margin=dict(l=20, r=20, t=50, b=20),
        xaxis_title="Date",
        yaxis_title="Units Sold",
        height=420
    )
    st.plotly_chart(fig_sales, use_container_width=True)
    st.markdown('<div class="small-note">Historical daily sales for the selected store-item combination.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with right:
    st.markdown('<div class="section-title">🔮 Demand Forecast</div>', unsafe_allow_html=True)
    st.markdown('<div class="glass purple-card">', unsafe_allow_html=True)

    if forecast_df.empty:
        st.warning("Forecast could not be generated for this selection.")
    else:
        forecast_total = round(forecast_df["forecast_qty"].sum(), 2)
        avg_forecast = round(forecast_df["forecast_qty"].mean(), 2)

        m1, m2 = st.columns(2)
        with m1:
            st.markdown(f"""
            <div class="mini-card">
                <div class="mini-label">Forecast Total</div>
                <div class="mini-value">{forecast_total}</div>
                <div class="subtle">{horizon}-day projected units</div>
            </div>
            """, unsafe_allow_html=True)

        with m2:
            st.markdown(f"""
            <div class="mini-card">
                <div class="mini-label">Forecast Average</div>
                <div class="mini-value">{avg_forecast}</div>
                <div class="subtle">average daily projection</div>
            </div>
            """, unsafe_allow_html=True)

        fig_forecast = px.line(
            forecast_df,
            x="date",
            y="forecast_qty",
            markers=True
        )
        fig_forecast.update_layout(
            title=f"Next {horizon} Days Forecast",
            template="plotly_dark",
            margin=dict(l=20, r=20, t=50, b=20),
            xaxis_title="Date",
            yaxis_title="Forecast Qty",
            height=300
        )
        st.plotly_chart(fig_forecast, use_container_width=True)
        st.dataframe(forecast_df, use_container_width=True, height=230)

    st.markdown('</div>', unsafe_allow_html=True)

# ---------- Inventory ----------
st.markdown('<div class="section-title">📦 Inventory Recommendation</div>', unsafe_allow_html=True)
st.markdown('<div class="glass yellow-card">', unsafe_allow_html=True)

inventory_result = compute_inventory_table(
    sales_df=sales_df,
    forecast_df=forecast_df,
    selected_store=selected_store,
    selected_item=selected_item
)

if inventory_result.empty:
    st.warning("Inventory recommendation could not be generated.")
else:
    order_qty = float(inventory_result.iloc[0]["recommended_order_qty"])
    rop = float(inventory_result.iloc[0]["reorder_point"])
    safety_stock = float(inventory_result.iloc[0]["safety_stock"])

    a1, a2, a3 = st.columns(3)
    a1.metric("Reorder Point", f"{rop:.0f}")
    a2.metric("Safety Stock", f"{safety_stock:.0f}")
    a3.metric("Recommended Order", f"{order_qty:.0f}")

    if current_stock <= rop:
        st.markdown(
            f'<div class="alert-box warn-box">⚠️ Reorder Alert: Current stock ({current_stock}) is below or near the reorder point ({rop:.0f}). Recommended order quantity: {order_qty:.0f} units.</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f'<div class="alert-box ok-box">✅ Stock looks healthy. Current stock ({current_stock}) is above the reorder point ({rop:.0f}).</div>',
            unsafe_allow_html=True
        )

    with st.expander("View detailed inventory table"):
        st.dataframe(inventory_result, use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)

# ---------- Bottom Section ----------
# ---------- Bottom Section ----------
b1, b2 = st.columns([1.25, 0.75], gap="large")

with b1:
    st.markdown('<div class="section-title">🧾 Store-wise Category Summary</div>', unsafe_allow_html=True)
    st.markdown('<div class="glass orange-card">', unsafe_allow_html=True)

    category_summary = sales_df[sales_df["store_id"] == selected_store].groupby("category", as_index=False).agg(
        total_qty=("qty_sold", "sum"),
        avg_price=("price", "mean"),
        avg_stock=("stock_on_hand", "mean")
    )

    fig_cat = px.bar(
        category_summary,
        x="category",
        y="total_qty",
        text_auto=True,
        color="category"
    )
    fig_cat.update_layout(
        title=f"Category-wise Sales Volume | {selected_store}",
        template="plotly_dark",
        margin=dict(l=20, r=20, t=50, b=20),
        xaxis_title="Category",
        yaxis_title="Total Units Sold",
        height=430,
        showlegend=False
    )
    st.plotly_chart(fig_cat, use_container_width=True)

    with st.expander("View category summary table"):
        st.dataframe(category_summary, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

with b2:
    st.markdown('<div class="section-title">🧠 Model Performance</div>', unsafe_allow_html=True)
    st.markdown('<div class="glass cyan-card">', unsafe_allow_html=True)

    if not metrics_df.empty:
        mae_val = float(metrics_df.iloc[0]["MAE"])
        rmse_val = float(metrics_df.iloc[0]["RMSE"])
        r2_val = float(metrics_df.iloc[0]["R2_SCORE"])

        st.metric("MAE", f"{mae_val:.3f}")
        mcol2, mcol3 = st.columns(2)
        mcol2.metric("RMSE", f"{rmse_val:.3f}")
        mcol3.metric("R² Score", f"{r2_val:.3f}")

    st.dataframe(metrics_df, use_container_width=True, height=120)
    st.markdown(
        '<div class="small-note">Lower MAE and RMSE generally indicate stronger forecasting performance.</div>',
        unsafe_allow_html=True
    )

    st.markdown('</div>', unsafe_allow_html=True)