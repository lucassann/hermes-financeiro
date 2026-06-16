import streamlit as st
from supabase import create_client
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

def get_config(key):
    return st.secrets[key] if key in st.secrets else os.environ.get(key)

supabase = create_client(get_config("SUPABASE_URL"), get_config("SUPABASE_KEY"))

st.set_page_config(page_title="Dashboard Financeiro", layout="wide")
st.title("💰 Controle de Gastos")

# --- ABA DE ADICIONAR GASTOS ---
with st.expander("➕ Adicionar novo gasto"):
    with st.form("form_gasto"):
        col1, col2 = st.columns(2)
        descricao = col1.text_input("Descrição")
        valor = col2.number_input("Valor (R$)", min_value=0.0, format="%.2f")
        categoria = st.selectbox("Categoria", ["Alimentação", "Transporte", "Casa", "Lazer", "Outros"])
        submit = st.form_submit_button("Salvar")
        
        if submit:
            supabase.table("gastos").insert({"descricao": descricao, "valor": valor, "categoria": categoria, "quem_gastou": "Manual"}).execute()
            st.success("Gasto salvo!")
            st.rerun()

# --- BUSCA DOS DADOS ---
response = supabase.table("gastos").select("*").execute()
df = pd.DataFrame(response.data)

if not df.empty:
    # --- GRÁFICOS ---
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Gastos por Categoria")
        fig_cat = df.groupby("categoria")["valor"].sum()
        st.bar_chart(fig_cat)
    
    # --- TABELA COM EDIÇÃO/EXCLUSÃO ---
    st.subheader("Lista de Gastos")
    # Mostra tabela
    st.dataframe(df, use_container_width=True)
    
    # Exclusão rápida pelo ID
    with st.expander("🗑️ Apagar um gasto (use o ID da tabela acima)"):
        id_apagar = st.number_input("ID do gasto para deletar", step=1)
        if st.button("Confirmar Deleção"):
            supabase.table("gastos").delete().eq("id", id_apagar).execute()
            st.rerun()
else:
    st.info("Nenhum dado cadastrado.")