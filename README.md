# Delivery Performance, Delay Risk, and Logistics Efficiency Analysis

An exploratory data analysis project that examines delivery performance in global supply chain operations using the supplied APL Logistics dataset. The project combines data preparation, delivery-gap analysis, category-level comparisons, and an interactive Streamlit dashboard.

**🚀 Live Dashboard:** [Open the Streamlit App](https://global-supply-chain-operations-dashboard.streamlit.app/)

## Overview

Delivery delays can affect service commitments, operational planning, and customer experience. This project analyses the difference between actual and scheduled shipping durations and compares delivery outcomes across shipping modes, geographic regions, markets, and customer segments.

The analysis distinguishes the timing category calculated from shipping durations from the dataset's existing `Delivery Status` and `Late_delivery_risk` fields. The dashboard is designed for descriptive monitoring and exploration; it is not a predictive model and does not establish the causes of delays.

## Objectives

- Clean and prepare the supplied logistics dataset.
- Calculate delivery gaps and classify records as **Early**, **On-time**, or **Delayed**.
- Summarise delivery performance using counts, percentages, and the mean delivery gap.
- Compare delivery outcomes across shipping modes, regions, countries, markets, and customer segments.
- Examine the supplied late-delivery-risk indicator separately from calculated timing outcomes.
- Present results in an interactive Streamlit dashboard.

## Dataset

The supplied dataset contains **180,519 records and 40 attributes**. After removing 11 records with missing values, **180,508 records** were retained for the principal analysis. The cleaned dataset contains no duplicate rows.

| Field | Purpose |
|---|---|
| `Days for shipping (real)` | Actual shipping duration |
| `Days for shipment (scheduled)` | Scheduled shipping duration |
| `Delivery Status` | Existing delivery-status label |
| `Late_delivery_risk` | Existing binary risk indicator |
| `Shipping Mode` | Shipping-service category |
| `Order Region` | Geographic grouping |
| `Order Country` | Country-level comparison |
| `Market` | Market grouping |
| `Customer Segment` | Consumer, Corporate, or Home Office |

**Data note:** The dataset does not contain an explicit order, shipping, or delivery date. Therefore, calendar-based trend analysis and a genuine date-range filter are not included.

If the dataset is not included in this repository, obtain it from the source provided for the project and place it at the path expected by the application. Do not redistribute data unless its licence and permissions allow it.

## Methodology

### 1. Data preparation

- Load the dataset into a Pandas DataFrame.
- Handle records containing missing values.
- Prepare categorical fields and convert shipping-duration fields to numeric values.
- Check relevant fields before calculating derived measures.

### 2. Delivery-gap calculation

For each record:

\[
\text{Delivery Gap} = \text{Actual Shipping Duration} - \text{Scheduled Shipping Duration}
\]

| Condition | Calculated category |
|---|---|
| Delivery gap < 0 | Early |
| Delivery gap = 0 | On-time |
| Delivery gap > 0 | Delayed |

This is the study's analytical definition based on the available duration fields. It is not necessarily equivalent to a contractual service-level agreement (SLA) breach or to the dataset's existing status and risk labels.

### 3. Exploratory analysis

The notebook explores overall delivery-timing outcomes and compares delivery measures across shipping modes, regions, countries, markets, and customer segments. Counts and percentages are considered together: counts show how many records are affected, while percentages show the frequency within a category.

## Key Findings

The following figures are calculated from the cleaned dataset using the delivery-gap definition above.

| Measure | Result |
|---|---:|
| Original records | 180,519 |
| Records retained after cleaning | 180,508 |
| Delayed | 103,395 (57.28%) |
| Early | 43,363 (24.02%) |
| On-time | 33,750 (18.70%) |
| Mean signed delivery gap | Approximately 0.566 days |
| Records with `Late_delivery_risk = 1` | Approximately 54.83% |

### Interpretation

- More than half of the cleaned records have an actual shipping duration greater than the scheduled duration under the study's definition.
- The mean signed delivery gap includes early, on-time, and delayed records; it is not the average delay among delayed records only.
- The supplied `Late_delivery_risk` indicator and the calculated delivery-gap category are distinct. Their aggregate percentages differ, but that alone does not establish record-level disagreement.
- Differences across shipping modes and geographic categories are descriptive and do not prove that a category causes delays.

## Interactive Dashboard

**[Launch the live Streamlit dashboard](https://global-supply-chain-operations-dashboard.streamlit.app/)**

The dashboard contains four views:

1. **Delivery Performance Overview** — summarises the delivery-timing distribution and principal measures.
2. **Delay Risk Analysis** — examines the supplied `Late_delivery_risk` indicator alongside calculated delivery-gap measures.
3. **Shipping Mode Comparison** — compares First Class, Second Class, Same Day, and Standard Class.
4. **Regional and Market Heatmaps** — explores differences across order regions and market categories.

Available filters:

- Shipping Mode
- Order Region
- Market
- Customer Segment

The displayed metrics depend on the active filters. A genuine calendar-based date filter is not available because the dataset lacks an explicit date field.

## Technology Stack

- **Language:** Python
- **Data analysis:** Pandas, NumPy
- **Visualisation:** plotting libraries used by the notebook and dashboard
- **Interactive application:** Streamlit
- **Analysis environment:** Jupyter Notebook
- **Version control:** Git

Confirm the exact plotting packages and dependency versions using the project's notebook, `app.py`, and `requirements.txt`.

## Project Structure

The following is an illustrative layout based on the project files. Adjust filenames and paths to match the actual repository.

```text
GSCDP/
├── Dashboard_Streamlit/
│   └── app.py
├── dataset/
│   └── APL_Logistics.csv
├── notebooks/
│   └── Global_Supply_Chain_Operations.ipynb
├── requirements.txt
└── README.md
```

## Run Locally

### Prerequisites

- Python version supported by the project's dependencies
- Git
- The dataset required by the application

### 1. Clone the repository

```bash
git clone https://github.com/Mainak156/GSCDP.git
cd GSCDP
```

### 2. Create a virtual environment

**Windows PowerShell:**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS/Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If the dependency file is stored inside the dashboard directory, use its actual path.

### 4. Add the dataset

Place the CSV at the path expected by `Dashboard_Streamlit/app.py`. The project configuration has been described as using:

```text
dataset/APL_Logistics.csv
```

Check the path in `app.py` before running the application.

### 5. Start Streamlit

From the repository root:

```bash
streamlit run Dashboard_Streamlit/app.py
```

Open the local URL shown in the terminal, commonly `http://localhost:8501`. If the application entry point has a different path, update the command accordingly.

## Metric Definitions

### Delay frequency

\[
\text{Delay Frequency} =
\frac{\text{Records with delivery gap} > 0}
{\text{Records in the selected group}} \times 100
\]

### On-time rate

\[
\text{On-time Rate} =
\frac{\text{Records with delivery gap} = 0}
{\text{Records in the selected group}} \times 100
\]

### Mean signed delivery gap

\[
\text{Mean Delivery Gap} =
\frac{1}{N}\sum_{i=1}^{N}
(\text{Actual Duration}_i-\text{Scheduled Duration}_i)
\]

Early records contribute negative values, so the mean signed gap is not the same as the average delay among delayed records.

### Supplied late-delivery-risk ratio

The percentage of selected records for which the existing `Late_delivery_risk` field equals `1`. This is reported separately from duration-based delay frequency.

## Limitations

- The analysis is descriptive and does not establish causality.
- The project does not train or evaluate a predictive delay model.
- The absence of an explicit date field prevents calendar-based trend analysis.
- The supplied risk indicator and delivery-status labels may use definitions different from the calculated timing category.
- Differences in category sizes affect interpretation; counts and percentages should be reviewed together.
- Removing records with missing values may affect the composition of the analytical sample.
- Results describe the supplied dataset and should not automatically be generalised to all logistics providers.

## Future Improvements

- Construct record-level cross-tabulations to assess agreement between the calculated timing category, `Delivery Status`, and `Late_delivery_risk`.
- Report sample sizes alongside country- and region-level delay rates.
- Add validated date fields for temporal and seasonal analysis.
- Investigate additional variables such as routes, carrier characteristics, weather, or customs-processing times if reliable data become available.
- Develop and evaluate a predictive model as a separate extension, with appropriate train/test separation and evaluation metrics.
- Test whether category differences remain after accounting for relevant shipment characteristics.

These are proposed extensions, not capabilities claimed by the current descriptive dashboard.

## Research Paper

**Title:** *Delivery Performance, Delay Risk, and Logistics Efficiency Analysis in Global Supply Chain Operations.*

The paper documents the dataset, methodology, exploratory analysis, findings, contributions, dashboard, limitations, and future research directions.

## Author

**Mainak Sen**  
B.Tech. in Computer Science and Engineering  
Specialization in Artificial Intelligence and Machine Learning  
SRM Institute of Science and Technology, Kattankulathur, Tamil Nadu

- **GitHub profile:** [Mainak156](https://github.com/Mainak156)
- **Live dashboard:** [Open Streamlit App](https://global-supply-chain-operations-dashboard.streamlit.app/)

---

*This project is intended for educational, analytical, and research purposes. Interpret results within the definitions and limitations described above.*
