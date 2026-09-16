DROP TABLE IF EXISTS f1_plataform_data.bronze.drivers;

CREATE TABLE f1_plataform_data.bronze.drivers (
    meeting_key INT,
    session_key INT,
    driver_number BIGINT,
    broadcast_name STRING,
    full_name STRING,
    name_acronym STRING,
    team_name STRING,
    team_colour STRING,
    first_name STRING,
    last_name STRING,
    headshot_url STRING,
    country_code STRING
)
