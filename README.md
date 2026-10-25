# 🏗️ End-to-End Lakehouse Pipeline: Data Engineering Architecture PoC

> **Nota de Projeto:** O foco principal deste repositório não é o processamento de grandes volumes de dados (Big Data), mas sim a **construção de uma Arquitetura de Dados moderna, escalável e resiliente**. Embora o volume de dados atual seja de uma empresa em fase inicial (early-stage), a infraestrutura foi totalmente desenhada com padrões de engenharia sénior, suportando orquestração automatizada, CI/CD e rigorosos testes de qualidade de dados.


## 1. Visão Geral
Este projeto é uma **Prova de Conceito (PoC)** que implementa um pipeline de dados automatizado de ponta a ponta. O fluxo extrai dados de fontes heterogéneas, unifica-os numa base operacional e transforma-os utilizando processamento distribuído, culminando numa camada analítica (Lakehouse) pronta para consumo em relatórios de Business Intelligence.

## 2. Tech Stack e Ferramentas
A arquitetura foi construída separando claramente a camada operacional da camada analítica:

*   **Ingestão:** Python & Pandas (Script de ETL / Integração de APIs REST).
*   **Armazenamento Operacional (OLTP):** Neon PostgreSQL.
*   **Processamento Distribuído:** Databricks (PySpark).
*   **Armazenamento Analítico (Lakehouse):** Delta Lake (Camada Gold).
*   **Orquestração e CI/CD:** GitHub Actions & Databricks Jobs.
*   **Consumo & BI:** Power BI (via DirectQuery) & Databricks Lakeview.

## 3. Fluxo de Dados (Data Flow)

1.  **Ingestão de Dados (Fase 1 e 2):** 
    *   Um script em Python extrai dados de 3 fontes distintas: APIs (com paginação e retry), ficheiros no Azure Blob Storage/SQL e a base transacional primária (Neon PostgreSQL).
    *   Estes dados são carregados de forma unificada numa base de dados de *stage* (Neon PostgreSQL) utilizando operações de *Upsert* para garantir a idempotência diária.
2.  **Transformação e Processamento (Fase 3):** 
    *   O Databricks conecta-se ao Neon via JDBC. Utilizando PySpark, os dados são limpos, os valores nulos são tratados e os tipos de dados (Casting) são padronizados.
    *   A lógica de negócio consolida as diferentes tabelas (ex: clientes, vendas, pagamentos), removendo duplicados e criando chaves consistentes.
3.  **Data Warehouse & Consumo (Fase 4):** 
    *   O resultado final é escrito em tabelas no formato Delta (Delta Lake - Camada Gold), garantindo transações ACID e compressão otimizada (Parquet).
    *   O Power BI consome estas tabelas diretamente via motor SQL Serverless do Databricks.

## 4. Destaques de Engenharia e Resiliência
Apesar do volume reduzido de dados, este projeto valida conceitos cruciais de Engenharia de Dados:
*   **Zero-Touch Automation:** Todo o fluxo corre de madrugada sem intervenção humana.
*   **CI/CD Pipeline:** O GitHub Actions não só gere o versionamento do código como também orquestra a execução do script de ingestão.
*   **Gestão Segura de Credenciais:** Nenhuma chave está *hardcoded*. Todas as *connection strings* e API keys são geridas via GitHub Secrets.
*   **Otimização de Custos:** Os *Jobs* do Databricks utilizam *clusters* efémeros que provisionam os recursos apenas durante a execução do processo PySpark, desligando-se automaticamente.

## 5. Como Executar Localmente

Para testar o módulo de ingestão em ambiente de desenvolvimento:

```bash
# 1. Clonar o repositório
git clone [https://github.com/teu-usuario/nome-do-repositorio.git](https://github.com/teu-usuario/nome-do-repositorio.git)
cd nome-do-repositorio

# 2. Criar ambiente virtual e instalar dependências
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. Configurar Variáveis de Ambiente
# Crie um ficheiro .env na raiz (ignorado pelo git) com as seguintes chaves:
API_KEY=sua_chave
AZURE_CONN_STRING=sua_string
NEON_DB_URL=seu_url

# 4. Executar a ingestão
python etl_pipeline.py
