CREATE TABLE IF NOT EXISTS f1_plataform_data.bronze.drivers (
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

CREATE TABLE IF NOT EXISTS f1_plataform_data.bronze.laps (
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

CREATE TABLE IF NOT EXISTS f1_plataform_data.bronze.stints (
    compound STRING,
    driver_number BIGINT,
    lap_end BIGINT,
    lap_start BIGINT,
    meeting_key INT,
    session_key INT,
    stint_number BIGINT,
    tyre_age_at_start BIGINT
);

CREATE TABLE IF NOT EXISTS f1_plataform_data.bronze.pits (
    date STRING,
    driver_number BIGINT,
    lane_duration DOUBLE,
    lap_number BIGINT,
    meeting_key INT,
    session_key INT,
    pit_duration DOUBLE,
    stop_duration DOUBLE
);

CREATE TABLE IF NOT EXISTS f1_plataform_data.bronze.position (
    date STRING,
    driver_number BIGINT,
    meeting_key INT,
    position BIGINT,
    session_key INT
);

CREATE TABLE IF NOT EXISTS f1_plataform_data.bronze.race_control (
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

CREATE TABLE IF NOT EXISTS f1_plataform_data.bronze.meetings (
    circuit_key INT,
    circuit_image STRING,
    circuit_info_url STRING,
    circuit_short_name STRING,
    circuit_type STRING,
    country_code STRING,
    country_flag STRING,
    country_key INT,
    country_name STRING,
    date_end STRING,
    date_start STRING,
    gmt_offset STRING,
    is_cancelled BOOLEAN,
    location STRING,
    meeting_key INT,
    meeting_name STRING,
    meeting_official_name STRING,
    year INT
);

CREATE TABLE IF NOT EXISTS f1_plataform_data.bronze.sessions (
    circuit_key INT,
    circuit_short_name STRING,
    country_code STRING,
    country_key INT,
    country_name STRING,
    date_end STRING,
    date_start STRING,
    gmt_offset STRING,
    is_cancelled BOOLEAN,
    location STRING,
    meeting_key INT,
    session_key INT,
    session_name STRING,
    session_type STRING,
    year INT
);
