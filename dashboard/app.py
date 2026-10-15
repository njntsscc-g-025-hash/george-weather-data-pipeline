import os
from pathlib import Path

import altair as alt
import pandas as pd
import psycopg2
import streamlit as st
from dotenv import load_dotenv

# the .env file lives in the project root, one folder up
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

st.set_page_config(page_title="George Weather", page_icon="🌤️", layout="wide")


def query(sql):
    conn = psycopg2.connect(
        host=os.environ["POSTGRES_HOST"],
        port=os.environ["POSTGRES_PORT"],
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
    )
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
            cols = [c.name for c in cur.description]
            return pd.DataFrame(cur.fetchall(), columns=cols)
    finally:
        conn.close()


def to_local(series):
    """UTC timestamps -> George local time (no timezone label, for charts)."""
    return (
        pd.to_datetime(series, utc=True)
        .dt.tz_convert("Africa/Johannesburg")
        .dt.tz_localize(None)
    )


def trend_chart(df, column, label):
    data = df.reset_index()
    return (
        alt.Chart(data)
        .mark_line(point=True)
        .encode(
            x=alt.X("observed_at:T", title="Time (George)"),
            y=alt.Y(f"{column}:Q", title=label, scale=alt.Scale(zero=False)),
            tooltip=["observed_at:T", f"{column}:Q"],
        )
    )


@st.cache_data(ttl=300)
def load_data():
    latest = query(
        """SELECT observed_at, temp_c, humidity, wind_speed, description
           FROM weather_clean WHERE city = 'George'
           ORDER BY observed_at DESC LIMIT 1"""
    )
    recent = query(
        """SELECT observed_at, temp_c, humidity, wind_speed
           FROM weather_clean
           WHERE city = 'George' AND observed_at >= NOW() - INTERVAL '7 days'
           ORDER BY observed_at"""
    )
    daily = query(
        """SELECT observation_date AS date, avg_temp_c, min_temp_c, max_temp_c,
                  avg_humidity, avg_wind_speed, reading_count
           FROM weather_daily_avg WHERE city = 'George'
           ORDER BY observation_date DESC LIMIT 7"""
    )
    return latest, recent, daily


st.title("🌤️ George, Western Cape: Live Weather Analytics")
st.caption("Data collected hourly from OpenWeatherMap by an Airflow pipeline into PostgreSQL.")

latest, recent, daily = load_data()

if latest.empty:
    st.warning("No weather data yet. Run the pipeline first.")
    st.stop()

row = latest.iloc[0]
observed = to_local(latest["observed_at"]).iloc[0]

c1, c2, c3, c4 = st.columns(4)
c1.metric("Temperature", f"{row['temp_c']:.1f} °C")
c2.metric("Humidity", f"{int(row['humidity'])} %")
c3.metric("Wind", f"{row['wind_speed']:.1f} m/s")
c4.metric("Conditions", str(row["description"]).title())
st.caption(f"Last reading: {observed:%Y-%m-%d %H:%M} (George time)")

recent["observed_at"] = to_local(recent["observed_at"])
recent = recent.set_index("observed_at")

st.subheader("Temperature, last 7 days")
st.altair_chart(trend_chart(recent, "temp_c", "°C"), width="stretch")

st.subheader("Humidity trend, last 7 days")
st.altair_chart(trend_chart(recent, "humidity", "%"), width="stretch")

st.subheader("Daily summary")
st.dataframe(daily, width="stretch", hide_index=True)

st.caption(f"{len(recent)} hourly readings in the last 7 days.")

if st.button("Refresh data"):
    st.cache_data.clear()
    st.rerun()
