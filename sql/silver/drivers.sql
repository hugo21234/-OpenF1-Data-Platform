-- Silver layer: Drivers dimension table
-- Deduplicates bronze.drivers by (session_key, driver_number), keeping most recent meeting_key

CREATE SCHEMA IF NOT EXISTS f1_plataform_data.silver;

CREATE OR REPLACE TABLE f1_plataform_data.silver.drivers AS
SELECT
    meeting_key,
    session_key,
    TRY_CAST(driver_number AS int) AS driver_number,
    TRIM(broadcast_name) AS broadcast_name,  -- mantém original, só remove espaços
    INITCAP(TRIM(full_name)) AS full_name,
    UPPER(TRIM(name_acronym)) AS name_acronym,
    INITCAP(TRIM(team_name)) AS team_name,
    UPPER(TRIM(team_colour)) AS team_colour,  -- hex colors uppercase
    INITCAP(TRIM(first_name)) AS first_name,
    INITCAP(TRIM(last_name)) AS last_name,
    TRIM(headshot_url) AS headshot_url
FROM (
    SELECT *,
        ROW_NUMBER() OVER (
            PARTITION BY session_key, driver_number
            ORDER BY meeting_key DESC
        ) AS rn
    FROM f1_plataform_data.bronze.drivers
)
WHERE rn = 1;
