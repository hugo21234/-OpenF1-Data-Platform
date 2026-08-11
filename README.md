# 🏎️ OpenF1 Data Platform

Projeto de estudo em engenharia de dados construído utilizando dados de Fórmula 1 disponibilizados pela **OpenF1 API**.

O objetivo é desenvolver uma plataforma de dados de ponta a ponta capaz de ingerir dados brutos da Fórmula 1, transformá-los em datasets analíticos e disponibilizar informações relevantes sobre corridas através de uma API.

> Este projeto está sendo desenvolvido como estudo prático de Python, Programação Orientada a Objetos, Engenharia de Dados e desenvolvimento Backend.

---

## 🎯 Objetivo do Projeto

A proposta não é simplesmente consumir uma API externa.

O objetivo é simular uma pequena plataforma de dados próxima de um cenário real de engenharia.

A arquitetura deverá evoluir para algo semelhante a:

```text
OpenF1 API
    │
    ▼
Ingestão de Dados
    │
    ▼
Camada Bronze
Dados brutos
    │
    ▼
Camada Silver
Dados tratados e modelados
    │
    ▼
Camada Gold
Métricas e análises
    │
    ▼
Banco de Dados
    │
    ▼
FastAPI
    │
    ▼
Aplicações / Consumidores
```

---

## 🏁 Domínio dos Dados

O projeto trabalhará com entidades do domínio da Fórmula 1, como:

* Pilotos
* Sessões
* Voltas
* Stints
* Pit stops
* Posições
* Eventos de controle de corrida
* Telemetria dos carros

Posteriormente, esses dados poderão ser relacionados para responder perguntas sobre desempenho, estratégia e comportamento durante uma corrida.

---

## 🧠 Objetivos de Aprendizado

O projeto foi pensado principalmente para consolidar conhecimentos em:

* Python
* Programação Orientada a Objetos
* Consumo de APIs REST
* HTTP
* Tratamento de erros
* Modelagem de dados
* ETL / ELT
* Arquitetura Medallion
* Validação de dados
* Pandas
* SQL
* PostgreSQL
* FastAPI
* Docker
* Testes
* Logging
* Design de APIs
* Deploy
* Documentação técnica

---

## 🏗️ Arquitetura Planejada

```text
                    OpenF1
                       │
                       ▼
                ┌─────────────┐
                │  Ingestão   │
                └──────┬──────┘
                       │
                       ▼
                ┌─────────────┐
                │   Bronze    │
                │ Dados Brutos│
                └──────┬──────┘
                       │
                       ▼
                ┌─────────────┐
                │   Silver    │
                │Dados Limpos │
                └──────┬──────┘
                       │
                       ▼
                ┌─────────────┐
                │    Gold     │
                │  Analytics  │
                └──────┬──────┘
                       │
                       ▼
                  PostgreSQL
                       │
                       ▼
                    FastAPI
```

A arquitetura poderá mudar durante o desenvolvimento conforme novos requisitos e problemas forem descobertos.

---

## 📁 Estrutura Planejada do Projeto

```text
openf1-data-platform/
│
├── src/
│   ├── ingestion/
│   ├── domain/
│   ├── transformations/
│   ├── repositories/
│   ├── services/
│   └── api/
│
├── data/
│   ├── bronze/
│   ├── silver/
│   └── gold/
│
├── tests/
│
├── docs/
│
├── .gitignore
├── requirements.txt
└── README.md
```

Essa estrutura é propositalmente inicial.

Ela deverá evoluir de acordo com as responsabilidades e necessidades encontradas durante a implementação.

---

## 🗺️ Roadmap

### Fase 1 — Exploração do domínio

Entender a OpenF1 API e identificar quais entidades e relacionamentos serão relevantes para o projeto.

### Fase 2 — Ingestão

Construir uma camada em Python responsável por consumir os dados da OpenF1 de maneira confiável.

### Fase 3 — Camada Bronze

Armazenar as respostas originais da API preservando os dados recebidos da fonte.

### Fase 4 — Camada Silver

Limpar, normalizar, validar e modelar os dados provenientes da camada Bronze.

### Fase 5 — Camada Gold

Criar datasets analíticos e métricas relacionadas ao desempenho na Fórmula 1.

### Fase 6 — Persistência

Persistir os dados processados relevantes em PostgreSQL.

### Fase 7 — API

Disponibilizar datasets e análises através de uma API desenvolvida com FastAPI.

### Fase 8 — Produção

Adicionar elementos necessários para aproximar o projeto de uma aplicação real:

* Testes
* Logging
* Docker
* Configuração de ambiente
* Documentação
* Deploy

---

## 📊 Possíveis Análises

Algumas análises que poderão ser exploradas durante o desenvolvimento:

* Comparação de ritmo entre pilotos
* Evolução dos tempos de volta
* Desempenho por stint
* Desgaste e desempenho dos pneus
* Impacto dos pit stops
* Mudanças de posição
* Comparação de estratégias
* Consistência dos pilotos
* Comparação de telemetria

O escopo analítico definitivo será definido conforme o projeto evoluir.

---

## 🛠️ Tecnologias

### Linguagem

* Python

### Dados

* Pandas
* SQL
* PostgreSQL

### Backend

* FastAPI

### Infraestrutura

* Docker

### Fonte dos Dados

* OpenF1 API

Novas tecnologias serão adicionadas somente quando houver uma necessidade real dentro do projeto.

---

## 🚧 Status do Projeto

**Em desenvolvimento.**

Status atual:

```text
[✓] Fonte de dados escolhida
[ ] Definir problema do produto
[ ] Explorar endpoints da OpenF1
[ ] Modelar o domínio
[ ] Construir ingestão
[ ] Implementar Bronze
[ ] Implementar Silver
[ ] Implementar Gold
[ ] PostgreSQL
[ ] FastAPI
[ ] Testes
[ ] Docker
[ ] Deploy
```

---

## 📚 Por que este projeto existe?

O objetivo deste repositório não é apenas apresentar uma aplicação pronta.

Ele também deverá registrar as decisões de engenharia tomadas durante o desenvolvimento:

* por que determinada abordagem foi escolhida;
* por que certas responsabilidades foram separadas;
* quais problemas apareceram;
* quais trade-offs foram considerados;
* quais decisões foram alteradas;
* como a arquitetura evoluiu.

Dessa forma, o repositório funciona tanto como **projeto de portfólio em Engenharia de Dados** quanto como registro do processo de aprendizado.
