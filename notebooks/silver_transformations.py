# Databricks notebook source
# DBTITLE 1,Silver: Drivers
# MAGIC %sql
# MAGIC -- Silver transform: Drivers - deduplicate by (session_key, driver_number), keep most recent meeting_key
# MAGIC INSERT OVERWRITE TABLE f1_plataform_data.silver.drivers
# MAGIC SELECT
# MAGIC     meeting_key,
# MAGIC     session_key,
# MAGIC     TRY_CAST(driver_number AS int) AS driver_number,
# MAGIC     TRIM(broadcast_name) AS broadcast_name,
# MAGIC     INITCAP(TRIM(full_name)) AS full_name,
# MAGIC     UPPER(TRIM(name_acronym)) AS name_acronym,
# MAGIC     INITCAP(TRIM(team_name)) AS team_name,
# MAGIC     UPPER(TRIM(team_colour)) AS team_colour,
# MAGIC     INITCAP(TRIM(first_name)) AS first_name,
# MAGIC     INITCAP(TRIM(last_name)) AS last_name,
# MAGIC     TRIM(headshot_url) AS headshot_url
# MAGIC FROM (
# MAGIC     SELECT *,
# MAGIC         ROW_NUMBER() OVER (
# MAGIC             PARTITION BY session_key, driver_number
# MAGIC             ORDER BY meeting_key DESC
# MAGIC         ) AS rn
# MAGIC     FROM f1_plataform_data.bronze.drivers
# MAGIC )
# MAGIC WHERE rn = 1

# COMMAND ----------

# DBTITLE 1,Silver: Stints
# MAGIC %sql
# MAGIC -- Silver transform: Stints - cast types and trim compound
# MAGIC INSERT OVERWRITE TABLE f1_plataform_data.silver.stints
# MAGIC SELECT
# MAGIC     meeting_key,
# MAGIC     session_key,
# MAGIC     CAST(stint_number AS INT) AS stint_number,
# MAGIC     CAST(driver_number AS INT) AS driver_number,
# MAGIC     CAST(lap_start AS INT) AS lap_start,
# MAGIC     CAST(lap_end AS INT) AS lap_end,
# MAGIC     TRIM(compound) AS compound,
# MAGIC     CAST(tyre_age_at_start AS INT) AS tyre_age_at_start
# MAGIC FROM f1_plataform_data.bronze.stints

# COMMAND ----------

# DBTITLE 1,Silver: Car Data
# MAGIC %sql
# MAGIC -- Silver transform: Car data - convert brake to boolean, parse timestamp
# MAGIC INSERT OVERWRITE TABLE f1_plataform_data.silver.car_data
# MAGIC SELECT
# MAGIC     CASE
# MAGIC         WHEN brake = 0 THEN false
# MAGIC         WHEN brake = 100 THEN true
# MAGIC         ELSE NULL
# MAGIC     END AS brake_boolean,
# MAGIC     to_timestamp(date) AS date,
# MAGIC     driver_number,
# MAGIC     drs,
# MAGIC     meeting_key,
# MAGIC     session_key,
# MAGIC     n_gear,
# MAGIC     rpm,
# MAGIC     speed,
# MAGIC     throttle
# MAGIC FROM f1_plataform_data.bronze.car_data

# COMMAND ----------

# DBTITLE 1,Silver: Laps
# MAGIC %sql
# MAGIC -- Silver transform: Laps - pass through with type preservation
# MAGIC INSERT OVERWRITE TABLE f1_plataform_data.silver.laps
# MAGIC SELECT
# MAGIC     meeting_key,
# MAGIC     session_key,
# MAGIC     driver_number,
# MAGIC     lap_number,
# MAGIC     date_start,
# MAGIC     duration_sector_1,
# MAGIC     duration_sector_2,
# MAGIC     duration_sector_3,
# MAGIC     i1_speed,
# MAGIC     i2_speed,
# MAGIC     is_pit_out_lap,
# MAGIC     lap_duration,
# MAGIC     segments_sector_1,
# MAGIC     segments_sector_2,
# MAGIC     segments_sector_3,
# MAGIC     st_speed
# MAGIC FROM f1_plataform_data.bronze.laps

# COMMAND ----------

# DBTITLE 1,Silver: Pits
# MAGIC %sql
# MAGIC -- Silver transform: Pits - parse timestamp, cast driver and lap numbers
# MAGIC INSERT OVERWRITE TABLE f1_plataform_data.silver.pits
# MAGIC SELECT
# MAGIC     to_timestamp(date) AS date,
# MAGIC     session_key,
# MAGIC     pit_duration,
# MAGIC     meeting_key,
# MAGIC     TRY_CAST(driver_number AS INT) AS driver_number,
# MAGIC     stop_duration,
# MAGIC     lane_duration,
# MAGIC     TRY_CAST(lap_number AS INT) AS lap_number
# MAGIC FROM f1_plataform_data.bronze.pits

# COMMAND ----------

# DBTITLE 1,Silver: Position
# MAGIC %sql
# MAGIC -- Silver transform: Position - parse timestamp, cast driver_number and position to int
# MAGIC INSERT OVERWRITE TABLE f1_plataform_data.silver.position
# MAGIC SELECT
# MAGIC     to_timestamp(date) AS date,
# MAGIC     session_key,
# MAGIC     meeting_key,
# MAGIC     try_cast(driver_number AS int) AS driver_number,
# MAGIC     try_cast(position AS int) AS position
# MAGIC FROM f1_plataform_data.bronze.position

# COMMAND ----------

# DBTITLE 1,Silver: Race Control
# MAGIC %sql
# MAGIC -- Silver transform: Race control - parse timestamp, cast types, trim scope
# MAGIC INSERT OVERWRITE TABLE f1_plataform_data.silver.race_control
# MAGIC SELECT
# MAGIC     meeting_key,
# MAGIC     session_key,
# MAGIC     try_to_timestamp(date) AS date,
# MAGIC     CAST(driver_number AS INT) AS driver_number,
# MAGIC     CAST(lap_number AS INT) AS lap_number,
# MAGIC     category,
# MAGIC     flag,
# MAGIC     TRIM(scope) AS scope,
# MAGIC     CAST(sector AS INT) AS sector,
# MAGIC     qualifying_phase,
# MAGIC     message
# MAGIC FROM f1_plataform_data.bronze.race_control