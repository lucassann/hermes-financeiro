import os
from fastapi import FastAPI, Request
from dotenv import load_dotenv
from ai_service import extrair_dados_texto, ler_recibo_imagem
from database import inserir_gasto, buscar_resumo, buscar_saldo_mes, deletar_ultimo
from whatsapp import enviar_mensagem, baixar_midia_base64, enviar_menu_botoes

load_dotenv()
ID_GRUPO_PERMITIDO = os.environ.get("ID_GRUPO_PERMITIDO", "")

app = FastAPI()

@app.post("/webhook")
async def receber_webhook(request: Request):
    try:
        dados = await request.json()
        
        # Só processamos mensagens que CHEGAM (Incoming)
        if dados.get("typeWebhook") != "incomingMessageReceived":
            return {"status": "ok"}
            
        chat_id = dados.get("senderData", {}).get("chatId")
        sender_id = dados.get("senderData", {}).get("sender", "")
        
        # 1. SEGURANÇA: Bloqueia outros grupos
        if ID_GRUPO_PERMITIDO and chat_id != ID_GRUPO_PERMITIDO:
            return {"status": "ok"}
            
        # 2. SEGURANÇA: Bloqueia mensagens enviadas pelo próprio bot (previne loop)
        # Se o sender_id contiver o wid da instância, é o bot falando
        wid = dados.get("instanceData", {}).get("wid", "")
        if wid and wid in sender_id:
            return {"status": "ok"}
            
        quem = dados.get("senderData", {}).get("senderName", "Desconhecido")
        msg_data = dados.get("messageData", {})
        tipo_msg = msg_data.get("typeMessage")
        
        # TRATAMENTO DE TEXTOS E BOTÕES
        texto = ""
        if tipo_msg in ["textMessage", "extendedTextMessage"]:
            texto = msg_data.get("textMessageData", {}).get("textMessage", "") if tipo_msg == "textMessage" else msg_data.get("extendedTextMessageData", {}).get("text", "")
        elif tipo_msg == "buttonsResponseMessage":
            texto = msg_data.get("buttonsResponseMessage", {}).get("displayText", "")

        if texto:
            text_lower = str(texto).lower()
            if "menu" in text_lower or "painel" in text_lower:
                enviar_menu_botoes(chat_id)
            elif "resumo" in text_lower or "relatorio" in text_lower:
                gastos = buscar_resumo()
                msg = "*📊 ÚLTIMOS 10 GASTOS*\n\n" + ("\n".join([f"• {g['data_registro'].split('T')[0]} {g['quem_gastou']}: R$ {g['valor']} ({g['descricao']})" for g in gastos]) if gastos else "📝 Nenhum registro.")
                enviar_mensagem(chat_id, msg)
            elif "saldo" in text_lower:
                total, por_pessoa = buscar_saldo_mes()
                msg = f"*💰 RESUMO DO MÊS*\nTotal: R$ {total:.2f}\n\n" + "\n".join([f"• {p}: R$ {v:.2f}" for p, v in por_pessoa.items()])
                enviar_mensagem(chat_id, msg)
            elif "desfazer" in text_lower:
                apagado = deletar_ultimo()
                enviar_mensagem(chat_id, f"🗑️ *Removido!*\n❌ {apagado['descricao']}\n💵 R$ {apagado['valor']}" if apagado else "❌ Nada para apagar.")
            elif "ajuda" in text_lower:
                enviar_mensagem(chat_id, "🤖 *HERMES*\n💵 *Gastar:* Envie texto ou foto.\n⚙️ *Menu:* Digite 'menu'.")
            else:
                enviar_mensagem(chat_id, "🧠 _Anotando..._")
                dados_ia = extrair_dados_texto(texto)
                if dados_ia and "valor" in dados_ia:
                    inserir_gasto(quem, "Texto", dados_ia.get("descricao", ""), dados_ia.get("valor", 0), dados_ia.get("categoria", ""))
                    enviar_mensagem(chat_id, f"✅ *Anotado!*\n💰 R$ {dados_ia['valor']}\n📂 {dados_ia['categoria']}\n📝 {dados_ia['descricao']}")
                else:
                    enviar_mensagem(chat_id, "❌ Não entendi o valor. Tente: 'Gastei 50 no posto'.")

        # TRATAMENTO DE IMAGENS
        elif tipo_msg == "imageMessage":
            enviar_mensagem(chat_id, "📸 _Lendo notinha..._")
            img_data = msg_data.get("imageMessageData", {})
            base64_img = baixar_midia_base64(img_data.get("fileName") or img_data.get("downloadUrl"))
            if base64_img:
                dados_ia = ler_recibo_imagem(base64_img, img_data.get("caption", ""))
                if dados_ia and "valor" in dados_ia:
                    inserir_gasto(quem, "Foto", dados_ia.get("descricao", "Recibo"), dados_ia.get("valor", 0), dados_ia.get("categoria", "Outros"))
                    enviar_mensagem(chat_id, f"✅ *Recibo Lido!*\n💰 R$ {dados_ia['valor']}\n📂 {dados_ia['categoria']}\n📝 {dados_ia['descricao']}")
                else:
                    enviar_mensagem(chat_id, "❌ IA não identificou o valor.")

        return {"status": "ok"}
    except Exception as e:
        print(f"🚨 ERRO: {e}")
        return {"status": "ok"}