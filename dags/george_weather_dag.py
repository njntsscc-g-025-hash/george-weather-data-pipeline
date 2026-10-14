import sys
from datetime import datetime, timedelta
from pathlib import Path

from airflow.sdk import dag, task

# make the scripts/ folder importable
sys.path.append(str(Path(__file__).resolve().parents[1] / "scripts"))

default_args = {
    "owner": "george-pipeline",
    "retries": 3,                       # retry up to 3 times if the API or DB fails
    "retry_delay": timedelta(minutes=5),
}


@dag(
    dag_id="george_weather_hourly",
    schedule="@hourly",
    start_date=datetime(2026, 10, 1),
    catchup=False,                      # weather is live, so don't backfill old hours
    default_args=default_args,
    tags=["weather", "etl"],
)
def george_weather():
    @task
    def run_etl():
        from extract_load import extract, transform, load

        payload = extract()
        row = transform(payload)
        load(payload, row)
        print("Saved!", row)

    @task
    def update_daily_summary():
        from transform import run

        run()

    run_etl() >> update_daily_summary()


george_weather()
