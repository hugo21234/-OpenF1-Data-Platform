CREATE TABLE laps (
    date_start STRING,
    driver_number BIGINT,
    duration_sector_1 DOUBLE,
    duration_sector_2 DOUBLE,
    duration_sector_3 DOUBLE,
    i1_speed BIGINT,
    i2_speed BIGINT,
    is_pit_out_lap BOOLEAN,
    lap_duration DOUBLE,
    lap_number BIGINT,
    meeting_key BIGINT,
    segments_sector_1 ARRAY<BIGINT>,
    segments_sector_2 ARRAY<BIGINT>,
    segments_sector_3 ARRAY<BIGINT>,
    session_key BIGINT,
    st_speed BIGINT
)
