============================================
-- GEORGE WEATHER DATA PIPELINE
-- Database table creation
-- ============================================

-- RAW LAYER
-- Stores the original API response.

CREATE TABLE IF NOT EXISTS weather_raw (
    id BIGSERIAL PRIMARY KEY,
    raw_json JSONB NOT NULL,
    inserted_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


-- CLEAN LAYER
-- Stores validated weather observations.

CREATE TABLE IF NOT EXISTS weather_clean (
    id BIGSERIAL PRIMARY KEY,
    observed_at TIMESTAMPTZ NOT NULL,
    city VARCHAR(50) NOT NULL,
    temp_c DOUBLE PRECISION NOT NULL,
    humidity INTEGER,
    wind_speed DOUBLE PRECISION,
    description VARCHAR(100),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT unique_weather_observation
        UNIQUE (city, observed_at),

    CONSTRAINT valid_humidity
        CHECK (
            humidity IS NULL
            OR humidity BETWEEN 0 AND 100
        ),

    CONSTRAINT nonnegative_wind_speed
        CHECK (
            wind_speed IS NULL
            OR wind_speed >= 0
        )
);

