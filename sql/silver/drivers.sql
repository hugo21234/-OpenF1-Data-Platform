-- Silver layer: Drivers dimension table
-- Deduplicates bronze.drivers by (session_key, driver_number), keeping most recent meeting_key

CREATE SCHEMA IF NOT EXISTS f1_plataform_data.silver;

CREATE OR REPLACE TABLE f1_plataform_data.silver.drivers AS
SELECT
    meeting_key,
    session_key,
    driver_number,
    broadcast_name,
    full_name,
    name_acronym,
    team_name,
    team_colour,
    first_name,
    last_name,
    headshot_url,
    country_code
FROM (
    SELECT *,
        ROW_NUMBER() OVER (
            PARTITION BY session_key, driver_number
            ORDER BY meeting_key DESC
        ) AS rn
    FROM f1_plataform_data.bronze.drivers
)
WHERE rn = 1;
