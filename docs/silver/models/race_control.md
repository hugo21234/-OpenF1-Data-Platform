# Model: `silver.race_control`

## Purpose
Representar mensagens e eventos emitidos pelo controle de corrida, preservando o escopo em que cada evento se aplica.

## Grain
**1 linha = 1 mensagem/evento emitido pelo Race Control em um instante da sessão.**

## Source
`f1_plataform_data.bronze.race_control`

## Identity
Não há chave natural fechada ainda. Candidato inicial baseado em contexto temporal: `(session_key, date, category, message)` com campos de escopo usados para desambiguar quando necessário.

## Transformations
- `date` → `TIMESTAMP` tolerante a falhas.
- `driver_number` → `INT` quando aplicável.
- `lap_number` → `INT` quando aplicável.
- `sector` → `INT` quando aplicável.
- `scope` → string limpa.
- Preservar `category`, `flag`, `qualifying_phase` e `message` sem perda semântica.

## Domain rules
- A validade de `driver_number`, `sector` e outros campos depende do `scope` e do tipo de mensagem.
- `driver_number IS NULL` não significa automaticamente dado inválido: eventos de pista/setor podem não se referir a um piloto específico.
- Regras de qualidade devem considerar o contexto do evento, não somente nulidade de coluna.

## Quality checks
- `session_key`, `date`, `category`/`message` suficientes para contextualizar o evento.
- Quando `scope = 'Driver'`, investigar ausência de `driver_number` como possível problema de qualidade.
- Quando o evento não é de piloto, não classificar `driver_number NULL` automaticamente como inválido.

## Open decisions
- Mapear os valores reais de `scope` e estabelecer regras condicionais por domínio.
- Confirmar em quais tipos de evento `lap_number`, `sector`, `flag` e `qualifying_phase` são obrigatórios, opcionais ou não aplicáveis.
