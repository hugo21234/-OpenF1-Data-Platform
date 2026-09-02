# Model: `silver.pits`

## Purpose
Representar eventos de passagem/parada no pit lane por piloto e volta, preservando as durações associadas.

## Grain
**1 linha = 1 evento de pit de 1 piloto em 1 volta de 1 sessão.**

## Source
`f1_plataform_data.bronze.pits`

## Natural key
Ainda não fechada. Candidato inicial: `(session_key, driver_number, lap_number, date)`.

## Transformations
- `date` → `TIMESTAMP`.
- `driver_number` → `INT`.
- `lap_number` → `INT`.
- Preservar `pit_duration`, `stop_duration` e `lane_duration` como medidas distintas.

## Domain rules
- `lap_number > 0` para eventos válidos.
- Durações não devem ser negativas.
- `pit_duration`, `stop_duration` e `lane_duration` representam conceitos diferentes e não devem ser fundidos sem regra explícita.

## Quality checks
- `session_key`, `driver_number`, `lap_number` e `date` presentes em registros válidos.
- Durações >= 0 quando preenchidas.
- Investigar duplicidade pela combinação temporal antes de remover registros.

## Open decisions
- Confirmar a chave natural correta para múltiplos eventos de pit na mesma volta, caso a fonte permita.
- Confirmar os tipos numéricos das colunas de duração na Bronze e padronizá-los explicitamente na Silver.
