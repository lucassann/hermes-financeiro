import streamlit as st
from supabase import create_client
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

# Conexão (Variáveis de ambiente)
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

st.set_page_config(page_title="Finanças do Casal", layout="centered")
st.title("📊 Finanças do Casal")

# Busca os dados
response = supabase.table("gastos").select("*").execute()
df = pd.DataFrame(response.data)

# Métricas rápidas
col1, col2 = st.columns(2)
col1.metric("Total Gasto", f"R$ {df['valor'].sum():.2f}")

# Gráfico e Tabela
st.subheader("Últimos Gastos")
st.dataframe(df.sort_values(by="data_registro", ascending=False))