import streamlit as st
import streamlit_shadcn_ui as ui
from supabase import create_client
import pandas as pd
import os

# Configuração de Layout Profissional
st.set_page_config(page_title="Hermes Financeiro", layout="centered")

# Conexão (Segura)
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

st.title("📊 Hermes Dashboard")

# Busca dados
data = supabase.table("gastos").select("*").execute()
df = pd.DataFrame(data.data)

# Grid de Cards (Estilo Purity)
col1, col2 = st.columns(2)
with col1:
    ui.metric_card(title="Total Gasto", content=f"R$ {df['valor'].sum():,.2f}", description="Acumulado mensal")
with col2:
    ui.metric_card(title="Transações", content=str(len(df)), description="Registros salvos")

# Formulário de Adição
with st.expander("➕ Adicionar Gasto"):
    with st.form("novo_gasto", clear_on_submit=True):
        desc = st.text_input("Descrição")
        val = st.number_input("Valor")
        if st.form_submit_button("Salvar"):
            supabase.table("gastos").insert({"descricao": desc, "valor": val, "quem_gastou": "Usuario"}).execute()
            st.success("Salvo!")
            st.rerun()

# Tabela e Gráfico
st.subheader("Visualização")
st.bar_chart(df.groupby("categoria")["valor"].sum() if "categoria" in df.columns else df["valor"])
st.dataframe(df, use_container_width=True)