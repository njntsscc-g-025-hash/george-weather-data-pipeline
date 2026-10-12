# george-weather-data-pipeline

Automated ETL pipeline that collects, stores, and visualizes hourly weather data for George, Western Cape, South Africa.

## Problem
Weather APIs give you live data only. There is no historical record for George. This pipeline builds that history automatically.

## Architecture
**OpenWeatherMap API -> Python (Extract) -> PostgreSQL (Raw Layer: weather_raw) -> Python Transform (Kelvin to Celsius, data quality checks) -> PostgreSQL (Clean Layer: weather_clean) -> Streamlit Dashboard**

- **Ingestion:** Hourly extraction of temp, humidity, wind, description
- **Raw Layer:** Stores exact JSON response for traceability (Medallion Architecture)
- **Clean Layer:** Transformed, validated, ready for analytics
- **Orchestration:** Apache Airflow DAG scheduled hourly
- **Visualization:** Streamlit dashboard for 7-day trends

## Tech Stack
Python, PostgreSQL, Apache Airflow, Streamlit, OpenWeatherMap API, Docker

## Project Structure
/george-weather-data-pipeline
├── dags/
├── scripts/
├── sql/
└── dashboard/

## Status
In Progress - Building ETL scripts
