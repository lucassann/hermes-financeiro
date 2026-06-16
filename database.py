import os
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

supabase: Client = create_client(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_KEY"))

def inserir_gasto(quem, tipo, descricao, valor, categoria):
    try:
        dados = {"quem_gastou": quem, "tipo_entrada": tipo, "descricao": descricao, "valor": valor, "categoria": categoria}
        return supabase.table("gastos").insert(dados).execute().data
    except Exception as e:
        print(f"Erro BD (Inserir): {e}")
        return None

def buscar_resumo():
    try:
        # Puxa os últimos 10 gastos
        res = supabase.table("gastos").select("*").order("id", desc=True).limit(10).execute()
        return res.data
    except Exception as e:
        print(f"Erro BD (Resumo): {e}")
        return []

def buscar_saldo_mes():
    try:
        res = supabase.table("gastos").select("*").execute()
        hoje = datetime.now()
        mes_atual, ano_atual = hoje.month, hoje.year
        
        total = 0.0
        por_pessoa = {}
        
        for g in res.data:
            data_db = datetime.fromisoformat(g['data_registro'].replace('Z', '+00:00'))
            if data_db.month == mes_atual and data_db.year == ano_atual:
                val = float(g['valor'])
                total += val
                quem = g['quem_gastou']
                por_pessoa[quem] = por_pessoa.get(quem, 0.0) + val
                
        return total, por_pessoa
    except Exception as e:
        print(f"Erro BD (Saldo): {e}")
        return 0.0, {}

def deletar_ultimo():
    try:
        # Puxa o último gasto com precisão
        res = supabase.table("gastos").select("*").order("id", desc=True).limit(1).execute()
        if res.data:
            ultimo = res.data[0]
            # Apaga usando a ID exata
            supabase.table("gastos").delete().eq("id", ultimo['id']).execute()
            # Retorna o pacote completo para mostrar no WhatsApp
            return ultimo 
        return None
    except Exception as e:
        print(f"Erro BD (Deletar): {e}")
        return None