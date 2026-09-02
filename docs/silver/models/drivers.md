# Model: `silver.drivers`

## Purpose
Fornecer uma representação limpa e padronizada dos pilotos participantes de cada sessão.

## Grain
**1 linha = 1 piloto em 1 sessão.**

## Source
`f1_plataform_data.bronze.drivers`

## Natural key
`(session_key, driver_number)`

## Transformations
- `driver_number` → `INT`.
- Remover espaços desnecessários de campos textuais.
- Padronizar nomes próprios com capitalização consistente.
- Padronizar `name_acronym` e `team_colour` em uppercase.
- Deduplicar por `(session_key, driver_number)` quando a origem repetir o mesmo piloto na mesma sessão.

## Domain rules
- `driver_number` identifica o piloto dentro do contexto da sessão.
- Um piloto não deve aparecer mais de uma vez por `session_key` após a deduplicação.
- Campos de nome são descritivos; não devem ser usados como chave.

## Quality checks
- Unicidade de `(session_key, driver_number)`.
- `driver_number IS NOT NULL` após cast para registros válidos.
- `name_acronym` sem espaços laterais.

## Open decisions
- Revisar se `ORDER BY meeting_key DESC` é realmente o critério correto para resolver duplicidade dentro da mesma sessão, já que `meeting_key` tende a ser constante nesse contexto.
