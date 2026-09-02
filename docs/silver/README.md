# Silver Model Design

Esta pasta documenta o contrato lógico dos modelos da camada Silver antes da implementação/alteração de SQL.

## Regra de uso

Antes de mudar um modelo Silver, confirme nesta ordem:

1. **Purpose** — por que o modelo existe.
2. **Grain** — o que uma linha representa.
3. **Source** — de onde os dados vêm.
4. **Natural key / identity** — quais campos identificam logicamente um registro, quando aplicável.
5. **Transformations** — limpeza e padronização permitidas.
6. **Domain rules** — regras semânticas do dado.
7. **Quality checks** — invariantes que precisam ser testados.
8. **Open decisions** — pontos ainda não fechados; não devem virar regra definitiva por acidente.

## Model list

| Model | Grain | Source | Status |
| --- | --- | --- | --- |
| `drivers` | 1 piloto em 1 sessão | `bronze.drivers` | definido |
| `laps` | 1 volta de 1 piloto em 1 sessão | `bronze.laps` | definido |
| `stints` | 1 stint de 1 piloto em 1 sessão | `bronze.stints` | definido |
| `pits` | 1 passagem/parada de pit de 1 piloto em 1 volta | `bronze.pits` | definido |
| `position` | 1 observação temporal da posição de 1 piloto | `bronze.position` | definido |
| `race_control` | 1 mensagem/evento emitido pelo controle de corrida | `bronze.race_control` | parcial |
| `car_data` | 1 amostra temporal de telemetria de 1 piloto | `bronze.car_data` | parcial |

## Organização do código

- `sql/silver/` contém a implementação executável.
- `docs/silver/models/` contém o contrato lógico dos modelos.
- Notebook Databricks e SQL não são o contrato: o contrato é a decisão de modelagem; o SQL deve implementá-la.

## Pendências estruturais

- Padronizar gradualmente os artefatos de `sql/silver/`, que hoje misturam `.sql` e `.dbquery.ipynb`.
- Fechar a semântica de `car_data.brake` antes de tratá-lo como booleano definitivo.
- Fechar a política de campos condicionais/nulos em `race_control` por `scope`.
