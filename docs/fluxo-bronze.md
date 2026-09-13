# Fluxo da camada Bronze

`main.py` monta o cliente OpenF1, o Volume e o loader Databricks.

1. Busca `/sessions?year=ANO` (ano atual por padr?o; `BronzePipeline(year=2025)` permite outro ano).
2. Seleciona `session_type` Practice, Qualifying ou Race, n?o canceladas e com `date_end` anterior ao instante atual em UTC. Datas ausentes, inv?lidas ou sem fuso s?o ignoradas. O filtro por tipo tamb?m inclui sess?es Sprint quando a API as classifica nesses tipos.
3. Para cada sess?o, verifica meetings por `meeting_key`. Se necess?rio, busca `/meetings?meeting_key=X`, salva o Parquet e carrega a tabela. O mesmo meeting ? processado uma vez por execu??o.
4. Salva o objeto da session obtido no passo 1 como Parquet.
5. Processa drivers, laps, stints, pit, position e race_control, nessa ordem.
6. Processa car_data por driver da sess?o.
7. Carrega a session na tabela `f1_plataform_data.bronze.sessions`, ap?s os dados da sess?o.

## Arquivos e tabelas

- Meeting: `{path_volume_databricks}/meeting_key=X/meetings.parquet`.
- Session e demais fontes: `{path_volume_databricks}/meeting_key=X/session_key=Y/{source}.parquet`.
- Telemetria: `car_data_driver=N.parquet`, carregada na tabela `car_data`.
- `pit.parquet` ? carregado em `pits`; as outras fontes usam seu pr?prio nome de tabela.

Execute `sql/bronze/create_table_meetings.sql` e `sql/bronze/create_table_sessions.sql` no Databricks antes da primeira carga. Os DDLs tamb?m est?o no script consolidado `bronze_tables.sql`.

A exist?ncia na tabela ? verificada por meeting e, quando aplic?vel, session e driver. Se a tabela j? cont?m dados, a carga ? pulada. Se apenas o Parquet existe, ele ? reutilizado pelo COPY INTO. Drivers ? consultado uma vez por sess?o para obter a lista de pilotos, inclusive em reexecu??es.

Respostas vazias dos endpoints de dados n?o geram arquivo nem COPY INTO. Meeting vazio interrompe a execu??o para n?o carregar uma sess?o sem seu meeting. Falhas de valida??o ou de transporte s?o propagadas.

O layout anterior sem `meeting_key` n?o ? migrado. Dados j? carregados nas tabelas s?o reutilizados; arquivos antigos ainda n?o carregados precisam ser migrados separadamente ou ser?o buscados novamente. A verifica??o de exist?ncia n?o garante completude de uma carga parcial j? presente na tabela.
