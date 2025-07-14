import os
import string
import nltk
from PyPDF2 import PdfReader


diretorio_artigos = os.path.join(os.getcwd(), 'Artigos')
arquivos = os.listdir(diretorio_artigos)

artigos = [i for i in arquivos if i.lower().endswith('.pdf')]

# Definição de um dicionário para armazenar o texto dos artigos
texto_artigos = {}

# Leitura dos artigos em PDF
for nome_artigo in artigos:
    caminho_artigo = os.path.join(diretorio_artigos, nome_artigo)
    print(f"Lendo artigo: {nome_artigo}")
    leitor = PdfReader(caminho_artigo)

    texto = ""
    for pagina in leitor.pages:
        texto_pagina = pagina.extract_text()
        if texto_pagina:
            texto += texto_pagina + "\n"
    
    # Armazena o texto lido do artigo no dicionário referente ao nome do artigo
    texto_artigos[nome_artigo] = texto

# Etapa de pré-processamento dos artigos
nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('stopwords')
nltk.download('wordnet')

# Definição das ferramentas de pré-processamento
lematizador = nltk.WordNetLemmatizer()
stop_words = set(nltk.corpus.stopwords.words('english'))

# Definição de um dicionário para armazenar os artigos processados
artigos_processados = {}

for nome_artigo, texto in texto_artigos.items():
    print(f"Processando artigo: {nome_artigo}")

    # Converte o texto para minúsculas
    texto = texto.lower()

    # Remove pontuação
    texto = texto.translate(str.maketrans('', '', string.punctuation))

    # Tonkenização do texto
    tokens = nltk.word_tokenize(texto)

    # Remoção de stop words
    tokens_sem_stopwords = [token for token in tokens if token not in stop_words]

    # Lematização dos tokens
    tokens_lematizados = [lematizador.lemmatize(token) for token in tokens_sem_stopwords]

    # Filtra tokens que tenham mais de um caractere ou numeros
    tokens_finais = [t for t in tokens_lematizados if len(t) > 1 or not t.isalpha()]

    # Armazena o texto processado no dicionário
    artigos_processados[nome_artigo] = tokens_finais

# Seleciona pasta destino de txts dos artigos processados
pasta_saida = os.path.join(os.getcwd(), "Artigos_Processados")
os.makedirs(pasta_saida, exist_ok=True)

for nome_arquivo, tokens in artigos_processados.items():
    # Cria um arquivo txt para cada artigo processado
    nome_txt = nome_arquivo.replace(".pdf", "_processado.txt")
    caminho_txt = os.path.join(pasta_saida, nome_txt)

    with open(caminho_txt, "w", encoding="utf-8") as f:
        f.write(" ".join(tokens))