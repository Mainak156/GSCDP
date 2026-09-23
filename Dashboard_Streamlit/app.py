import os
import json
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(
    page_title="Global Supply Chain Operations",
    page_icon="🚚",
    layout="wide"
)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOTEBOOK_PATH = os.path.join(PROJECT_ROOT, "Global_Supply_Chain_Operations.ipynb")
DATASET_DIR = os.path.join(PROJECT_ROOT, "dataset")


@st.cache_resource
def execute_notebook():
    with open(NOTEBOOK_PATH, "r", encoding="utf-8") as f:
        notebook = json.load(f)

    namespace = {
        "__name__": "__main__"
    }

    original_directory = os.getcwd()

    try:
        os.chdir(DATASET_DIR)

        for cell in notebook["cells"]:
            if cell.get("cell_type") != "code":
                continue

            source = "".join(cell.get("source", []))

            if not source.strip():
                continue

            if "from google.colab import files" in source:
                continue

            if "files.upload()" in source:
                continue

            exec(compile(source, NOTEBOOK_PATH, "exec"), namespace)

    finally:
        os.chdir(original_directory)

    return namespace


nb = execute_notebook()

df = nb["df"]
actual_col = nb["actual_col"]
scheduled_col = nb["scheduled_col"]
classify_delivery = nb["classify_delivery"]
on_time_percentage = nb["on_time_percentage"]

with st.sidebar:
    st.header("Filters")

    shipping_modes = st.multiselect(
        "Shipping Mode",
        sorted(df["Shipping Mode"].unique())
    )

    regions = st.multiselect(
        "Order Region",
        sorted(df["Order Region"].unique())
    )

    markets = st.multiselect(
        "Market",
        sorted(df["Market"].unique())
    )

    customer_segments = st.multiselect(
        "Customer Segment",
        sorted(df["Customer Segment"].unique())
    )

filtered_df = df.copy()

if shipping_modes:
    filtered_df = filtered_df[
        filtered_df["Shipping Mode"].isin(shipping_modes)
    ]

if regions:
    filtered_df = filtered_df[
        filtered_df["Order Region"].isin(regions)
    ]

if markets:
    filtered_df = filtered_df[
        filtered_df["Market"].isin(markets)
    ]

if customer_segments:
    filtered_df = filtered_df[
        filtered_df["Customer Segment"].isin(customer_segments)
    ]

if filtered_df.empty:
    st.warning("No shipments match the selected filters.")
    st.stop()

st.title("🚚 Global Supply Chain Operations Dashboard")
st.caption("Delivery Performance, Delay Risk, and Logistics Efficiency Analysis")

tab1, tab2, tab3, tab4 = st.tabs([
    "Delivery Performance Overview",
    "Delay Risk Analysis",
    "Shipping Mode Comparison",
    "Regional & Market Heatmaps"
])

with tab1:
    st.subheader("Delivery Performance Overview")

    filtered_on_time_percentage = (
        (filtered_df["Delivery Timing"] == "On-time").sum()
        / len(filtered_df)
    ) * 100

    average_delay = filtered_df["Delay Gap"].mean()

    delayed_percentage = (
        (filtered_df["Delivery Timing"] == "Delayed").sum()
        / len(filtered_df)
    ) * 100

    late_risk_percentage = (
        filtered_df["Late_delivery_risk"].mean()
    ) * 100

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Shipments",
        f"{len(filtered_df):,}"
    )

    col2.metric(
        "On-Time Delivery",
        f"{filtered_on_time_percentage:.2f}%"
    )

    col3.metric(
        "Average Delivery Delay",
        f"{average_delay:.2f} days"
    )

    col4.metric(
        "Late Delivery Risk",
        f"{late_risk_percentage:.2f}%"
    )

    timing_counts = (
        filtered_df["Delivery Timing"]
        .value_counts()
        .reindex(["Early", "On-time", "Delayed"])
        .fillna(0)
    )

    timing_df = timing_counts.reset_index()
    timing_df.columns = ["Delivery Timing", "Shipments"]

    fig = px.bar(
        timing_df,
        x="Delivery Timing",
        y="Shipments",
        title="Delivery Performance"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    customer_segment_delay = (
        filtered_df.groupby("Customer Segment")
        .agg(
            Total_Shipments=("Customer Segment", "size"),
            Delayed_Shipments=(
                "Delivery Timing",
                lambda x: (x == "Delayed").sum()
            )
        )
    )

    customer_segment_delay["Delay Frequency (%)"] = (
        customer_segment_delay["Delayed_Shipments"]
        / customer_segment_delay["Total_Shipments"] * 100
    )

    customer_segment_delay = (
        customer_segment_delay
        .sort_values("Delay Frequency (%)", ascending=False)
        .round(2)
    )

    st.subheader("Customer Segment Impact")

    st.dataframe(
        customer_segment_delay,
        use_container_width=True
    )

    fig = px.bar(
        customer_segment_delay.reset_index(),
        x="Customer Segment",
        y="Delay Frequency (%)",
        title="Delay Frequency by Customer Segment"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

with tab2:
    st.subheader("Delay Risk Analysis")

    risk_distribution = (
        filtered_df["Late_delivery_risk"]
        .value_counts()
        .sort_index()
    )

    risk_df = risk_distribution.reset_index()
    risk_df.columns = [
        "Late_delivery_risk",
        "Shipments"
    ]

    fig = px.bar(
        risk_df,
        x="Late_delivery_risk",
        y="Shipments",
        title="Late Delivery Risk Distribution"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.subheader("Delivery Timing Distribution")

    timing_percentage = (
        filtered_df["Delivery Timing"]
        .value_counts(normalize=True)
        .mul(100)
        .round(2)
    )

    timing_percentage_df = timing_percentage.reset_index()

    timing_percentage_df.columns = [
        "Delivery Timing",
        "Percentage"
    ]

    fig = px.bar(
        timing_percentage_df,
        x="Delivery Timing",
        y="Percentage",
        title="Delivery Timing Percentage"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.subheader("Delay Gap Distribution")

    fig = px.histogram(
        filtered_df,
        x="Delay Gap",
        nbins=30,
        title="Delivery Delay Gap Distribution",
        labels={
            "Delay Gap": "Delay Gap (Days)"
        }
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

with tab3:
    st.subheader("Shipping Mode Comparison")

    shipping_mode_delay = (
        filtered_df.groupby("Shipping Mode")["Delay Gap"]
        .agg(["mean", "median", "min", "max"])
        .round(2)
        .sort_values("mean", ascending=False)
    )

    st.dataframe(
        shipping_mode_delay,
        use_container_width=True
    )

    fig = px.bar(
        shipping_mode_delay.reset_index(),
        x="Shipping Mode",
        y="mean",
        title="Average Delay Gap by Shipping Mode",
        labels={
            "mean": "Average Delay Gap (Days)"
        }
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    delivery_status_delay = (
        filtered_df.groupby("Delivery Status")["Delay Gap"]
        .agg(["mean", "median", "min", "max"])
        .round(2)
        .sort_values("mean", ascending=False)
    )

    st.subheader("Delay Gap by Delivery Status")

    st.dataframe(
        delivery_status_delay,
        use_container_width=True
    )

    fig = px.bar(
        delivery_status_delay.reset_index(),
        x="Delivery Status",
        y="mean",
        title="Average Delay Gap by Delivery Status",
        labels={
            "mean": "Average Delay Gap (Days)"
        }
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    shipping_mode_delay_frequency = (
        filtered_df.groupby("Shipping Mode")
        .agg(
            Total_Shipments=("Shipping Mode", "size"),
            Delayed_Shipments=(
                "Delivery Timing",
                lambda x: (x == "Delayed").sum()
            )
        )
    )

    shipping_mode_delay_frequency["Delay Frequency (%)"] = (
        shipping_mode_delay_frequency["Delayed_Shipments"]
        / shipping_mode_delay_frequency["Total_Shipments"] * 100
    )

    shipping_mode_delay_frequency = (
        shipping_mode_delay_frequency
        .sort_values("Delay Frequency (%)", ascending=False)
        .round(2)
    )

    st.subheader("Delay Frequency by Shipping Mode")

    st.dataframe(
        shipping_mode_delay_frequency,
        use_container_width=True
    )

    fig = px.bar(
        shipping_mode_delay_frequency.reset_index(),
        x="Shipping Mode",
        y="Delay Frequency (%)",
        title="Delay Frequency by Shipping Mode"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

with tab4:
    st.subheader("Regional & Market Diagnostics")

    region_delay = (
        filtered_df.groupby("Order Region")
        .agg(
            Total_Shipments=("Order Region", "size"),
            Delayed_Shipments=(
                "Delivery Timing",
                lambda x: (x == "Delayed").sum()
            )
        )
    )

    region_delay["Delay Frequency (%)"] = (
        region_delay["Delayed_Shipments"]
        / region_delay["Total_Shipments"] * 100
    )

    region_delay = (
        region_delay
        .sort_values("Delay Frequency (%)", ascending=False)
        .round(2)
    )

    st.subheader("Regional Delay Frequency")

    fig = px.bar(
        region_delay.reset_index(),
        y="Order Region",
        x="Delay Frequency (%)",
        orientation="h",
        title="Delay Frequency by Order Region"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    country_delay = (
        filtered_df.groupby("Order Country")
        .agg(
            Total_Shipments=("Order Country", "size"),
            Delayed_Shipments=(
                "Delivery Timing",
                lambda x: (x == "Delayed").sum()
            )
        )
    )

    country_delay["Delay Frequency (%)"] = (
        country_delay["Delayed_Shipments"]
        / country_delay["Total_Shipments"] * 100
    )

    country_delay = (
        country_delay
        .sort_values("Delay Frequency (%)", ascending=False)
        .round(2)
    )

    st.subheader("Top Countries by Delay Frequency")

    top_countries = country_delay.head(15)

    fig = px.bar(
        top_countries.reset_index(),
        y="Order Country",
        x="Delay Frequency (%)",
        orientation="h",
        title="Top 15 Countries by Delay Frequency"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    market_delay = (
        filtered_df.groupby("Market")
        .agg(
            Total_Shipments=("Market", "size"),
            Delayed_Shipments=(
                "Delivery Timing",
                lambda x: (x == "Delayed").sum()
            )
        )
    )

    market_delay["Delay Frequency (%)"] = (
        market_delay["Delayed_Shipments"]
        / market_delay["Total_Shipments"] * 100
    )

    market_delay = (
        market_delay
        .sort_values("Delay Frequency (%)", ascending=False)
        .round(2)
    )

    st.subheader("Market Delay Frequency")

    fig = px.bar(
        market_delay.reset_index(),
        x="Market",
        y="Delay Frequency (%)",
        title="Delay Frequency by Market"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    regional_delay_index = (
        filtered_df.groupby("Order Region")["Delay Gap"]
        .mean()
        .sort_values(ascending=False)
        .round(2)
    )

    regional_delay_index_df = (
        regional_delay_index
        .reset_index()
    )

    regional_delay_index_df.columns = [
        "Order Region",
        "Regional Delay Index"
    ]

    st.subheader("Regional Delay Index")

    fig = px.bar(
        regional_delay_index_df,
        y="Order Region",
        x="Regional Delay Index",
        orientation="h",
        title="Regional Delay Index"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )