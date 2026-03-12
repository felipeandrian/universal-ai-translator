
#  Universal AI Translator & Formatter

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/SEU_USUARIO/universal-ai-translator/blob/main/notebook/Tradutor_Universal.ipynb)

Um tradutor de artigos web  que combina o poder da **Azure Translator** com a inteligência estética do **Google Gemini 2.5 Flash**.

O grande diferencial deste projeto é a capacidade de **detectar idiomas automaticamente** e processar **artigos grandes** (como Wikipedia) sem interrupções, graças a um sistema inteligente de *Backoff Exponencial* e fatiamento de texto (chunking) e usando as api's free da Azure e Gemini.

---

##  Funcionalidades

| Recurso | Descrição |
| :--- | :--- |
| ** Extração Inteligente** | Utiliza `newspaper3k` para isolar o conteúdo real, removendo anúncios e menus. |
| ** Auto-Detect** | Identifica automaticamente o idioma original (Chinês, Russo, Japonês, etc.). |
| **️ Resiliência (Erro 429)** | Algoritmo que pausa e retoma a tradução automaticamente caso atinja limites de API. |
| ** Estética IA** | O Gemini atua como editor, aplicando negrito e estruturando o Markdown. |
| ** Dual Language** | Gera um documento com a tradução fluida e mantém o original como citação. |

---

## ⚙ Como funciona "por baixo do capô"

O fluxo de processamento foi desenhado para ser à prova de falhas:

1. **Scraping:** O `newspaper3k` limpa o HTML e extrai o texto bruto.
2. **Chunking:** O texto é fatiado em blocos de 4.000 caracteres para respeitar os limites da Microsoft.
3. **Translation:** Os blocos são enviados à Azure. Se o servidor pedir calma (Erro 429), o script dobra o tempo de espera.
4. **Formatting:** A tradução bruta é refinada pelo Gemini 2.0 para ganhar estrutura visual.
5. **Assembly:** O sistema gera o arquivo `.md` final pronto para publicação.



---

##  Execução via Google Colab (Recomendado)

A forma mais rápida de usar, sem precisar instalar nada no seu computador.

1. Clique no botão **Open in Colab** no topo deste README.
2. No menu lateral esquerdo, clique na **Chave (Secrets 🔑)** e adicione suas credenciais:
   - `AZURE_KEY`: Sua chave do tradutor Azure.
   - `GEMINI_KEY`: Sua chave do Google AI Studio.
3. Execute a célula de instalação e a célula de injeção de chaves.
4. Informe a URL desejada no comando final:
   ```bash
   !python translate.py -u "URL_DO_ARTIGO"
   ```


##  Uso Local

### Pré-requisitos

* Python 3.10+
* Chave Azure Translator (Nível F0 - Gratuito)
* Chave Google AI Studio (Gemini)

### Instalação

1. **Clone o repositório:**
```bash
git clone [https://github.com/felipeandrian/universal-ai-translator.git](https://github.com/felipeandrian/universal-ai-translator.git)
cd universal-ai-translator

```


2. **Instale as dependências:**
```bash
pip install -r requirements.txt

```


3. **Configuração de Segurança:**
O script busca as chaves em variáveis de ambiente. Defina-as no seu sistema ou edite o `translate.py`:
```python
# No translate.py
TRANSLATOR_CHAVE = os.environ.get('AZURE_KEY') or "SUA_CHAVE_AQUI"
GEMINI_CHAVE = os.environ.get('GEMINI_KEY') or "SUA_CHAVE_AQUI"

```


4. **Execute:**
```bash
python translate.py -u "[https://link-do-artigo.com](https://link-do-artigo.com)"

```

---

## 📄 Licença

Distribuído sob a licença MIT. Veja `LICENSE` para mais informações.

