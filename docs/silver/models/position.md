# Model: `silver.position`

## Purpose
Representar a evolução temporal da posição de cada piloto durante a sessão.

## Grain
**1 linha = 1 observação temporal da posição de 1 piloto em 1 sessão.**

## Source
`f1_plataform_data.bronze.position`

## Identity
Não deve ser tratada como uma tabela de estado único por piloto. A identidade lógica depende do tempo da observação.

Candidato inicial: `(session_key, driver_number, date)`.

## Transformations
- `date` → `TIMESTAMP`.
- `driver_number` → `INT`.
- `position` → `INT`.

## Domain rules
- O mesmo piloto pode aparecer muitas vezes na mesma sessão porque sua posição muda ao longo da corrida.
- Portanto, **não deduplicar apenas por `(session_key, driver_number)`**.
- `position > 0` para posições válidas.

## Quality checks
- `date`, `session_key`, `driver_number` e `position` presentes em registros válidos.
- `position > 0`.
- Duplicidade só deve ser investigada para observações que coincidam na identidade temporal, não pela presença de múltiplas linhas do mesmo piloto.

## Open decisions
- Confirmar se `date` tem resolução suficiente para funcionar como parte da identidade natural de todas as observações.
