# Model: `silver.stints`

## Purpose
Representar os períodos contínuos em que um piloto utiliza um conjunto de pneus durante uma sessão.

## Grain
**1 linha = 1 stint de 1 piloto em 1 sessão.**

## Source
`f1_plataform_data.bronze.stints`

## Natural key
`(session_key, driver_number, stint_number)`

## Transformations
- `stint_number` → `INT`.
- `driver_number` → `INT`.
- `lap_start` → `INT`.
- `lap_end` → `INT`.
- `tyre_age_at_start` → `INT`.
- `compound` → string limpa e padronizada.

## Domain rules
- `stint_number > 0`.
- `lap_start > 0`.
- `lap_end >= lap_start` quando `lap_end` estiver preenchido.
- `tyre_age_at_start >= 0`.
- `compound` pertence ao domínio de compostos fornecido pela fonte; valores desconhecidos devem ser observáveis, não silenciosamente convertidos para um composto existente.

## Quality checks
- Unicidade de `(session_key, driver_number, stint_number)`.
- Nenhum `lap_end < lap_start`.
- Nenhum `tyre_age_at_start < 0`.
- Identificadores numéricos devem ser convertíveis para `INT` em registros válidos.

## Open decisions
- Definir política para stint ainda aberto/sem `lap_end`: preservar `NULL` ou aplicar outra representação explícita.
