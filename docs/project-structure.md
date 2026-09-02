# Estrutura do projeto

A organização do repositório segue uma separação por responsabilidade técnica, não apenas por camada Medallion.

```text
.
├── main.py
├── src/
│   ├── bronze/
│   │   ├── extractor/
│   │   ├── load/
│   │   ├── storage/
│   │   ├── validator/
│   │   └── verification/
│   └── clients/
│       └── openf1.py
├── sql/
│   ├── bronze/
│   └── silver/
├── notebooks/
└── docs/
```

## `src/`
Contém apenas código Python executável e reutilizável.

- `bronze/`: pipeline de ingestão da Bronze.
- `clients/`: integrações com fontes externas, como a API OpenF1.

Pastas vazias `prata/` e `ouro/` não são necessárias. Silver e Gold são camadas de dados; elas só devem ganhar pacotes Python em `src/` quando existir comportamento Python real que justifique isso.

## `sql/`
É o local canônico para artefatos SQL versionados.

- `sql/bronze/`: DDLs, criação e migração das tabelas Bronze.
- `sql/silver/`: transformações Bronze → Silver.
- `sql/gold/`: deve ser criado quando a camada Gold começar a existir.

SQL não deve ficar dentro de `src/`, porque não faz parte do pacote Python.

## `notebooks/`
Contém notebooks usados como superfície de execução no Databricks.

`silver_transformations.py` ainda duplica parte da lógica presente em `sql/silver`. Essa duplicação é transitória: antes de removê-la é necessário confirmar qual artefato o Lakeflow Job executa atualmente. O objetivo futuro é ter uma única fonte canônica para cada transformação.

## `docs/`
Contém arquitetura, contratos de modelos, decisões e fluxos do projeto.

## Regra mental

```text
src  = comportamento Python
sql  = definição e transformação de dados
notebooks = execução/interação no Databricks
docs = decisões e contratos
```
