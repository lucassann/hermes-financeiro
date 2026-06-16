from ai_service import extrair_dados_texto

print("🧠 Enviando mensagem para a IA analisar...")
mensagem = "Gastei 150 contos no supermercado DB ontem a noite."

resultado_ia = extrair_dados_texto(mensagem)

if resultado_ia:
    print("✅ Sucesso! A IA entendeu os dados:")
    print(resultado_ia)
else:
    print("❌ Falha na extração.")