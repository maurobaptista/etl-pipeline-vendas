import os
import numpy as np
import pandas as pd
import requests
import urllib.parse
import io
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv
load_dotenv(override=True) # O override=True força o Python a usar as credenciais novas
from sqlalchemy import create_engine

# URL pública do  JSON no GitHub 
url_api ="https://raw.githubusercontent.com/maurobaptista/avaliacoes_produtos.json/refs/heads/main/avaliacoes_produtos.json"

# 1. Carregar as variáveis do cofre oculto (.env)
load_dotenv()

# 2. Resgatar as credenciais
db_user = os.getenv('DB_USER')
db_pass = os.getenv('DB_PASS')
db_host = os.getenv('DB_HOST')
db_port = os.getenv('DB_PORT')
db_name = os.getenv('DB_NAME')

# 3. O Segredo Profissional: Codificar a senha para lidar com o '@' ou '#'
senha_codificada = urllib.parse.quote_plus(db_pass)

# 4. Criar a string de conexão (agora com a senha protegida e SSL para a nuvem)
string_conexao = f"postgresql+psycopg2://{db_user}:{senha_codificada}@{db_host}:{db_port}/{db_name}?sslmode=require"
# 5. Iniciar o motor (engine) e testar a conexão
print("A iniciar o pipeline ELT...")

try:
    engine = create_engine(string_conexao)
    with engine.connect() as conexao_teste:
        print("✅ Conexão ao PostgreSQL estabelecida com sucesso!")
except Exception as erro:
    print(f"❌ Erro ao ligar ao banco de dados.\nDetalhe: {erro}")

# ==========================================

# 1. Simular a chamada de API (Extração via HTTP)
resposta = requests.get(url_api)

if resposta.status_code == 200:
    dados_json = resposta.json()

    # 2. Desaninhar a estrutura (flatten) com json_normalize
    df_avaliacoes = pd.json_normalize(dados_json)

    print("✅ Dados JSON extraídos com sucesso da web!")
    print(df_avaliacoes.head())
else:
    print(f"❌ Falha ao consumir API. Código de status: {resposta.status_code}")


# Criar uma cópia de trabalho para não alterar os dados brutos
df_limpo = df_avaliacoes.copy()

# 1. Tratamento de Tipos e Datas
# Método seguro para renomear colunas sem conflito de caracteres especiais
df_limpo = df_limpo.rename(columns=lambda x: x.replace('detalhes_avaliacao.', ''))

# Print de diagnóstico (revela os nomes reais das colunas antes da conversão)
print("🔍 Nomes das colunas após limpeza:", df_limpo.columns.tolist())

# Conversões
df_limpo['data_avaliacao'] = pd.to_datetime(df_limpo['data_avaliacao'])
df_limpo['id_pedido_fk'] = df_limpo['id_pedido_fk'].astype(int)
df_limpo['nota_estrelas'] = df_limpo['nota_estrelas'].astype(int)
df_limpo['compra_verificada'] = df_limpo['compra_verificada'].astype(bool)

# 2. Tratamento de Textos e Nulos
df_limpo['comentario_texto'] = df_limpo['comentario_texto'].str.strip()
df_limpo['tem_comentario'] = df_limpo['comentario_texto'].notna()
df_limpo['comentario_tratado'] = df_limpo['comentario_texto'].fillna('Sem comentário')

# 3. Engenharia de Atributos (NPS / Categoria de Satisfação)
condicoes = [
    df_limpo['nota_estrelas'] <= 2,
    df_limpo['nota_estrelas'] == 3,
    df_limpo['nota_estrelas'] >= 4
]
categorias = ['Detrator', 'Neutro', 'Promotor']
df_limpo['classe_nps'] = np.select(condicoes, categorias, default='Indefinido')

# 4. Extração de Componentes de Data
df_limpo['ano_mes'] = df_limpo['data_avaliacao'].dt.to_period('M').astype(str)

# 5. Visualizar o resultado final
df_limpo[['id_pedido_fk', 'nota_estrelas', 'classe_nps', 'tem_comentario', 'ano_mes', 'comentario_tratado']]

# ==========================================

import io
import os
import pandas as pd
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv

# 1. Forçar a leitura do .env atualizado do disco
load_dotenv(override=True)

connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
nome_contentor = "bronze"
nome_ficheiro = "vendas.csv"

# Verificação de segurança antes de conectar
print("Início da string em uso:", str(connection_string)[:45])

# 2. Conectar ao serviço da Azure
blob_service_client = BlobServiceClient.from_connection_string(connection_string)
container_client = blob_service_client.get_container_client(nome_contentor)
blob_client = container_client.get_blob_client(nome_ficheiro)

print(f"A descarregar {nome_ficheiro} da camada Bronze na Azure...")

# 3. Leitura direta para a memória RAM
stream_bytes = blob_client.download_blob().readall()
df_vendas = pd.read_csv(io.BytesIO(stream_bytes))

print("✅ Ficheiro extraído com sucesso da Azure!")
df_vendas.head()

# Cruzamento relacional mantendo todas as vendas
df_silver = pd.merge(
    df_vendas,
    df_limpo,
    how='left',
    left_on='id_pedido',
    right_on='id_pedido_fk'
)

# Selecionar e ordenar as colunas da camada Silver
colunas_finais = [
    'id_pedido',
    'cliente',
    'pais',
    'valor_total',
    'status_entrega',
    'data_pedido',
    'nota_estrelas',
    'classe_nps',
    'tem_comentario',
    'comentario_tratado'
]

df_silver = df_silver[colunas_finais]
df_silver

# Envio para o PostgreSQL (substitui a tabela se já existir)
df_silver.to_sql(
    name='silver_vendas_avaliacoes',
    con=engine,
    if_exists='replace',
    index=False
)

print("🚀 Camada Silver carregada com sucesso no PostgreSQL!")

# ==========================================
# CAMADA GOLD - CRUZAMENTO FINAL NO PYTHON
# ==========================================
print("A extrair dados transacionais para a Camada Gold...")

# 1. Ler as tabelas transacionais do PostgreSQL para DataFrames Pandas
df_pedidos = pd.read_sql("SELECT * FROM pedidos", engine)
df_clientes = pd.read_sql("SELECT * FROM clientes", engine)
df_departamentos = pd.read_sql("SELECT * FROM departamentos", engine)

# 2. Construir a Tabela Gold (Desnormalizada)
# Cruzar Pedidos com Clientes
df_gold = pd.merge(df_pedidos, df_clientes, on='id_cliente', how='left')

# Cruzar o resultado com Departamentos
df_gold = pd.merge(df_gold, df_departamentos, on='id_dep', how='left')

# Cruzar finalmente com a nossa tabela Silver (que já tem dados do Azure e da API)
# Atenção às chaves: as tabelas cruzam através do 'id_pedido'
df_gold = pd.merge(df_gold, df_silver, on='id_pedido', how='left')

# 3. Limpeza Final (Remover colunas duplicadas ou desnecessárias geradas no join)
colunas_para_remover = ['id_cliente', 'id_dep']
df_gold = df_gold.drop(columns=colunas_para_remover)

# 4. Enviar a Camada Gold final para o PostgreSQL
df_gold.to_sql(
    name='gold_vendas_consolidadas',
    con=engine,
    if_exists='replace',
    index=False
)

print("🏆 Camada Gold construída e carregada com sucesso no PostgreSQL!")