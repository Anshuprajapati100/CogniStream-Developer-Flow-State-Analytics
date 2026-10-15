# CogniStream: Developer Flow-State & Cognitive Load Analytics

## Project Overview

CogniStream is a Python-based Data Analytics project developed as part of the Infotact Solutions internship.

The project analyzes developer coding sessions, interruptions, context switching, focus ratings, and cognitive workload indicators.

It provides an interactive Streamlit dashboard to visualize developer activity patterns and experimental flow-state indicators.

## Problem Statement

Software developers frequently experience interruptions, task switching, and changes in concentration during coding sessions.

Analyzing these activity patterns can help identify potential factors associated with focused work and perceived cognitive workload.

CogniStream provides a data analytics prototype for exploring these relationships.

## Project Objectives

- Collect and organize developer activity data.
- Clean and validate session records.
- Perform exploratory data analysis.
- Analyze coding activity and interruptions.
- Calculate experimental flow indicator scores.
- Examine cognitive load ratings.
- Develop an interactive analytics dashboard.
- Generate downloadable reports.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python 3.12 | Programming |
| Pandas | Data processing and analysis |
| NumPy | Numerical operations |
| Matplotlib | Data visualization library |
| Plotly | Interactive visualizations |
| Streamlit | Dashboard development |
| Git | Version control |
| GitHub | Source code repository |
| VS Code | Development environment |

## Project Structure

```text
CogniStream/
├── dashboard/
│   ├── app.py
│   └── app_v1_backup.py
├── data/
│   ├── raw/
│   └── processed/
├── notebooks/
├── reports/
├── src/
│   ├── __init__.py
│   ├── data_collection.py
│   ├── data_cleaning.py
│   ├── analytics.py
│   └── cognitive_load.py
├── tests/
│   └── test_pipeline.py
├── .gitignore
├── README.md
└── requirements.txt
```

## Dataset

The current prototype uses a synthetic dataset containing:

- 120 developer sessions
- 4 fictional developers
- 13 original dataset columns

The dataset includes session duration, coding time, idle time, interruptions, context switches, completed tasks, focus ratings, and cognitive load ratings.

The dataset is artificially generated for development and demonstration purposes.

## Project Workflow

```text
Synthetic Data Generation
          |
          v
Data Cleaning & Validation
          |
          v
Exploratory Data Analysis
          |
          v
Flow Indicator Calculation
          |
          v
Cognitive Load Rating Analysis
          |
          v
Interactive Streamlit Dashboard
          |
          v
Analytics Reports
```

## Flow Indicator Methodology

The prototype calculates an experimental flow indicator using:

- Coding activity: 35%
- Interruption component: 25%
- Context-switching component: 20%
- Focus rating component: 20%

Formula:

Flow Indicator =
0.35 × Coding Component
+ 0.25 × Interruption Component
+ 0.20 × Context-Switching Component
+ 0.20 × Focus Component

The component values are normalized to a 0–100 scale.

Flow indicator bands:

| Score | Classification |
|---|---|
| 0–40 | Low |
| Above 40–70 | Moderate |
| Above 70–100 | High |

These thresholds and weights are prototype assumptions, not scientifically validated flow-state measures.

## Cognitive Load Analysis

The project uses simulated cognitive load ratings on a scale of 1–5.

| Rating | Classification |
|---|---|
| 1–2 | Low |
| 3 | Moderate |
| 4–5 | High |

These ratings are synthetic and should not be interpreted as actual psychological assessments.

## Analytics Results

Results from the current synthetic dataset:

| Metric | Value |
|---|---|
| Total Sessions | 120 |
| Total Developers | 4 |
| Total Coding Hours | 176.90 |
| Average Session Duration | 121.69 minutes |
| Average Coding Time | 88.45 minutes |
| Overall Coding Activity | 72.68% |
| Total Interruptions | 447 |
| Total Context Switches | 663 |
| Average Focus Rating | 3.19/5 |
| Average Cognitive Load Rating | 3.01/5 |
| Average Flow Indicator | 65.79/100 |

### Flow Indicator Distribution

| Classification | Sessions |
|---|---|
| Low | 4 |
| Moderate | 73 |
| High | 43 |

### Cognitive Load Rating Distribution

| Classification | Sessions |
|---|---|
| Low | 45 |
| Moderate | 30 |
| High | 45 |

All results are based on synthetic data.

## Dashboard Features

CogniStream Dashboard V2 provides four sections:

### 1. Overview
- Key performance indicators
- Daily coding activity
- Interruption frequency charts
- Context-switching charts

### 2. Developer Analytics
- Developer-level activity statistics
- Coding hours comparison
- Average flow indicator comparison

### 3. Flow & Cognitive Load
- Flow indicator distribution
- Simulated cognitive load distribution
- Interruption rate and flow indicator visualization

### 4. Session Explorer
- Developer session records
- Developer filtering
- Date range filtering
- CSV download

## Installation

Clone the repository:

```bash
git clone https://github.com/Anshuprajapati100/CogniStream-Developer-Flow-State-Analytics.git
```

Enter the project directory:

```bash
cd CogniStream-Developer-Flow-State-Analytics
```

Create a virtual environment using Python 3.12:

```bash
python3.12 -m venv .venv
```

Activate it on macOS or Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

## Run the Analytics Pipeline

Run these commands in order:

```bash
python src/data_collection.py
python src/data_cleaning.py
python src/analytics.py
python src/cognitive_load.py
```

## Run the Dashboard

```bash
streamlit run dashboard/app.py
```

Open:

http://localhost:8501

## Testing

The project includes 14 automated pipeline validation tests.

Run:

```bash
python -m unittest discover -s tests -v
```

Latest confirmed test result:

```text
Ran 14 tests

OK
```

These tests cover generated data integrity, session consistency, valid ratings, and output classifications.

Additional unit and dashboard interaction testing remains part of final verification.

## Limitations

- The current dataset is synthetic.
- Developer focus ratings are simulated.
- Cognitive load ratings are simulated.
- Flow indicator weights and thresholds are heuristic.
- Coding activity does not independently establish productivity.
- Flow-state classifications are not psychological diagnoses.
- No real-time developer monitoring is implemented.
- Current findings are illustrative, not real-world causal conclusions.

## Future Scope

- Consent-based real developer activity collection.
- Privacy-preserving activity analysis.
- Additional dashboard visualizations.
- Longitudinal developer work-pattern analysis.
- Validated self-report questionnaires.
- Evaluation of flow indicator assumptions.
- Optional machine learning after collecting suitable data.

## Project Information

**Project:** CogniStream: Developer Flow-State & Cognitive Load Analytics

**Organization:** Infotact Solutions

**Internship Domain:** Data Analytics

**Internship Role:** Data Associate L1 Intern

**Project Period:** 12 October 2026 – 12 November 2026

**Developer:** Anshu Suresh Prajapati

## Conclusion

CogniStream demonstrates an end-to-end developer activity analytics workflow using Python, Pandas, Plotly, and Streamlit.

It provides data generation, validation, exploratory analytics, experimental flow indicators, cognitive load rating analysis, interactive visualizations, and report generation.

The current implementation is a synthetic-data prototype intended for learning, experimentation, and further evaluation.
