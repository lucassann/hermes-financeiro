import streamlit as st
import pandas as pd
from supabase import create_client

# Configuração Pessoal do Casal
st.set_page_config(page_title="Finanças do Lar", layout="wide")

# CSS para um visual "Clean & Soft"
st.markdown("""
    <style>
    .stApp { background-color: #F8FAFC; }
    .css-1r6slp0 { background: #FFFFFF; border-radius: 16px; padding: 25px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }
    h1 { color: #1E293B; font-weight: 700; }
    div.stButton > button { border-radius: 10px; background-color: #3B82F6; color: white; width: 100%; }
    </style>
""", unsafe_allow_html=True)

# Conexão
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

st.title("🏠 Nossas Finanças")
st.markdown("Bem-vindos ao nosso painel de controle.")

# Busca e Processamento
data = supabase.table("gastos").select("*").execute()
df = pd.DataFrame(data.data)

# Resumo em Cards (Design moderno)
col1, col2, col3 = st.columns(3)
col1.metric("Total Gasto", f"R$ {df['valor'].sum():,.2f}")
col2.metric("Nº de Compras", len(df))
col3.metric("Ticket Médio", f"R$ {df['valor'].mean():,.2f}")

# Layout em duas colunas (Dashboard)
left, right = st.columns([1, 2])

with left:
    st.subheader("Registrar Gasto")
    with st.form("gasto_form"):
        desc = st.text_input("O que foi?")
        val = st.number_input("Valor (R$)", min_value=0.0)
        st.form_submit_button("Lançar Gasto")

with right:
    st.subheader("Distribuição")
    # Gráfico de barras simples e elegante
    st.bar_chart(df.groupby("categoria")["valor"].sum() if "categoria" in df.columns else df["valor"])

# Tabela Limpa
st.subheader("Últimos Lançamentos")
st.table(df.tail(8))