import os
import requests
import base64
from dotenv import load_dotenv

load_dotenv()

ID_INSTANCIA = os.environ.get("ID_INSTANCIA")
TOKEN_API = os.environ.get("TOKEN_API")

def enviar_mensagem(chat_id: str, texto: str):
    url = f"https://api.green-api.com/waInstance{ID_INSTANCIA}/sendMessage/{TOKEN_API}"
    try:
        requests.post(url, json={"chatId": chat_id, "message": texto}, headers={"Content-Type": "application/json"})
    except Exception as e:
        print(f"Erro Whatsapp Envio: {e}")

def baixar_midia_base64(file_name_url: str):
    try:
        url = file_name_url if file_name_url.startswith("http") else f"https://api.green-api.com/waInstance{ID_INSTANCIA}/downloadFile/{TOKEN_API}?fileName={requests.utils.quote(file_name_url)}"
        res = requests.get(url)
        if res.status_code == 200:
            return base64.b64encode(res.content).decode('utf-8')
        return None
    except Exception as e:
        print(f"Erro Download Mídia: {e}")
        return None

def enviar_menu_texto(chat_id: str):
    """
    Versão de texto simples do menu para garantir que a mensagem chegue
    mesmo que o WhatsApp bloqueie os botões interativos.
    """
    texto = (
        "⚙️ *PAINEL DE CONTROLE - HERMES*\n\n"
        "Toque ou digite uma opção abaixo:\n"
        "📊 *resumo* - Ver últimos gastos\n"
        "💰 *saldo* - Ver saldo do mês\n"
        "🗑️ *desfazer* - Apagar último gasto"
    )
    enviar_mensagem(chat_id, texto)

def enviar_menu_botoes(chat_id: str):
    """
    Envia um painel interativo. Se o WhatsApp bloquear, use o menu de texto.
    """
    url = f"https://api.green-api.com/waInstance{ID_INSTANCIA}/sendButtons/{TOKEN_API}"
    payload = {
        "chatId": chat_id,
        "message": "⚙️ *PAINEL DE CONTROLE - HERMES*\n\nO que você deseja acessar agora?",
        "footer": "Toque em um botão abaixo:",
        "buttons": [
            {"buttonId": "cmd_resumo", "buttonText": {"displayText": "📊 Resumo"}},
            {"buttonId": "cmd_saldo", "buttonText": {"displayText": "💰 Saldo"}},
            {"buttonId": "cmd_desfazer", "buttonText": {"displayText": "🗑️ Desfazer"}}
        ]
    }
    
    try:
        # Tenta enviar botões
        res = requests.post(url, json=payload, headers={"Content-Type": "application/json"})
        # Se a API retornar erro (geralmente 400), cai no except
        res.raise_for_status()
        print(f"🔘 Menu de botões enviado para {chat_id}")
    except Exception as e:
        print(f"🚨 Erro ao enviar botões, caindo para texto simples: {e}")
        enviar_menu_texto(chat_id)