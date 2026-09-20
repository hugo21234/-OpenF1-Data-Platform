-- ===========================================
-- GOLD LAYER LOAD
-- Executes all Gold dimension and fact table loads
-- Order: Dimensions first, then Facts
-- ===========================================

CREATE SCHEMA IF NOT EXISTS f1_plataform_data.gold;

-- ===== DIMENSIONS =====

-- 1. DIM_TEAMS (must run before dim_drivers)
CREATE OR REPLACE TABLE f1_plataform_data.gold.dim_teams AS
SELECT
    uuid() AS team_id,
    team_name AS name,
    team_colour AS colour,
    current_date() AS effective_from,
    CAST(NULL AS DATE) AS effective_to,
    TRUE AS is_current
FROM (
    SELECT DISTINCT
        team_name,
        team_colour
    FROM f1_plataform_data.silver.drivers
    WHERE team_name IS NOT NULL
) teams;

-- 2. DIM_DRIVERS (depends on dim_teams)
CREATE OR REPLACE TABLE f1_plataform_data.gold.dim_drivers AS
SELECT
    uuid() AS driver_id,
    d.driver_number,
    d.broadcast_name,
    d.full_name,
    d.name_acronym,
    d.first_name,
    d.last_name,
    t.team_id,
    d.headshot_url,
    current_date() AS effective_from,
    CAST(NULL AS DATE) AS effective_to,
    TRUE AS is_current
FROM (
    SELECT DISTINCT driver_number,
        broadcast_name,
        full_name,
        name_acronym,
        first_name,
        last_name,
        team_name,
        headshot_url
    FROM f1_plataform_data.silver.drivers
) as d
JOIN f1_plataform_data.gold.dim_teams AS t
    ON d.team_name = t.name
    AND t.is_current = TRUE;

-- ===== FACTS =====

-- 3. FACT_LAPS
CREATE OR REPLACE TABLE f1_plataform_data.gold.fact_laps AS
SELECT
    uuid() as lap_id,
    d.driver_id,
    l.date_start,
    l.duration_sector_1,
    l.duration_sector_2,
    l.duration_sector_3,
    l.i1_speed,
    l.i2_speed,
    l.is_pit_out_lap,
    l.lap_number,
    l.meeting_key,
    l.session_key,
    l.st_speed
FROM f1_plataform_data.silver.laps as l
JOIN f1_plataform_data.gold.dim_drivers as d
    ON l.driver_number = d.driver_number;

-- 4. FACT_PIT
CREATE OR REPLACE TABLE f1_plataform_data.gold.fact_pit AS
SELECT 
    uuid() AS pit_id,
    p.date,
    d.driver_id,
    p.lane_duration,
    p.pit_duration,
    p.stop_duration,
    p.lap_number,
    p.meeting_key,
    p.session_key
FROM f1_plataform_data.silver.pits AS p
JOIN f1_plataform_data.gold.dim_drivers AS d
    ON p.driver_number = d.driver_number
WHERE d.is_current = true;

-- 5. FACT_POSITION
CREATE OR REPLACE TABLE f1_plataform_data.gold.fact_position AS
SELECT
    uuid() AS position_id,
    p.position,
    d.driver_id,
    p.session_key,
    p.meeting_key,
    p.date
FROM f1_plataform_data.silver.position AS p
JOIN f1_plataform_data.gold.dim_drivers AS d
    ON p.driver_number = d.driver_number;

-- 6. FACT_CAR_DATA
CREATE OR REPLACE TABLE f1_plataform_data.gold.fact_car_data AS
SELECT
    uuid() as car_data_id,
    d.driver_id,
    c.brake_boolean,
    c.date,
    c.drs,
    c.meeting_key,
    c.session_key,
    c.n_gear,
    c.rpm,
    c.speed,
    c.throttle
FROM f1_plataform_data.silver.car_data AS c
JOIN f1_plataform_data.gold.dim_drivers AS d
    ON c.driver_number = d.driver_number;

-- 7. FACT_RACE_CONTROL
CREATE OR REPLACE TABLE f1_plataform_data.gold.fact_race_control AS
SELECT
    CASE 
        WHEN r.driver_number is null
        THEN 'de5f2dd6-f38d-4963-9f93-67ada7ae37ed'
        ELSE d.driver_id
    END AS driver_id,
    r.category,
    r.date,
    r.flag,
    r.lap_number,
    r.message,
    r.qualifying_phase,
    r.scope,
    r.sector,
    r.meeting_key,
    r.session_key
FROM f1_plataform_data.silver.race_control AS r
JOIN f1_plataform_data.gold.dim_drivers AS d
    ON r.driver_number = d.driver_number;

-- 8. FACT_STINTS
CREATE OR REPLACE TABLE f1_plataform_data.gold.fact_stints AS
SELECT
    uuid() AS stint_id,
    d.driver_id,
    s.compound,
    s.lap_start,
    s.lap_end,
    s.stint_number,
    s.tyre_age_at_start,
    s.meeting_key,
    s.session_key
FROM f1_plataform_data.silver.stints AS s
JOIN f1_plataform_data.gold.dim_drivers AS d
    ON s.driver_number = d.driver_number;