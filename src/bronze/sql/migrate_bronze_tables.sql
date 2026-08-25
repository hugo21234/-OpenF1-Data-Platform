-- Execute este arquivo somente quando as tabelas antigas existirem.
-- Os backups ficam no mesmo schema com o sufixo _backup.
CREATE OR REPLACE TABLE f1_plataform_data.bronze.drivers_backup AS
SELECT * FROM f1_plataform_data.bronze.drivers;
CREATE OR REPLACE TABLE f1_plataform_data.bronze.laps_backup AS
SELECT * FROM f1_plataform_data.bronze.laps;
CREATE OR REPLACE TABLE f1_plataform_data.bronze.stints_backup AS
SELECT * FROM f1_plataform_data.bronze.stints;
CREATE OR REPLACE TABLE f1_plataform_data.bronze.pits_backup AS
SELECT * FROM f1_plataform_data.bronze.pits;
CREATE OR REPLACE TABLE f1_plataform_data.bronze.position_backup AS
SELECT * FROM f1_plataform_data.bronze.position;
CREATE OR REPLACE TABLE f1_plataform_data.bronze.race_control_backup AS
SELECT * FROM f1_plataform_data.bronze.race_control;

DROP TABLE f1_plataform_data.bronze.drivers;
DROP TABLE f1_plataform_data.bronze.laps;
DROP TABLE f1_plataform_data.bronze.stints;
DROP TABLE f1_plataform_data.bronze.pits;
DROP TABLE f1_plataform_data.bronze.position;
DROP TABLE f1_plataform_data.bronze.race_control;

CREATE TABLE f1_plataform_data.bronze.drivers (
    broadcast_name STRING,
    country_code INT,
    driver_number BIGINT,
    first_name STRING,
    last_name STRING,
    headshot_url STRING,
    full_name STRING,
    meeting_key INT,
    session_key INT,
    name_acronym STRING,
    team_colour STRING,
    team_name STRING
);

CREATE TABLE f1_plataform_data.bronze.laps (
    date_start STRING,
    driver_number BIGINT,
    duration_sector_1 DOUBLE,
    duration_sector_2 DOUBLE,
    duration_sector_3 DOUBLE,
    i1_speed DOUBLE,
    i2_speed DOUBLE,
    is_pit_out_lap BOOLEAN,
    lap_duration DOUBLE,
    lap_number BIGINT,
    meeting_key INT,
    segments_sector_1 ARRAY<BIGINT>,
    segments_sector_2 ARRAY<BIGINT>,
    segments_sector_3 ARRAY<BIGINT>,
    session_key INT,
    st_speed DOUBLE
);

CREATE TABLE f1_plataform_data.bronze.stints (
    compound STRING,
    driver_number BIGINT,
    lap_end BIGINT,
    lap_start BIGINT,
    meeting_key INT,
    session_key INT,
    stint_number BIGINT,
    tyre_age_at_start BIGINT
);

CREATE TABLE f1_plataform_data.bronze.pits (
    date STRING,
    driver_number BIGINT,
    lane_duration DOUBLE,
    lap_number BIGINT,
    meeting_key INT,
    session_key INT,
    pit_duration DOUBLE,
    stop_duration DOUBLE
);

CREATE TABLE f1_plataform_data.bronze.position (
    date STRING,
    driver_number BIGINT,
    meeting_key INT,
    position BIGINT,
    session_key INT
);

CREATE TABLE f1_plataform_data.bronze.race_control (
    category STRING,
    date STRING,
    driver_number DOUBLE,
    lap_number BIGINT,
    flag STRING,
    meeting_key INT,
    message STRING,
    session_key INT,
    qualifying_phase INT,
    scope STRING,
    sector DOUBLE
);
