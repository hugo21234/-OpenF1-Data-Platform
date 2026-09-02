# Model: `silver.car_data`

## Purpose
Representar amostras temporais de telemetria dos carros por piloto durante a sessão.

## Grain
**1 linha = 1 amostra temporal de telemetria de 1 piloto em 1 sessão.**

## Source
`f1_plataform_data.bronze.car_data`

## Identity
Candidato inicial: `(session_key, driver_number, date)`.

## Transformations
- `date` → `TIMESTAMP`.
- Tipar explicitamente `driver_number`, `drs`, `n_gear`, `rpm`, `speed`, `throttle` e `brake` conforme o contrato real da fonte.
- Preservar a granularidade temporal; não agregar na Silver sem necessidade explícita.

## Domain rules
- `speed >= 0` quando preenchido.
- `rpm >= 0` quando preenchido.
- `n_gear` deve respeitar o domínio real de marchas fornecido pela fonte.
- `throttle` deve respeitar a escala real da fonte.
- `brake` **não deve ser convertido definitivamente para booleano enquanto a semântica do campo não estiver fechada**. Se a fonte representar apenas `0/100`, booleano pode ser uma projeção válida; se houver níveis intermediários, a conversão perde informação.
- `drs` deve ser interpretado conforme o código de domínio da OpenF1; não assumir booleano sem mapeamento explícito.

## Quality checks
- `session_key`, `driver_number` e `date` presentes para amostras válidas.
- Valores físicos impossíveis devem ser observáveis, não silenciosamente corrigidos.
- Verificar duplicidade apenas para a mesma identidade temporal.

## Open decisions
- Confirmar domínio e escala reais de `brake`.
- Confirmar domínio de `drs`.
- Confirmar tipos e limites esperados de `throttle`, `rpm`, `speed` e `n_gear`.
- Decidir se `lap_number` deve permanecer no contrato Silver caso esteja disponível na Bronze e seja necessário para joins/particionamento analítico.
