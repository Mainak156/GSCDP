import os
import streamlit as st
import pandas as pd
import plotly.express as px
from babel import Locale

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

ACTUAL_COL = "Days for shipping (real)"
SCHEDULED_COL = "Days for shipment (scheduled)"

ES_TERRITORIES = Locale("es").territories
EN_TERRITORIES = Locale("en").territories

COUNTRY_ALIASES = {
    "Canada": "CA",
    "Costa de Marfil": "CI",
    "Guinea-Bissau": "GW",
    "Hong Kong": "HK",
    "Macedonia": "MK",
    "Qatar": "QA",
    "República Checa": "CZ",
    "República de Gambia": "GM",
    "República del Congo": "CG",
    "Rumania": "RO",
    "Suazilandia": "SZ",
    "SudAfrica": "ZA"
}

SPANISH_COUNTRY_CODES = {
    name.casefold(): code
    for code, name in ES_TERRITORIES.items()
    if len(code) == 2
}


def country_to_map_name(country):
    code = COUNTRY_ALIASES.get(country)
    if code is None:
        code = SPANISH_COUNTRY_CODES.get(country.casefold())
    return EN_TERRITORIES.get(code, country)


def classify_delivery(delay):
    if delay < 0:
        return "Early"
    elif delay == 0:
        return "On-time"
    else:
        return "Delayed"


@st.cache_data
def load_data():

    df = pd.read_csv(
        DATASET_PATH,
        encoding="latin1"
    )

    raw_rows = len(df)

    df.dropna(inplace=True)

    rows_after_cleaning = len(df)

    categorical_columns = [
        "Shipping Mode",
        "Order Region",
        "Market",
        "Customer Segment",
        "Order Country"
    ]

    for column in categorical_columns:
        df[column] = (
            df[column]
            .astype(str)
            .str.strip()
        )

    df[ACTUAL_COL] = pd.to_numeric(
        df[ACTUAL_COL],
        errors="coerce"
    )

    df[SCHEDULED_COL] = pd.to_numeric(
        df[SCHEDULED_COL],
        errors="coerce"
    )

    invalid_duration_mask = (
        df[[ACTUAL_COL, SCHEDULED_COL]]
        .isna()
        .any(axis=1)
        |
        (df[ACTUAL_COL] < 0)
        |
        (df[SCHEDULED_COL] < 0)
    )

    invalid_duration_rows = int(
        invalid_duration_mask.sum()
    )

    if invalid_duration_rows > 0:

        df = df[
            df[ACTUAL_COL].notna()
            &
            df[SCHEDULED_COL].notna()
            &
            (df[ACTUAL_COL] >= 0)
            &
            (df[SCHEDULED_COL] >= 0)
        ].copy()

    df["Delay Gap"] = (
        df[ACTUAL_COL]
        -
        df[SCHEDULED_COL]
    )

    df["Delivery Timing"] = (
        df["Delay Gap"]
        .apply(classify_delivery)
    )

    quality_summary = {
        "Raw Records": raw_rows,
        "Records After Missing-Value Cleaning": rows_after_cleaning,
        "Records Used for Analysis": len(df),
        "Records Removed": raw_rows - len(df),
        "Invalid Shipping-Duration Records":
            invalid_duration_rows
    }

    return df, quality_summary


def apply_filters(data):

    filtered_df = data.copy()

    if st.session_state.shipping_mode_filter:

        filtered_df = filtered_df[
            filtered_df["Shipping Mode"].isin(
                st.session_state.shipping_mode_filter
            )
        ]

    if st.session_state.region_filter:

        filtered_df = filtered_df[
            filtered_df["Order Region"].isin(
                st.session_state.region_filter
            )
        ]

    if st.session_state.market_filter:

        filtered_df = filtered_df[
            filtered_df["Market"].isin(
                st.session_state.market_filter
            )
        ]

    if st.session_state.segment_filter:

        filtered_df = filtered_df[
            filtered_df["Customer Segment"].isin(
                st.session_state.segment_filter
            )
        ]

    return filtered_df


df, quality_summary = load_data()


st.title(
    "🚚 Global Supply Chain Delivery Performance Dashboard"
)

st.markdown(
    """
    **Delivery Performance, Delay Risk, and Logistics Efficiency Analysis**

    Analyze shipment delivery performance, delay risk, shipping-mode
    efficiency, customer segments, regions, countries, and markets.
    """
)


st.sidebar.header(
    "🔎 Dashboard Filters"
)


st.sidebar.multiselect(
    "Shipping Mode",
    options=sorted(
        df["Shipping Mode"].unique()
    ),
    default=[],
    key="shipping_mode_filter"
)


st.sidebar.multiselect(
    "Order Region",
    options=sorted(
        df["Order Region"].unique()
    ),
    default=[],
    key="region_filter"
)


st.sidebar.multiselect(
    "Market",
    options=sorted(
        df["Market"].unique()
    ),
    default=[],
    key="market_filter"
)


st.sidebar.multiselect(
    "Customer Segment",
    options=sorted(
        df["Customer Segment"].unique()
    ),
    default=[],
    key="segment_filter"
)


with st.sidebar.expander(
    "Data Quality & Methodology"
):

    st.write(
        f"Raw records: "
        f"{quality_summary['Raw Records']:,}"
    )

    st.write(
        f"Records used: "
        f"{quality_summary['Records Used for Analysis']:,}"
    )

    st.write(
        f"Records removed: "
        f"{quality_summary['Records Removed']:,}"
    )

    st.write(
        f"Invalid shipping-duration records: "
        f"{quality_summary['Invalid Shipping-Duration Records']:,}"
    )

    st.caption(
        "Delay Gap = actual shipping days − scheduled shipping days."
    )

    st.caption(
        "Negative Delay Gap = Early | "
        "Zero = On-time | "
        "Positive = Delayed"
    )


filtered_df = apply_filters(df)


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

    st.header(
        "📊 Delivery Performance Overview"
    )

    total_shipments = len(
        filtered_df
    )

    on_time_shipments = int(
        (
            filtered_df["Delivery Timing"]
            == "On-time"
        ).sum()
    )

    delayed_shipments = int(
        (
            filtered_df["Delivery Timing"]
            == "Delayed"
        ).sum()
    )

    early_shipments = int(
        (
            filtered_df["Delivery Timing"]
            == "Early"
        ).sum()
    )

    on_time_rate = (
        on_time_shipments
        /
        total_shipments
        *
        100
    )

    late_rate = (
        delayed_shipments
        /
        total_shipments
        *
        100
    )

    average_delay = (
        filtered_df["Delay Gap"]
        .mean()
    )

    dataset_risk_ratio = (
        filtered_df["Late_delivery_risk"]
        .mean()
        *
        100
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Shipments",
        f"{total_shipments:,}"
    )

    col2.metric(
        "On-Time Delivery",
        f"{on_time_rate:.2f}%"
    )

    col3.metric(
        "Late Delivery",
        f"{late_rate:.2f}%"
    )

    col4.metric(
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
        .rename_axis(
            "Delivery Timing"
        )
        .reset_index(
            name="Shipments"
        )
    )

    delivery_timing[
        "Percentage (%)"
    ] = (
        delivery_timing["Shipments"]
        /
        total_shipments
        *
        100
    )


    fig_delivery = px.bar(
        delivery_timing,
        x="Delivery Timing",
        y="Shipments",
        text="Shipments",
        title="Delivery Timing Distribution"
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
                "Late Delivery Risk Ratio (%)",
                "Dataset Late_delivery_risk (%)"
            ],
            "Value": [
                total_shipments,
                on_time_shipments,
                delayed_shipments,
                early_shipments,
                on_time_rate,
                late_rate,
                average_delay,
                late_rate,
                dataset_risk_ratio
            ]
        }
    )


    st.dataframe(
        performance_summary.round(2),
        use_container_width=True,
        hide_index=True
    )


    st.subheader(
        "Customer Segment Impact Analysis"
    )


    segment_performance = (
        filtered_df
        .groupby(
            "Customer Segment"
        )
        .agg(
            Total_Shipments=(
                "Customer Segment",
                "size"
            ),
            Average_Delay=(
                "Delay Gap",
                "mean"
            ),
            Delayed_Shipments=(
                "Delivery Timing",
                lambda x:
                (x == "Delayed").sum()
            ),
            At_Risk_Shipments=(
                "Late_delivery_risk",
                "sum"
            )
        )
        .reset_index()
    )


    segment_performance[
        "Delay Frequency (%)"
    ] = (
        segment_performance[
            "Delayed_Shipments"
        ]
        /
        segment_performance[
            "Total_Shipments"
        ]
        *
        100
    )


    segment_performance[
        "SLA Risk Exposure (%)"
    ] = (
        segment_performance[
            "At_Risk_Shipments"
        ]
        /
        segment_performance[
            "Total_Shipments"
        ]
        *
        100
    )


    fig_segment = px.bar(
        segment_performance.sort_values(
            "Delay Frequency (%)",
            ascending=False
        ),
        x="Customer Segment",
        y="Delay Frequency (%)",
        text_auto=".2f",
        title="Customer Segment Delay Frequency"
    )


    st.plotly_chart(
        fig_segment,
        use_container_width=True
    )


    st.dataframe(
        segment_performance.round(2),
        use_container_width=True,
        hide_index=True
    )


with tab2:

    st.header(
        "⚠️ Delay Risk Analysis"
    )


    risk_distribution = (
        filtered_df[
            "Late_delivery_risk"
        ]
        .value_counts()
        .sort_index()
        .rename_axis(
            "Late Delivery Risk"
        )
        .reset_index(
            name="Shipments"
        )
    )


    risk_distribution[
        "Risk Label"
    ] = (
        risk_distribution[
            "Late Delivery Risk"
        ]
        .map(
            {
                0: "No Risk",
                1: "At Risk"
            }
        )
    )


    risk_distribution[
        "Percentage (%)"
    ] = (
        risk_distribution[
            "Shipments"
        ]
        /
        total_shipments
        *
        100
    )


    col1, col2 = st.columns(2)


    with col1:

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
                "Delay Gap":
                "Delay Gap (Days)"
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


    st.dataframe(
        risk_distribution[
            [
                "Late Delivery Risk",
                "Risk Label",
                "Shipments",
                "Percentage (%)"
            ]
        ].round(2),
        use_container_width=True,
        hide_index=True
    )


    st.subheader(
        "Delay Gap Summary"
    )


    delay_summary = pd.DataFrame(
        {
            "Metric": [
                "Minimum Delay Gap (Days)",
                "Average Delay Gap (Days)",
                "Maximum Delay Gap (Days)",
                "Delayed Shipments (%)"
            ],
            "Value": [
                filtered_df[
                    "Delay Gap"
                ].min(),
                filtered_df[
                    "Delay Gap"
                ].mean(),
                filtered_df[
                    "Delay Gap"
                ].max(),
                late_rate
            ]
        }
    )


    st.dataframe(
        delay_summary.round(2),
        use_container_width=True,
        hide_index=True
    )


with tab3:

    st.header(
        "🚚 Shipping Mode Comparison"
    )


    mode_performance = (
        filtered_df
        .groupby(
            "Shipping Mode"
        )
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
                lambda x:
                (x == "Delayed").sum()
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
        /
        mode_performance[
            "Total_Shipments"
        ]
        *
        100
    )


    mode_performance[
        "SLA Compliance (%)"
    ] = (
        100
        -
        mode_performance[
            "Delay Frequency (%)"
        ]
    )


    mode_performance[
        "Shipping Mode Efficiency Index"
    ] = (
        mode_performance[
            "SLA Compliance (%)"
        ]
    )


    col1, col2 = st.columns(2)


    with col1:

        fig_mode_delay = px.bar(
            mode_performance.sort_values(
                "Average_Delay",
                ascending=False
            ),
            x="Shipping Mode",
            y="Average_Delay",
            text_auto=".2f",
            title="Mode-wise Delay Performance",
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
            mode_performance.sort_values(
                "SLA Compliance (%)"
            ),
            x="Shipping Mode",
            y="SLA Compliance (%)",
            text_auto=".2f",
            title="SLA Compliance by Shipping Mode"
        )

        st.plotly_chart(
            fig_sla,
            use_container_width=True
        )


    st.subheader(
        "Shipping Mode Performance"
    )


    st.dataframe(
        mode_performance.sort_values(
            "Delay Frequency (%)",
            ascending=False
        ).round(2),
        use_container_width=True,
        hide_index=True
    )


    st.subheader(
        "Shipping Mode × Delivery Status"
    )


    mode_status = (
        filtered_df
        .groupby(
            [
                "Shipping Mode",
                "Delivery Status"
            ]
        )
        .agg(
            Shipments=(
                "Delivery Status",
                "size"
            ),
            Average_Delay=(
                "Delay Gap",
                "mean"
            )
        )
        .reset_index()
    )


    mode_status[
        "Share Within Mode (%)"
    ] = (
        mode_status["Shipments"]
        /
        mode_status.groupby(
            "Shipping Mode"
        )["Shipments"]
        .transform("sum")
        *
        100
    )


    fig_mode_status = px.bar(
        mode_status,
        x="Shipping Mode",
        y="Shipments",
        color="Delivery Status",
        barmode="group",
        title="Delivery Status by Shipping Mode"
    )


    st.plotly_chart(
        fig_mode_status,
        use_container_width=True
    )


    st.dataframe(
        mode_status.round(2),
        use_container_width=True,
        hide_index=True
    )


with tab4:

    st.header(
        "🌍 Regional & Market Heatmaps"
    )


    regional_performance = (
        filtered_df
        .groupby(
            "Order Region"
        )
        .agg(
            Total_Shipments=(
                "Order Region",
                "size"
            ),
            Average_Delay=(
                "Delay Gap",
                "mean"
            ),
            Delayed_Shipments=(
                "Delivery Timing",
                lambda x:
                (x == "Delayed").sum()
            )
        )
        .reset_index()
    )


    regional_performance[
        "Regional Delay Index (%)"
    ] = (
        regional_performance[
            "Delayed_Shipments"
        ]
        /
        regional_performance[
            "Total_Shipments"
        ]
        *
        100
    )


    regional_performance = (
        regional_performance
        .sort_values(
            "Regional Delay Index (%)",
            ascending=False
        )
    )


    market_performance = (
        filtered_df
        .groupby(
            "Market"
        )
        .agg(
            Total_Shipments=(
                "Market",
                "size"
            ),
            Average_Delay=(
                "Delay Gap",
                "mean"
            ),
            Delayed_Shipments=(
                "Delivery Timing",
                lambda x:
                (x == "Delayed").sum()
            )
        )
        .reset_index()
    )


    market_performance[
        "Market Delay Index (%)"
    ] = (
        market_performance[
            "Delayed_Shipments"
        ]
        /
        market_performance[
            "Total_Shipments"
        ]
        *
        100
    )


    market_performance[
        "Logistics Efficiency Index (%)"
    ] = (
        100
        -
        market_performance[
            "Market Delay Index (%)"
        ]
    )


    region_market_heatmap = (
        filtered_df
        .assign(
            Delayed=(
                filtered_df[
                    "Delivery Timing"
                ]
                == "Delayed"
            ).astype(int)
        )
        .pivot_table(
            index="Order Region",
            columns="Market",
            values="Delayed",
            aggfunc="mean"
        )
        *
        100
    )



    country_map = country_performance.copy()

    country_map["Map Country"] = (
        country_map["Order Country"]
        .apply(country_to_map_name)
    )

    fig_country_map = px.choropleth(
        country_map,
        locations="Map Country",
        locationmode="country names",
        color="Delay Frequency (%)",
        hover_name="Order Country",
        hover_data={
            "Map Country": False,
            "Total_Shipments": ":,",
            "Delayed_Shipments": ":,",
            "Delay Frequency (%)": ":.2f",
            "Average_Delay": ":.2f"
        },
        color_continuous_scale="Blues",
        title="Global Geographic Delay Visualization",
        labels={
            "Delay Frequency (%)": "Delay Frequency (%)",
            "Total_Shipments": "Total Shipments",
            "Delayed_Shipments": "Delayed Shipments",
            "Average_Delay": "Average Delay (Days)"
        }
    )

    fig_country_map.update_geos(
        showframe=False,
        showcoastlines=True,
        showland=True,
        projection_type="natural earth"
    )

    fig_country_map.update_layout(
        height=600,
        margin=dict(l=0, r=0, t=60, b=0)
    )

    st.plotly_chart(
        fig_country_map,
        use_container_width=True
    )

    st.caption(
        "Country color represents delay frequency. Hover over a country for shipment volume, delayed shipments, and average delay."
    )

    col1, col2 = st.columns(2)


    with col1:

        fig_region_heatmap = px.imshow(
            region_market_heatmap,
            text_auto=".1f",
            aspect="auto",
            title="Regional × Market Delay Heatmap",
            labels={
                "x": "Market",
                "y": "Order Region",
                "color":
                "Delay Frequency (%)"
            }
        )

        st.plotly_chart(
            fig_region_heatmap,
            use_container_width=True
        )


    with col2:

        fig_market = px.bar(
            market_performance.sort_values(
                "Average_Delay",
                ascending=False
            ),
            x="Market",
            y="Average_Delay",
            text_auto=".2f",
            title="Market-wise Logistics Efficiency",
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
        regional_performance.round(2),
        use_container_width=True,
        hide_index=True
    )


    st.subheader(
        "Market Logistics Performance"
    )


    st.dataframe(
        market_performance.round(2),
        use_container_width=True,
        hide_index=True
    )


    st.subheader(
        "Country Delay Diagnostics"
    )


    st.caption(
        "Country delay rates should be interpreted together "
        "with shipment volume, especially for low-volume countries."
    )


    country_performance = (
        filtered_df
        .groupby(
            "Order Country"
        )
        .agg(
            Total_Shipments=(
                "Order Country",
                "size"
            ),
            Average_Delay=(
                "Delay Gap",
                "mean"
            ),
            Delayed_Shipments=(
                "Delivery Timing",
                lambda x:
                (x == "Delayed").sum()
            )
        )
        .reset_index()
    )


    country_performance[
        "Delay Frequency (%)"
    ] = (
        country_performance[
            "Delayed_Shipments"
        ]
        /
        country_performance[
            "Total_Shipments"
        ]
        *
        100
    )


    st.dataframe(
        country_performance.sort_values(
            [
                "Delay Frequency (%)",
                "Total_Shipments"
            ],
            ascending=[
                False,
                False
            ]
        ).round(2),
        use_container_width=True,
        hide_index=True
    )