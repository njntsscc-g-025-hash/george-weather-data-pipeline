-- ANALYTICS LAYER: one row per city per day
CREATE TABLE IF NOT EXISTS weather_daily_avg (
    city             VARCHAR(50) NOT NULL,
    observation_date DATE NOT NULL,
    avg_temp_c       DOUBLE PRECISION,
    min_temp_c       DOUBLE PRECISION,
    max_temp_c       DOUBLE PRECISION,
    avg_humidity     DOUBLE PRECISION,
    avg_wind_speed   DOUBLE PRECISION,
    reading_count    INTEGER NOT NULL,
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (city, observation_date)
);
