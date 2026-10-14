import os

import psycopg2
from dotenv import load_dotenv

load_dotenv()

AGGREGATE_SQL = """
INSERT INTO weather_daily_avg
    (city, observation_date, avg_temp_c, min_temp_c, max_temp_c,
     avg_humidity, avg_wind_speed, reading_count)
SELECT
    city,
    (observed_at AT TIME ZONE 'Africa/Johannesburg')::date AS observation_date,
    ROUND(AVG(temp_c)::numeric, 2),
    MIN(temp_c),
    MAX(temp_c),
    ROUND(AVG(humidity)::numeric, 1),
    ROUND(AVG(wind_speed)::numeric, 2),
    COUNT(*)
FROM weather_clean
GROUP BY city, (observed_at AT TIME ZONE 'Africa/Johannesburg')::date
ON CONFLICT (city, observation_date) DO UPDATE SET
    avg_temp_c     = EXCLUDED.avg_temp_c,
    min_temp_c     = EXCLUDED.min_temp_c,
    max_temp_c     = EXCLUDED.max_temp_c,
    avg_humidity   = EXCLUDED.avg_humidity,
    avg_wind_speed = EXCLUDED.avg_wind_speed,
    reading_count  = EXCLUDED.reading_count,
    updated_at     = NOW();
"""


def run():
    conn = psycopg2.connect(
        host=os.environ["POSTGRES_HOST"],
        port=os.environ["POSTGRES_PORT"],
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
    )
    try:
        with conn, conn.cursor() as cur:
            cur.execute(AGGREGATE_SQL)
            print(f"Daily summary updated: {cur.rowcount} day(s) written")
    finally:
        conn.close()


if __name__ == "__main__":
    run()
