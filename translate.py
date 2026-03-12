import argparse
import requests
import uuid
import time  
import os
from google import genai 
from newspaper import Article


# ==========================================
# 1. CREDENCIAIS AZURE TRANSLATOR
# ==========================================
TRANSLATOR_CHAVE = os.environ.get('AZURE_KEY') or "INSIRA_SUA_CHAVE_AZURE_AQUI"
TRANSLATOR_REGIAO = "eastus" #coloque sua regiao azure
TRANSLATOR_ENDPOINT = "https://api.cognitive.microsofttranslator.com"

# ==========================================
# 2. CREDENCIAIS GOOGLE GEMINI
# ==========================================
GEMINI_CHAVE = os.environ.get('GEMINI_KEY') or "INSIRA_SUA_CHAVE_GEMINI_AQUI"
client = genai.Client(api_key=GEMINI_CHAVE) 

# ==========================================
# FUNÇÕES DO SISTEMA
# ==========================================

def extrair_artigo_da_url(url):
    print(f"Lendo o link: {url}...")
    try:
        artigo_web = Article(url)
        artigo_web.download()
        artigo_web.parse()
        return artigo_web.title, artigo_web.text
    except Exception as e:
        print(f" Erro ao tentar ler o link: {e}")
        return None, None

def traduzir_texto_azure(texto, idioma_destino='pt'):
    """Fatia o texto e usa Backoff Exponencial para vencer o erro 429."""
    url = TRANSLATOR_ENDPOINT + '/translate'
    params = {'api-version': '3.0', 'to': idioma_destino}
    headers = {
        'Ocp-Apim-Subscription-Key': TRANSLATOR_CHAVE,
        'Ocp-Apim-Subscription-Region': TRANSLATOR_REGIAO,
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
    }
    
    # Blocos ainda menores para não chamar atenção do filtro
    limite = 4000 
    pedacos = []
    texto_restante = texto

    while len(texto_restante) > limite:
        corte = texto_restante.rfind('\n', 0, limite)
        if corte == -1: corte = texto_restante.rfind(' ', 0, limite)
        if corte == -1: corte = limite
        pedacos.append(texto_restante[:corte])
        texto_restante = texto_restante[corte:]
    pedacos.append(texto_restante)

    texto_traduzido_completo = ""
    total = len(pedacos)
    print(f"Dividido em {total} partes. Usando modo de segurança (lentidão proposital).")
    
    for i, pedaco in enumerate(pedacos):
        tentativas = 0
        sucesso = False
        espera_atual = 10 # Começa esperando 10 segundos

        while tentativas < 5 and not sucesso:
            print(f"   -> Parte {i+1}/{total} (Tentativa {tentativas + 1})...")
            resposta = requests.post(url, params=params, headers=headers, json=[{'text': pedaco}])
            
            if resposta.status_code == 200:
                dados_json = resposta.json()[0]
                
                # Exibe o idioma detectado apenas na primeira parte para não poluir o terminal
                if i == 0 and 'detectedLanguage' in dados_json:
                    idioma_origem = dados_json['detectedLanguage']['language']
                    score = dados_json['detectedLanguage']['score']
                    print(f"    Idioma detectado: {idioma_origem} (Confiança: {score*100}%)")
                
                texto_traduzido_completo += dados_json['translations'][0]['text'] + " "
                sucesso = True
            elif resposta.status_code == 429:
                print(f"        Azure cansou. Esperando {espera_atual}s para recuperar...")
                time.sleep(espera_atual)
                espera_atual *= 2 # Dobra o tempo de espera (Backoff Exponencial)
                tentativas += 1
            else:
                print(f"       Erro crítico: {resposta.text}")
                return None
        
        if not sucesso:
            print(" Falha após várias tentativas. A Azure bloqueou o IP temporariamente.")
            return None

        # Pausa fixa de segurança entre partes bem-sucedidas
        if i < total - 1:
            time.sleep(5) 

    return texto_traduzido_completo

def formatar_com_ia_gratis(titulo, texto_traduzido):
    prompt = f"""
    Atue como um editor especialista em Markdown.
    
    Regras:
    1. Crie um Título Principal (H1) atrativo em português baseado no título original: '{titulo}'.
    2. Formate o texto abaixo de forma fluida, colocando conceitos chave em **negrito** e dividindo em parágrafos.
    3. Retorne APENAS o código Markdown em português, sem conversinha. NÃO adicione o texto original.

    Texto para formatar: 
    {texto_traduzido}
    """

    print("Pedindo para a IA formatar a tradução (Isso pode levar alguns segundos)...")
    try:
        resposta = client.models.generate_content(
            model='gemini-2.5-flash', 
            contents=prompt
        )
        texto_limpo = resposta.text.replace("```markdown", "").replace("```", "").strip()
        return texto_limpo
    except Exception as e:
        print(f"Erro na IA: {e}")
        return None

def salvar_arquivo(conteudo_md, nome_do_arquivo):
    if conteudo_md:
        with open(f"{nome_do_arquivo}.md", "w", encoding="utf-8") as arquivo:
            arquivo.write(conteudo_md)
        print(f" Sucesso! '{nome_do_arquivo}.md' gerado com sucesso.")

# ==========================================
# FLUXO PRINCIPAL
# ==========================================
if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description="Tradutor automático de artigos da web para Markdown.")
    parser.add_argument("-u", "--url", required=True, help="O link (URL) do artigo que você quer traduzir.")
    
    args = parser.parse_args()
    link_do_artigo = args.url
    
    print("Iniciando o processo...")
    
    titulo, artigo = extrair_artigo_da_url(link_do_artigo)
    
    if titulo and artigo:
        print(f"\nTítulo encontrado: {titulo}")
        print("1. Iniciando comunicação com a Azure...")
        texto_pt = traduzir_texto_azure(artigo, 'pt')
        
        if texto_pt:
            print("2. Formatando com IA Gratuita...")
            markdown_ia = formatar_com_ia_gratis(titulo, texto_pt)
            
            if markdown_ia:
                print("3. Montando o documento final via Python...")
                citacao_original = "> " + artigo.replace("\n", "\n> ")
                markdown_final = f"{markdown_ia}\n\n---\n\n## Texto Original\n\n{citacao_original}"
                
                print("4. Salvando...")
                nome_seguro = "".join([c if c.isalnum() else "_" for c in titulo])[:30]
                salvar_arquivo(markdown_final, f"Artigo_{nome_seguro}")
    else:
        print("Não foi possível continuar porque o texto não foi extraído do link.")
