import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(
    page_title="Global Supply Chain Dashboard",
    page_icon="🚚",
    layout="wide"
)

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

DATASET_PATH = os.path.join(
    PROJECT_ROOT,
    "dataset",
    "APL_Logistics.csv"
)


@st.cache_data
def load_data():
    df = pd.read_csv(
        DATASET_PATH,
        encoding="latin1"
    )

    df.dropna(inplace=True)

    actual_col = "Days for shipping (real)"
    scheduled_col = "Days for shipment (scheduled)"

    df["Delay Gap"] = (
        df[actual_col] - df[scheduled_col]
    )

    def classify_delivery(delay):
        if delay < 0:
            return "Early"
        elif delay == 0:
            return "On-time"
        else:
            return "Delayed"

    df["Delivery Timing"] = (
        df["Delay Gap"].apply(classify_delivery)
    )

    return df


df = load_data()

st.title(
    "🚚 Global Supply Chain Delivery Performance Dashboard"
)

st.markdown(
    """
    **Delivery Performance, Delay Risk, and Logistics Efficiency Analysis**

    Analyze shipment delays, delivery risk, shipping-mode performance,
    customer segments, regions, and markets.
    """
)

st.sidebar.header("🔎 Dashboard Filters")

shipping_modes = sorted(
    df["Shipping Mode"].dropna().unique()
)

selected_shipping_modes = st.sidebar.multiselect(
    "Shipping Mode",
    options=shipping_modes,
    default=[]
)

regions = sorted(
    df["Order Region"].dropna().unique()
)

selected_regions = st.sidebar.multiselect(
    "Order Region",
    options=regions,
    default=[]
)

markets = sorted(
    df["Market"].dropna().unique()
)

selected_markets = st.sidebar.multiselect(
    "Market",
    options=markets,
    default=[]
)

customer_segments = sorted(
    df["Customer Segment"].dropna().unique()
)

selected_customer_segments = st.sidebar.multiselect(
    "Customer Segment",
    options=customer_segments,
    default=[]
)

filtered_df = df.copy()

if selected_shipping_modes:
    filtered_df = filtered_df[
        filtered_df["Shipping Mode"].isin(
            selected_shipping_modes
        )
    ]

if selected_regions:
    filtered_df = filtered_df[
        filtered_df["Order Region"].isin(
            selected_regions
        )
    ]

if selected_markets:
    filtered_df = filtered_df[
        filtered_df["Market"].isin(
            selected_markets
        )
    ]

if selected_customer_segments:
    filtered_df = filtered_df[
        filtered_df["Customer Segment"].isin(
            selected_customer_segments
        )
    ]

if filtered_df.empty:
    st.warning(
        "No shipments match the selected filters. "
        "Please adjust the filters."
    )
    st.stop()

st.caption(
    f"Showing {len(filtered_df):,} shipments"
)

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "📊 Delivery Performance Overview",
        "⚠️ Delay Risk Analysis",
        "🚚 Shipping Mode Comparison",
        "🌍 Regional & Market Heatmaps"
    ]
)

with tab1:

    st.header("📊 Delivery Performance Overview")

    total_shipments = len(filtered_df)

    on_time_shipments = (
        filtered_df["Delivery Timing"] == "On-time"
    ).sum()

    delayed_shipments = (
        filtered_df["Delivery Timing"] == "Delayed"
    ).sum()

    early_shipments = (
        filtered_df["Delivery Timing"] == "Early"
    ).sum()

    on_time_rate = (
        on_time_shipments
        / total_shipments
        * 100
    )

    late_rate = (
        delayed_shipments
        / total_shipments
        * 100
    )

    average_delay = (
        filtered_df["Delay Gap"].mean()
    )

    late_risk_ratio = (
        filtered_df["Late_delivery_risk"].mean()
        * 100
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total Shipments",
            f"{total_shipments:,}"
        )

    with col2:
        st.metric(
            "On-Time Delivery",
            f"{on_time_rate:.2f}%"
        )

    with col3:
        st.metric(
            "Late Delivery",
            f"{late_rate:.2f}%"
        )

    with col4:
        st.metric(
            "Average Delay",
            f"{average_delay:.2f} days"
        )

    delivery_timing = (
        filtered_df["Delivery Timing"]
        .value_counts()
        .reindex(
            [
                "On-time",
                "Delayed",
                "Early"
            ],
            fill_value=0
        )
        .reset_index()
    )

    delivery_timing.columns = [
        "Delivery Timing",
        "Shipments"
    ]

    fig_delivery = px.bar(
        delivery_timing,
        x="Delivery Timing",
        y="Shipments",
        title="Delivery Timing Distribution",
        text="Shipments"
    )

    fig_delivery.update_layout(
        height=400
    )

    st.plotly_chart(
        fig_delivery,
        use_container_width=True
    )

    st.subheader(
        "Delivery Performance Summary"
    )

    performance_summary = pd.DataFrame(
        {
            "Metric": [
                "Total Shipments",
                "On-Time Shipments",
                "Delayed Shipments",
                "Early Shipments",
                "On-Time Delivery Rate (%)",
                "Late Delivery Rate (%)",
                "Average Delivery Delay (Days)",
                "Late Delivery Risk Ratio (%)"
            ],
            "Value": [
                total_shipments,
                on_time_shipments,
                delayed_shipments,
                early_shipments,
                on_time_rate,
                late_rate,
                average_delay,
                late_risk_ratio
            ]
        }
    )

    performance_summary["Value"] = (
        performance_summary["Value"].round(2)
    )

    st.dataframe(
        performance_summary,
        use_container_width=True,
        hide_index=True
    )


with tab2:

    st.header("⚠️ Delay Risk Analysis")

    col1, col2 = st.columns(2)

    with col1:

        risk_distribution = (
            filtered_df["Late_delivery_risk"]
            .value_counts()
            .sort_index()
            .reset_index()
        )

        risk_distribution.columns = [
            "Late Delivery Risk",
            "Shipments"
        ]

        risk_distribution["Risk Label"] = (
            risk_distribution[
                "Late Delivery Risk"
            ].map(
                {
                    0: "No Risk",
                    1: "At Risk"
                }
            )
        )

        fig_risk = px.pie(
            risk_distribution,
            names="Risk Label",
            values="Shipments",
            title="Late Delivery Risk Distribution"
        )

        st.plotly_chart(
            fig_risk,
            use_container_width=True
        )

    with col2:

        fig_delay = px.histogram(
            filtered_df,
            x="Delay Gap",
            nbins=20,
            title="Delivery Delay Gap Distribution",
            labels={
                "Delay Gap": "Delay Gap (Days)"
            }
        )

        fig_delay.add_vline(
            x=0,
            line_dash="dash"
        )

        st.plotly_chart(
            fig_delay,
            use_container_width=True
        )

    st.subheader(
        "Late Delivery Risk Distribution"
    )

    risk_table = (
        filtered_df
        .groupby("Late_delivery_risk")
        .agg(
            Total_Shipments=(
                "Late_delivery_risk",
                "size"
            )
        )
        .reset_index()
    )

    risk_table["Risk Label"] = (
        risk_table["Late_delivery_risk"].map(
            {
                0: "No Risk",
                1: "At Risk"
            }
        )
    )

    risk_table["Percentage (%)"] = (
        risk_table["Total_Shipments"]
        / total_shipments
        * 100
    )

    risk_table = risk_table[
        [
            "Late_delivery_risk",
            "Risk Label",
            "Total_Shipments",
            "Percentage (%)"
        ]
    ]

    st.dataframe(
        risk_table.round(2),
        use_container_width=True,
        hide_index=True
    )


with tab3:

    st.header("🚚 Shipping Mode Comparison")

    mode_performance = (
        filtered_df
        .groupby("Shipping Mode")
        .agg(
            Total_Shipments=(
                "Shipping Mode",
                "size"
            ),
            Average_Delay=(
                "Delay Gap",
                "mean"
            ),
            Delayed_Shipments=(
                "Delivery Timing",
                lambda x: (
                    x == "Delayed"
                ).sum()
            )
        )
        .reset_index()
    )

    mode_performance[
        "Delay Frequency (%)"
    ] = (
        mode_performance[
            "Delayed_Shipments"
        ]
        / mode_performance[
            "Total_Shipments"
        ]
        * 100
    )

    mode_performance[
        "SLA Compliance (%)"
    ] = (
        100
        - mode_performance[
            "Delay Frequency (%)"
        ]
    )

    col1, col2 = st.columns(2)

    with col1:

        fig_mode_delay = px.bar(
            mode_performance,
            x="Shipping Mode",
            y="Average_Delay",
            title="Mode-wise Delay Performance",
            text_auto=".2f",
            labels={
                "Average_Delay":
                "Average Delay (Days)"
            }
        )

        st.plotly_chart(
            fig_mode_delay,
            use_container_width=True
        )

    with col2:

        fig_sla = px.bar(
            mode_performance,
            x="Shipping Mode",
            y="SLA Compliance (%)",
            title="SLA Compliance by Shipping Mode",
            text_auto=".2f",
            labels={
                "SLA Compliance (%)":
                "SLA Compliance (%)"
            }
        )

        st.plotly_chart(
            fig_sla,
            use_container_width=True
        )

    st.subheader(
        "Shipping Mode Performance"
    )

    st.dataframe(
        mode_performance.round(2),
        use_container_width=True,
        hide_index=True
    )


with tab4:

    st.header(
        "🌍 Regional & Market Heatmaps"
    )

    col1, col2 = st.columns(2)

    with col1:

        regional_heatmap = (
            filtered_df
            .groupby("Order Region")
            .agg(
                Total_Shipments=(
                    "Order Region",
                    "size"
                ),
                Average_Delay=(
                    "Delay Gap",
                    "mean"
                ),
                Delay_Frequency=(
                    "Delivery Timing",
                    lambda x: (
                        x == "Delayed"
                    ).mean() * 100
                )
            )
            .reset_index()
        )

        regional_heatmap = (
            regional_heatmap
            .sort_values(
                "Delay_Frequency",
                ascending=False
            )
        )

        fig_region = px.density_heatmap(
            regional_heatmap,
            x="Order Region",
            y="Delay_Frequency",
            z="Average_Delay",
            title="Regional Delay Heatmap",
            labels={
                "Order Region": "Region",
                "Delay_Frequency":
                "Delay Frequency (%)",
                "Average_Delay":
                "Average Delay (Days)"
            }
        )

        fig_region.update_layout(
            xaxis_tickangle=-45
        )

        st.plotly_chart(
            fig_region,
            use_container_width=True
        )

    with col2:

        market_efficiency = (
            filtered_df
            .groupby("Market")
            .agg(
                Total_Shipments=(
                    "Market",
                    "size"
                ),
                Average_Delay=(
                    "Delay Gap",
                    "mean"
                ),
                Delay_Frequency=(
                    "Delivery Timing",
                    lambda x: (
                        x == "Delayed"
                    ).mean() * 100
                )
            )
            .reset_index()
        )

        fig_market = px.bar(
            market_efficiency,
            x="Market",
            y="Average_Delay",
            title="Market-wise Logistics Efficiency",
            text_auto=".2f",
            labels={
                "Average_Delay":
                "Average Delay (Days)"
            }
        )

        st.plotly_chart(
            fig_market,
            use_container_width=True
        )

    st.subheader(
        "Regional Logistics Performance"
    )

    st.dataframe(
        regional_heatmap.round(2),
        use_container_width=True,
        hide_index=True
    )

    st.subheader(
        "Market Logistics Performance"
    )

    st.dataframe(
        market_efficiency.round(2),
        use_container_width=True,
        hide_index=True
    )