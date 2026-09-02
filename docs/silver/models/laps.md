# Model: `silver.laps`

## Purpose
Representar as voltas realizadas por cada piloto com tempos e medições associadas aos setores.

## Grain
**1 linha = 1 volta de 1 piloto em 1 sessão.**

## Source
`f1_plataform_data.bronze.laps`

## Natural key
`(session_key, driver_number, lap_number)`

## Transformations
- Preservar métricas de volta e setores.
- Tipar explicitamente identificadores, número da volta, timestamp e métricas quando necessário.
- Preservar `is_pit_out_lap` como atributo da volta.

## Domain rules
- `lap_number` deve ser positivo para voltas válidas.
- Durações de volta/setor não devem ser negativas.
- Uma mesma volta lógica não deve ser removida apenas porque timestamps ou métricas diferem sem antes confirmar duplicidade real na fonte.

## Quality checks
- `session_key`, `driver_number` e `lap_number` presentes para registros válidos.
- `lap_duration >= 0` quando preenchido.
- `duration_sector_1`, `duration_sector_2`, `duration_sector_3 >= 0` quando preenchidos.
- Investigar duplicidades pela chave natural em vez de deduplicar automaticamente.

## Open decisions
- Fechar quais colunas exigem cast explícito na Silver; o SQL atual ainda replica vários tipos diretamente da Bronze.
