import os
from datetime import datetime, timezone

import psycopg2
import requests
from dotenv import load_dotenv
from psycopg2.extras import Json

load_dotenv()

URL = "https://api.openweathermap.org/data/2.5/weather"


def extract():
    """Call the OpenWeatherMap API for George, ZA."""
    r = requests.get(
        URL,
        params={"q": "George,ZA", "appid": os.environ["OWM_API_KEY"]},
        timeout=15,
    )
    r.raise_for_status()
    return r.json()


def transform(p):
    """Kelvin -> Celsius, pick the fields we need, run quality checks."""
    temp_c = round(p["main"]["temp"] - 273.15, 2)
    humidity = p["main"].get("humidity")
    wind_speed = p.get("wind", {}).get("speed")

    # data quality checks (the database enforces some of these too)
    assert -30 <= temp_c <= 55, f"Temp out of range: {temp_c}"
    assert humidity is None or 0 <= humidity <= 100, f"Bad humidity: {humidity}"
    assert wind_speed is None or wind_speed >= 0, f"Bad wind speed: {wind_speed}"

    return {
        "observed_at": datetime.fromtimestamp(p["dt"], tz=timezone.utc),
        "city": "George",
        "temp_c": temp_c,
        "humidity": humidity,
        "wind_speed": wind_speed,
        "description": p["weather"][0]["description"],
    }


def load(payload, row):
    """Save the raw JSON, then the clean row, in one transaction."""
    conn = psycopg2.connect(
        host=os.environ["POSTGRES_HOST"],
        port=os.environ["POSTGRES_PORT"],
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
    )
    try:
        with conn, conn.cursor() as cur:
            cur.execute(
                "INSERT INTO weather_raw (raw_json) VALUES (%s)",
                (Json(payload),),
            )
            cur.execute(
                """
                INSERT INTO weather_clean
                    (observed_at, city, temp_c, humidity, wind_speed, description)
                VALUES
                    (%(observed_at)s, %(city)s, %(temp_c)s, %(humidity)s,
                     %(wind_speed)s, %(description)s)
                ON CONFLICT (city, observed_at) DO NOTHING
                """,
                row,
            )
    finally:
        conn.close()


if __name__ == "__main__":
    payload = extract()
    row = transform(payload)
    load(payload, row)
    print("Saved!", row)
