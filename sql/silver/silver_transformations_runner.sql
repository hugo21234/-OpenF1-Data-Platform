-- ===========================================
-- SILVER LAYER TRANSFORMATIONS
-- Executes all Silver transformations in order
-- ===========================================

CREATE SCHEMA IF NOT EXISTS f1_plataform_data.silver;

-- 1. DRIVERS
CREATE OR REPLACE TABLE f1_plataform_data.silver.drivers AS
SELECT DISTINCT
    meeting_key,
    session_key,
    TRY_CAST(driver_number AS int) AS driver_number,
    TRIM(broadcast_name) AS broadcast_name,
    INITCAP(TRIM(full_name)) AS full_name,
    UPPER(TRIM(name_acronym)) AS name_acronym,
    INITCAP(TRIM(team_name)) AS team_name,
    UPPER(TRIM(team_colour)) AS team_colour,
    INITCAP(TRIM(first_name)) AS first_name,
    INITCAP(TRIM(last_name)) AS last_name,
    TRIM(headshot_url) AS headshot_url
FROM (
    SELECT *,
        ROW_NUMBER() OVER (
            PARTITION BY full_name, team_name
            ORDER BY meeting_key DESC
        ) AS rn
    FROM f1_plataform_data.bronze.drivers
)
WHERE rn = 1;

-- 2. CAR_DATA
CREATE OR REPLACE TABLE f1_plataform_data.silver.car_data AS
SELECT
  CASE  
    WHEN brake = 0 THEN false
    WHEN brake = 100 THEN true
    ELSE NULL
  END AS brake_boolean,
  to_timestamp(date) AS date,
  driver_number,
  drs,
  meeting_key,
  session_key,
  n_gear,
  rpm,
  speed,
  throttle
FROM f1_plataform_data.bronze.car_data;

-- 3. PITS
CREATE OR REPLACE TABLE f1_plataform_data.silver.pits AS
SELECT
    to_timestamp(date) AS date,
    session_key,
    pit_duration,
    meeting_key,
    TRY_CAST(driver_number AS INT) as driver_number,
    stop_duration,
    lane_duration,
    TRY_CAST(lap_number AS INT) as lap_number
FROM f1_plataform_data.bronze.pits;

-- 4. LAPS
CREATE OR REPLACE TABLE f1_plataform_data.silver.laps AS 
SELECT
    meeting_key,
    session_key,
    driver_number,
    lap_number,
    date_start,
    duration_sector_1,
    duration_sector_2,
    duration_sector_3,
    i1_speed,
    i2_speed,
    is_pit_out_lap,
    lap_duration,
    segments_sector_1,
    segments_sector_2,
    segments_sector_3,
    st_speed
FROM f1_plataform_data.bronze.laps;

-- 5. POSITION
CREATE OR REPLACE TABLE f1_plataform_data.silver.position AS
SELECT 
  to_timestamp(date) AS date,
  session_key,
  meeting_key,
  try_cast(driver_number AS int) AS driver_number,
  try_cast(position AS int) AS position
FROM f1_plataform_data.bronze.position;

-- 6. RACE_CONTROL
CREATE OR REPLACE TABLE f1_plataform_data.silver.race_control AS
SELECT
    meeting_key,
    session_key,
    try_to_timestamp(date) AS date,
    CAST(driver_number AS INT) as driver_number,
    CAST(lap_number AS INT) as lap_number,
    category,
    flag,
    TRIM(scope) AS scope,
    CAST(sector AS INT) AS sector,
    qualifying_phase,
    message
FROM f1_plataform_data.bronze.race_control;

-- 7. STINTS
CREATE OR REPLACE TABLE f1_plataform_data.silver.stints AS 
SELECT     
    meeting_key,     
    session_key,     
    CAST(stint_number AS INT) AS stint_number,     
    CAST(driver_number AS INT) AS driver_number,     
    CAST(lap_start AS INT) AS lap_start,  
    CASE
        WHEN TRY_CAST(lap_end AS INT) >= TRY_CAST(lap_start AS INT)
        THEN TRY_CAST(lap_end AS INT)
        ELSE NULL
    END AS lap_end,
    CASE
        WHEN UPPER(TRIM(compound)) IN ('SOFT', 'MEDIUM', 'HARD', 'INTERMEDIATE', 'WET')
        THEN UPPER(TRIM(compound))
        ELSE NULL
    END AS compound,
    CASE
        WHEN CAST(tyre_age_at_start AS INT) >= 0
        THEN tyre_age_at_start
        ELSE NULL
    END  AS tyre_age_at_start 
FROM f1_plataform_data.bronze.stints;