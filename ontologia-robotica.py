import os
import re
import string
import nltk
from nltk.tokenize import sent_tokenize
from PyPDF2 import PdfReader
from collections import Counter

# Busca os artigos em pdf
diretorio_artigos = os.path.join(os.getcwd(), 'Artigos')
arquivos = os.listdir(diretorio_artigos)

artigos = [i for i in arquivos if i.lower().endswith('.pdf')]

# Cria uma pasta para armazenar os artigos crus no formato txt
pasta_txt = os.path.join(os.getcwd(), "Artigos_txt")
os.makedirs(pasta_txt, exist_ok=True)

""" 
# Usada para teste apenas
# Cria uma pasta para armazenar os artigos sem referência no formato txt
pasta_txt_sreferencias = os.path.join(os.getcwd(), "Artigos_SReferencias_txt")
os.makedirs(pasta_txt_sreferencias, exist_ok=True)
"""
# Definição de um dicionário para armazenar o texto dos artigos
texto_artigos = {}

# Leitura dos artigos em PDF
for nome_artigo in artigos:
    caminho_artigo = os.path.join(diretorio_artigos, nome_artigo)
    print(f"\nLendo artigo: {nome_artigo}")
    leitor = PdfReader(caminho_artigo)

    texto = ""
    for pagina in leitor.pages:
        texto_pagina = pagina.extract_text()
        if texto_pagina:
            texto += texto_pagina + "\n"
    
    # Armazena o texto lido do artigo no dicionário referente ao nome do artigo
    texto_artigos[nome_artigo] = texto

    nome_txt = nome_artigo.replace(".pdf", ".txt")
    caminho_txt = os.path.join(pasta_txt, nome_txt)
    
    with open(caminho_txt, "w", encoding="utf-8") as f:
        f.write(texto)

print("\n")

# Etapa de pré-processamento dos artigos
nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('stopwords')
nltk.download('wordnet')

# Definição das ferramentas de pré-processamento
lematizador = nltk.WordNetLemmatizer()
stop_words = set(nltk.corpus.stopwords.words('english'))

# Etapa para remover as referências bibliograficas
marcadores_referencia = ["REFERENCES", "R EFERENCES", "R\nEFERENCES"]

for nome_artigo, texto in texto_artigos.items():
    print(f"\nRemovendo referências em: {nome_artigo}...")
    
    # Por padrão, considera o texto inteiro
    texto_limpo = texto
    
    for marcador in marcadores_referencia:
        indice = texto.find(marcador)
        if indice != -1:
            # Corta o texto até o marcador
            texto_limpo = texto[:indice]
            print("Seção de referências encontrada e removida.")
            break
    
    # Salvar o texto sem referencia no dicionário de artigos
    texto_artigos[nome_artigo] = texto_limpo 

    # Atualiza os artigos txt para os txt sem referencias
    nome_txt = nome_artigo.replace(".pdf", ".txt")
    caminho_txt = os.path.join(pasta_txt, nome_txt)
    
    with open(caminho_txt, "w", encoding="utf-8") as f:
        f.write(texto_limpo)
    
print("\n")
# Definição de um dicionário para armazenar os artigos processados
artigos_processados = {}

for nome_artigo, texto in texto_artigos.items():
    print(f"\nProcessando artigo: {nome_artigo}")

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

print("\n")

# Etapa para encontrar os 10 termos mais recorrentes em todos os artigos

# Uni todos os tokens de artigos em um só vetor
todos_tokens = []
for tokens in artigos_processados.values():
    todos_tokens.extend(tokens)

# Cria o Bag-of-Words utilizando a função counter
bag_of_wordsAux = Counter(todos_tokens)

# Filtra o bag_of_words
bag_of_words = Counter({
    termo: freq
    for termo, freq in bag_of_wordsAux.items()
    if termo not in ["fig", "time"] and not termo.isdigit()
})

# Obter os 10 termos mais recorrentes
termos_recorrentes = bag_of_words.most_common(10)

print("\nOs 10 termos mais recorrentes nos artigos:")
for termo, frequencia in termos_recorrentes:
    print(f"{termo}: {frequencia} ocorrências")

    # Salva os termos recorrentes em arquivo txt
    with open("termos_recorrentes.txt", "w", encoding="utf-8") as f:
        for termo, freq in termos_recorrentes:
            f.write(f"{termo}: {freq}\n")


print("--- Iniciando extração de informações (Objetivo, Problema...) ---")
info_extraida = {}

# Palavras-chave por categoria
palavras_chave = {
    "objetivo": ["objective", "aim", "purpose", "goal", "the main goal"],
    "problema": ["problem", "issue", "challenge", "gap", "difficulty"],
    "metodologia": ["method", "methodology", "approach", "procedure", "framework", "survey", "analysis"],
    "contribuicao": ["contribution", "contributes", "this study adds"]
}

for nome_artigo, texto in texto_artigos.items():
    print(f"Extraindo de: {nome_artigo}")
    
    # Dicionário para guardar as informações do artigo atual
    info = {"objetivo": "", "problema": "", "metodologia": "", "contribuicao": ""}
    
    texto_lower = texto.lower() # Trabalhar com o texto em minúsculas para a busca
    
    # Itera sobre cada categoria que queremos extrair
    for categoria, chaves in palavras_chave.items():
        # Itera sobre cada palavra-chave da categoria
        for chave in chaves:
            # Procura a primeira ocorrência da palavra-chave no texto
            posicao_chave = texto_lower.find(chave)
            
            # Se a chave foi encontrada e a categoria ainda não foi preenchida
            if posicao_chave != -1 and not info[categoria]:
                # Encontra o ponto final ANTERIOR à palavra-chave
                inicio_frase = texto_lower.rfind('.', 0, posicao_chave)
                
                # Encontra o ponto final POSTERIOR à palavra-chave
                fim_frase = texto_lower.find('.', posicao_chave)

                # Se não encontrou um ponto final depois, pega até o fim do texto
                if fim_frase == -1:
                    fim_frase = len(texto_lower)

                # Extrai a frase do texto original (com a capitalização correta)
                # O +1 é para começar a capturar depois do ponto final
                frase_extraida = texto[inicio_frase + 1 : fim_frase].strip()
                
                # Armazena a frase e para de procurar outras chaves para esta categoria
                info[categoria] = frase_extraida.replace('\n', ' ').strip()
                break # Vai para a próxima categoria
    
    info_extraida[nome_artigo] = info
print("Extração de informações finalizada.\n")


# --- ETAPA 5: SALVAR RESULTADOS FINAIS ---

print("--- Salvando resultados consolidados ---")
nome_arquivo_saida = "extracoes_final.txt"
with open(nome_arquivo_saida, "w", encoding="utf-8") as f:
    # Escreve o cabeçalho do arquivo
    f.write("NomeArquivo;;Objetivo;;Problema;;Metodologia;;Contribuicao\n")
    
    for nome_arquivo, dados in info_extraida.items():
        # Usa .get() para pegar o valor ou um padrão "Não encontrado"
        objetivo = dados.get("objetivo", "Não encontrado.").replace("\n", " ").strip()
        problema = dados.get("problema", "Não encontrado.").replace("\n", " ").strip()
        metodologia = dados.get("metodologia", "Não encontrado.").replace("\n", " ").strip()
        contribuicao = dados.get("contribuicao", "Não encontrado.").replace("\n", " ").strip()
        
        # Formata a linha e adiciona aspas para garantir que o CSV funcione bem
        linha = f'"{nome_arquivo}";;"{objetivo}";;"{problema}";;"{metodologia}";;"{contribuicao}"\n'
        f.write(linha)

print(f"Script finalizado! Resultados salvos em '{nome_arquivo_saida}'.")