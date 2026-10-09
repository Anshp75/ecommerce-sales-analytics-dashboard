from pathlib import Path
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="E-commerce Sales Analytics",
    page_icon="📊",
    layout="wide",
)

st.title("📊 E-commerce Sales Analytics Dashboard")
st.caption("Turn transaction data into clear business insights and recommended actions.")

REQUIRED_ALIASES = {
    "InvoiceNo": ["InvoiceNo", "Invoice", "Order_ID", "Order ID", "OrderID"],
    "StockCode": ["StockCode", "Product_ID", "Product ID", "SKU"],
    "Description": ["Description", "Product_Name", "Product Name", "Product"],
    "Quantity": ["Quantity", "Qty", "Units"],
    "InvoiceDate": ["InvoiceDate", "Invoice Date", "Order_Date", "Order Date", "Date"],
    "UnitPrice": ["UnitPrice", "Unit Price", "Price", "Unit_Price"],
    "CustomerID": ["CustomerID", "Customer ID", "Customer_ID"],
    "Country": ["Country", "Region", "State"],
}

@st.cache_data
def load_file(file_bytes, filename):
    suffix = Path(filename).suffix.lower()
    from io import BytesIO
    stream = BytesIO(file_bytes)
    if suffix == ".xlsx":
        return pd.read_excel(stream)
    if suffix == ".xls":
        return pd.read_excel(stream)
    return pd.read_csv(stream)

def normalize_columns(df):
    df = df.copy()
    rename = {}
    for standard, aliases in REQUIRED_ALIASES.items():
        for col in df.columns:
            if str(col).strip().lower() in {a.lower() for a in aliases}:
                rename[col] = standard
                break
    return df.rename(columns=rename)

def prepare_data(raw):
    df = normalize_columns(raw)
    needed = ["InvoiceNo", "Description", "Quantity", "InvoiceDate", "UnitPrice", "Country"]
    missing = [c for c in needed if c not in df.columns]
    if missing:
        raise ValueError(
            "Missing required columns: " + ", ".join(missing) +
            ". For the UCI Online Retail dataset, upload Online Retail.xlsx."
        )

    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"], errors="coerce", dayfirst=True)
    df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce")
    df["UnitPrice"] = pd.to_numeric(df["UnitPrice"], errors="coerce")
    df["InvoiceNo"] = df["InvoiceNo"].astype(str).str.strip()
    df["Country"] = df["Country"].fillna("Unknown").astype(str)
    df["Description"] = df["Description"].fillna("Unknown product").astype(str)

    before = len(df)
    df = df.dropna(subset=["InvoiceDate", "Quantity", "UnitPrice", "InvoiceNo"])
    # Cancellation invoices and non-positive transactions are excluded from sales KPIs.
    df = df[~df["InvoiceNo"].str.upper().str.startswith("C")]
    df = df[(df["Quantity"] > 0) & (df["UnitPrice"] > 0)]
    df["Revenue"] = df["Quantity"] * df["UnitPrice"]
    df["Month"] = df["InvoiceDate"].dt.to_period("M").astype(str)
    df["OrderDate"] = df["InvoiceDate"].dt.date.astype(str)
    if "CustomerID" not in df.columns:
        df["CustomerID"] = pd.NA
    df["CustomerID"] = df["CustomerID"].astype("string")
    return df, before, len(df)

with st.sidebar:
    st.header("Data")
    uploaded = st.file_uploader(
        "Upload transaction data",
        type=["xlsx", "xls", "csv"],
        help="Recommended: UCI Online Retail.xlsx. The app also accepts CSV files with equivalent columns."
    )
    st.markdown("**Dataset source**")
    st.markdown("[UCI Online Retail dataset](https://archive.ics.uci.edu/dataset/352/online%2Bretail)")
    st.caption("For final submission, use a dataset not used as the masterclass learning dataset.")

if uploaded is not None:
    try:
        raw = load_file(uploaded.getvalue(), uploaded.name)
        data, rows_before, rows_after = prepare_data(raw)
    except Exception as exc:
        st.error(f"Could not load dataset: {exc}")
        st.stop()
else:
    demo_path = Path(__file__).parent / "data" / "demo_online_retail.csv"
    if not demo_path.exists():
        st.info("Upload a dataset from the sidebar to begin. A small demo dataset is included with this project.")
        st.stop()
    raw = pd.read_csv(demo_path)
    data, rows_before, rows_after = prepare_data(raw)
    st.info("Demo mode: showing results from the included illustrative sample. Upload the UCI dataset for your final analysis.")

if data.empty:
    st.warning("No valid positive sales transactions remain after cleaning. Check the uploaded dataset.")
    st.stop()

with st.sidebar:
    st.divider()
    min_date = data["InvoiceDate"].min().date()
    max_date = data["InvoiceDate"].max().date()
    date_range = st.date_input("Invoice date range", value=(min_date, max_date), min_value=min_date, max_value=max_date)
    countries = sorted(data["Country"].dropna().unique().tolist())
    selected_countries = st.multiselect("Country", countries, default=countries)
    products = sorted(data["Description"].dropna().unique().tolist())
    selected_products = st.multiselect("Product", products, default=[],
                                       help="Leave empty to include all products.")

filtered = data.copy()
if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start, end = date_range
    filtered = filtered[(filtered["InvoiceDate"].dt.date >= start) & (filtered["InvoiceDate"].dt.date <= end)]
if selected_countries:
    filtered = filtered[filtered["Country"].isin(selected_countries)]
else:
    filtered = filtered.iloc[0:0]
if selected_products:
    filtered = filtered[filtered["Description"].isin(selected_products)]

if filtered.empty:
    st.warning("No records match the selected filters. Change the filters in the sidebar.")
    st.stop()

# Online Retail does not contain a cost/profit field, so this project does not invent profit values.
revenue = float(filtered["Revenue"].sum())
orders = int(filtered["InvoiceNo"].nunique())
customers = int(filtered["CustomerID"].nunique()) if filtered["CustomerID"].notna().any() else 0
aov = revenue / orders if orders else 0
units = int(filtered["Quantity"].sum())

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total Revenue", f"£{revenue:,.2f}")
k2.metric("Orders", f"{orders:,}")
k3.metric("Unique Customers", f"{customers:,}" if customers else "N/A")
k4.metric("Average Order Value", f"£{aov:,.2f}")
k5.metric("Units Sold", f"{units:,}")

st.caption(f"Rows loaded: {rows_before:,} · Valid positive sales rows after cleaning: {rows_after:,} · Filtered rows: {len(filtered):,}")

tab_overview, tab_products, tab_customers, tab_data = st.tabs(
    ["Executive Overview", "Product Analysis", "Customer & Country Analysis", "Cleaned Data"]
)

with tab_overview:
    monthly = filtered.groupby("Month", as_index=False).agg(Revenue=("Revenue", "sum"), Orders=("InvoiceNo", "nunique"))
    left, right = st.columns(2)
    with left:
        fig = px.line(monthly, x="Month", y="Revenue", markers=True, title="Monthly Revenue Trend")
        fig.update_layout(xaxis_title="Month", yaxis_title="Revenue (£)")
        st.plotly_chart(fig, use_container_width=True)
    with right:
        country_sales = filtered.groupby("Country", as_index=False)["Revenue"].sum().nlargest(10, "Revenue")
        fig = px.bar(country_sales.sort_values("Revenue"), x="Revenue", y="Country", orientation="h",
                     title="Top 10 Countries by Revenue", labels={"Revenue": "Revenue (£)"})
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Business insights and recommended actions")
    best_month = monthly.loc[monthly["Revenue"].idxmax(), "Month"] if not monthly.empty else "N/A"
    best_country_row = filtered.groupby("Country")["Revenue"].sum().sort_values(ascending=False)
    best_country = best_country_row.index[0] if not best_country_row.empty else "N/A"
    best_product_row = filtered.groupby("Description")["Revenue"].sum().sort_values(ascending=False)
    best_product = best_product_row.index[0] if not best_product_row.empty else "N/A"
    insights = [
        f"Highest-revenue month in the selected data: **{best_month}**.",
        f"Top country by revenue in the selected data: **{best_country}**.",
        f"Top product by revenue in the selected data: **{best_product}**.",
        "Compare weaker months and countries with stronger periods before deciding where to focus promotions.",
        "Consider retention campaigns for identifiable repeat customers; confirm the pattern with customer-level data.",
    ]
    for item in insights:
        st.markdown(f"- {item}")
    st.caption("These are descriptive insights from the currently filtered data, not causal claims. The dataset has no cost field, so profit is not calculated.")

with tab_products:
    product_sales = filtered.groupby("Description", as_index=False).agg(
        Revenue=("Revenue", "sum"), Units=("Quantity", "sum"), Orders=("InvoiceNo", "nunique")
    ).sort_values("Revenue", ascending=False).head(15)
    fig = px.bar(product_sales.sort_values("Revenue"), x="Revenue", y="Description", orientation="h",
                 title="Top 15 Products by Revenue", labels={"Revenue": "Revenue (£)", "Description": "Product"})
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(product_sales, use_container_width=True, hide_index=True)

with tab_customers:
    country_summary = filtered.groupby("Country", as_index=False).agg(
        Revenue=("Revenue", "sum"),
        Orders=("InvoiceNo", "nunique"),
        Units=("Quantity", "sum"),
        Customers=("CustomerID", "nunique"),
    ).sort_values("Revenue", ascending=False)
    st.subheader("Country performance")
    st.dataframe(country_summary, use_container_width=True, hide_index=True)
    known_customers = filtered.dropna(subset=["CustomerID"])
    if not known_customers.empty:
        customer_summary = known_customers.groupby("CustomerID", as_index=False).agg(
            Revenue=("Revenue", "sum"), Orders=("InvoiceNo", "nunique")
        ).sort_values("Revenue", ascending=False).head(10)
        st.subheader("Top 10 customers by revenue")
        st.dataframe(customer_summary, use_container_width=True, hide_index=True)
    else:
        st.info("Customer IDs are unavailable in the selected data.")

with tab_data:
    st.subheader("Cleaned transaction records")
    st.dataframe(filtered.head(500), use_container_width=True, hide_index=True)
    csv_bytes = filtered.to_csv(index=False).encode("utf-8")
    st.download_button("Download filtered cleaned data (CSV)", data=csv_bytes,
                       file_name="cleaned_ecommerce_sales.csv", mime="text/csv")
