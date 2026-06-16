import os
import json
import requests
import re
from dotenv import load_dotenv

load_dotenv()
NVIDIA_API_KEY = os.environ.get("NVIDIA_API_KEY")
HEADERS = {"Authorization": f"Bearer {NVIDIA_API_KEY}", "Content-Type": "application/json"}

def limpar_json(texto: str):
    match = re.search(r'\{[\s\S]*\}', texto)
    return json.loads(match.group(0)) if match else None

def extrair_dados_texto(texto: str):
    url = "https://integrate.api.nvidia.com/v1/chat/completions"
    prompt = f'Você é um assistente financeiro. Extraia os dados da mensagem. Retorne EXATAMENTE um JSON válido com chaves: "valor" (apenas números decimais usando ponto), "categoria" (ex: Mercado, Saúde, Contas, Comer Fora, Lazer, Transporte) e "descricao" (o local). Mensagem: "{texto}"'
    
    payload = {"model": "meta/llama-3.1-8b-instruct", "messages": [{"role": "user", "content": prompt}], "temperature": 0.1, "max_tokens": 150}
    try:
        res = requests.post(url, headers=HEADERS, json=payload)
        return limpar_json(res.json()["choices"][0]["message"]["content"]) if res.status_code == 200 else None
    except Exception:
        return None

def ler_recibo_imagem(base64_image: str, caption: str):
    url = "https://integrate.api.nvidia.com/v1/chat/completions"
    prompt = f"Descubra o VALOR TOTAL pago e o ESTABELECIMENTO neste recibo. Contexto: {caption}. Retorne EXATAMENTE um JSON válido com chaves: 'valor' (ex: 150.00), 'categoria', e 'descricao'. Não escreva nada além do JSON."
    
    payload = {
        "model": "meta/llama-3.2-11b-vision-instruct",
        "messages": [{"role": "user", "content": [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}]}],
        "temperature": 0.1,
        "max_tokens": 200
    }
    try:
        res = requests.post(url, headers=HEADERS, json=payload)
        return limpar_json(res.json()["choices"][0]["message"]["content"]) if res.status_code == 200 else None
    except Exception:
        return None