# AI Job Market & Cost-of-Living Explorer

Explore the intersection of AI job salaries and cost-of-living data to discover the true purchasing power of AI professionals worldwide.
<img width="1154" alt="Screenshot 2025-06-07 at 4 51 58 AM" src="https://github.com/user-attachments/assets/726e666d-611b-45e9-a7c7-a729a6a783c4" />

## Overview

This repository contains a **Preswald** application that merges:
- **Global AI Job Market & Salary Trends 2025** dataset (15,000+ AI/ML positions)
- **Numbeo Cost-of-Living Data** (relative to NYC = 100)

Key features include:
- **Data Quality Checks**: Basic stats, missing values, outlier identification
- **SQL Queries**: DuckDB for advanced filtering and aggregation
- **Visualizations**: Plotly-based charts for salaries, cost-of-living, remote ratio, etc.
- **PPP (Purchasing Power Parity) Adjustments**: Weighted CoL indices + local purchasing power
- **Aggressive Filtering**: Outlier removal, clamped indexes, ensuring more realistic insights

## Requirements

Before running this app, please ensure you have the following libraries installed (Python 3.7+ recommended):

- **pandas** `>=1.0`
- **plotly** `>=5.0`
- **duckdb** `>=0.7`
- **statsmodel** 
- **preswald** (the Preswald framework)
- **pyarrow** (often a dependency for DuckDB)
- **numpy** (common numeric library)
