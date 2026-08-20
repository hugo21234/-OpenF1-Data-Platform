CREATE TABLE  laps(
    date_start STRING,
    drive_number INT,
    duration_sector_1 DOUBLE,
    duration_sector_2 DOUBLE,
    duration_sector_3 DOUBLE,
    i1_speed INT,
    i2_speed INT,
    is_pit_out_lap BOOLEAN,
    lap_duration DOUBLE,
    meeting_key INT,
    session_key INT,
    segmentes_sector_1 ARRAY<INT>,
    segmentes_sector_2 ARRAY<INT>,
    segmentes_sector_3 ARRAY<INT>,
    st_speed int
)