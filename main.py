import pdfplumber
from pypdf import PdfWriter, PdfReader
import os
import pytesseract
from pdf2image import convert_from_path
# Ajustar o caminho do pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Apenas para comprimir determinado erro
import logging
logging.getLogger("pdfminer").setLevel(logging.ERROR)

from pdfs import consolidar_informes
from transformar_zip import comprimir_pdfs


# Variáveis para buscar determinadas informações
ano = ""
ANO: int = ""  


def documento(pasta_entrada, pasta_saida, ano):
    '''
    A FUNÇÃO RECEBE O DIRETÓRIO ONDE DEVERÁ BUSCAR OS ARQUIVOS, 
    O DIRETÓRIO ONDE IRÁ GUARDAR OS ARQUIVOS,
    E ALGUMAS VARIÁVEIS PARA FILTRAR SE O DOCUMENTO CORRESPONDE AO DESEJADO.

    EXISTEM TRÊS BLOCOS DIFERENTES PARA PROCESSAR, CASO NECESSÁRIO.
    '''

    contador_informe_rendimento: int = 0
    contador_segunda_pagina: int = 0
    contador_2: int = 0
    contador_3: int = 0
    pagina_total = 0
    nao_processados = []
    nao_processado_1 = []
    nao_processado_3 = []
    nao_processados_2 = []
    

    # Como existem subpastas, coloquei o walk para acessar todas as pastas e subpastas sendo .pdf
    for raiz, pastas, arquivos in os.walk(pasta_entrada):
        for arquivo in arquivos:
            if arquivo.endswith(".pdf"): 
                caminho_arquivo = os.path.join(raiz, arquivo)
                
                try:
                    reader = PdfReader(caminho_arquivo)
                except Exception as e:
                    print(f"Arquivo corrompido, pulando: {arquivo} — {e}")
                    continue

                paginas_processadas = set()

                print(f"Acessando {raiz}")
                

                # Inicia a primeira busca e salva
                with pdfplumber.open(caminho_arquivo) as pdf:
                    for i, pagina in enumerate(pdf.pages):
                        # Validação para o loop seguinte, onde, faz com que não verifique a segunda página do func
                        if i in paginas_processadas:
                            continue

                        texto = pagina.extract_text()

                        # Verifica se o pdf é imagem ou texto. Se for imagem, vai pelo ocr
                        # SEMPRE AJUSTAR O CAMINHO DO `poppler_path`
                        if not texto or texto.strip() == "":
                            try:
                                imagens = convert_from_path(caminho_arquivo,first_page=i + 1, last_page=i + 1, poppler_path=r"C:\Users\josue\Desktop\RPA Original\Release-25.12.0-0\poppler-25.12.0\Library\bin")
                                texto = pytesseract.image_to_string(imagens[0], lang="por")
                            except Exception as e:
                                print(f"Erro OCR: {e}")  
                                nao_processados.append(f"{arquivo} - página {i + 1} não processada")
                                continue

                        if not texto or texto.strip() == "":
                            nao_processados.append(f"{arquivo} - página {i + 1} sem texto")
                            continue

                        linhas: str = texto.split('\n')
                        
                        try: 
                            # Informar qual palavra-chave para verificar se a página a contém
                            if "Nome_da_busca" in texto:   
                                
                                validacao_1: str = ""

                                writer = PdfWriter()

                                for a, linha in enumerate(linhas):
                                    if "Nome_da_busca" in linha:
                                        valor = linhas[a + 1].strip()
                                        nome_da_busca = valor[:14]
                                        break

                                # Formata o nome do arquivo
                                arquivo_base_1 = f"Nome_do_arquivo{""}_{""}"
                                nome_arquivo_1 = f"{arquivo_base_1}.pdf"

                                # Guarda a página pra depois salvar
                                writer.add_page(reader.pages[i])

                                print(f"Arquivo: {arquivo}, página {i + 1}, salva!")
                                contador_informe_rendimento += 1

                                # Verificação para não dar erro na última busca, por conta do índice que começa em 0
                                if i + 1 < len(reader.pages):
                                    pagina_seguinte = pdf.pages[i + 1].extract_text()
                                    if "Pág. 2" in pagina_seguinte:
                                        linhas_pag_2: str = pagina_seguinte.split('\n')
                                        for a, linha in enumerate(linhas_pag_2):
                                            if "Informação que terá na segunda página, caso exista" in linha:
                                                validacao_1 = linha
                                            
                                        # Valida se há uma segunda página e a adiciona junto da primeira
                                        if validacao_1 in pagina_seguinte:
                                            writer.add_page(reader.pages[i + 1])    # Guarda a segunda página (i = pagina atual) + 1 a seguinte)
                                            print(f"Existe uma segunda página. Salvando página {i + 2} junto à anterior.")
                                            contador_segunda_pagina += 1

                                # Se x arquivo já existir, salvará com o mesmo nome, mas com um numeral ao lado
                                contador = 1
                                while os.path.exists(os.path.join(pasta_saida, nome_arquivo_1)):
                                    nome_arquivo_1 = f"{arquivo_base_1}_{contador}.pdf"
                                    contador += 1

                                # Efetivamente salva o arquivo no determinado diretório com o nome formatado
                                with open(os.path.join(pasta_saida, nome_arquivo_1), "wb") as f:
                                    writer.write(f)

                                # Irá indicar que a página atual e a próxima já foram processadas (porque cada pdf tem 2 páginas para a mesma pessoa)
                                paginas_processadas.add(i)
                                paginas_processadas.add(i + 1)
                            else:
                                nao_pf = f"Arquivo: `{arquivo}` não é no modelo x"
                                nao_processado_1.append(nao_pf)
                        except Exception as e:
                            print(f"Não há arquivos no modelo x. {e}")


                        # Inicia busca para uma segunda formatação
                        try:                        
                            writer = PdfWriter()
                            
                            # Este for é para colher as informações que você precisa de dentro do pdf
                            for a, linha in enumerate(linhas):
                                if "Nome_da_busca" in texto:
                                    dados_coleta = linhas[a + 1].strip()
                                    nome_filtrado = dados_coleta[:-18].strip()
                                         

                            if "Determinado_nome" in texto:          
                                arquivo_base_2 = f"Nome_do_arquivo_{""}_{""}"
                                nome_arquivo_2 = f"{arquivo_base_2}.pdf"

                                writer.add_page(reader.pages[i])
                                
                                contador = 1
                                while os.path.exists(os.path.join(pasta_saida, nome_arquivo_2)):
                                    nome_arquivo_2 = f"{arquivo_base_2}_{contador}.pdf"
                                    contador += 1

                                with open(os.path.join(pasta_saida, nome_arquivo_2), "wb") as f:
                                    writer.write(f)
                                    
                                print(f"Arquivo: {arquivo}, página {i + 1} ] salva!")
                                contador_2 += 1

                                paginas_processadas.add(i)
                            else:
                                nao_pj = f"Arquivo: `{arquivo}` não é no modelo y"
                                nao_processados_2.append(nao_pj)
                        except Exception as e:
                            print(f"Não existem as informações procuradas. {e}")


                        # Inicia uma outra busca, caso necessário
                        try:                            
                            writer = PdfWriter()                        
                            nome_empresa = []
                            dados_coleta = []
                            

                            # Este for é para colher as informações que você precisa de dentro do pdf
                            for a, linha in enumerate(linhas):
                                if "Nome_da_busca" in texto:
                                    dados_coleta = linhas[a + 1].strip()                            

                            if "informação" in texto:
                                arquivo_base_modelo = f"Nome_do_arquivo_{""}_{""}"
                                nome_arquivo_modelo = f"{arquivo_base_modelo}.pdf"

                                contador = 1
                                while os.path.exists(os.path.join(pasta_saida, nome_arquivo_modelo)):
                                    nome_arquivo_modelo = f"{arquivo_base_modelo}_{contador}.pdf"
                                    contador += 1
                                writer.add_page(reader.pages[i])

                                with open(os.path.join(pasta_saida, nome_arquivo_modelo), 'wb') as f:
                                    writer.write(f)
                                    
                                print(f"Arquivo: {arquivo}, página {i + 1}  salva!")
                                contador_3 += 1

                                paginas_processadas.add(i)
                            else:
                                nao_3 = f"Arquivo: `{arquivo}` não é no modelo Informe de Rendimentos"
                                nao_processado_3.append(nao_3)
                        except Exception as e:
                            print(f"Não há processos no determinado modelo. {e}")

                    soma_contadores = contador_informe_rendimento + contador_segunda_pagina + contador_2 + contador_3
                    pagina_total += len(pdf.pages)
                    soma_arquivos = contador_informe_rendimento + contador_2 + contador_3


    nao_identificados = set(nao_processado_1) & set(nao_processados_2) & set(nao_processado_3)
    
    if soma_contadores == pagina_total:
        print(f"Processo finalizado com sucesso.\nTotal de páginas: {pagina_total} -> Páginas processadas: {soma_contadores}. Total de {soma_arquivos} arquivos na pasta.\n -Arquivos incorretos: {nao_identificados}")
    elif soma_contadores < pagina_total:
        print(f"Processo finalizado com sucesso.\nExistem arquivos que não são do formato. Páginas totais: {pagina_total} -> Páginas processadas: {soma_contadores}. Total de {soma_arquivos} arquivos na pasta.\n -Arquivos incorretos: {nao_identificados}")
    else:
        print(f"Processo finalizado com sucesso.\nExistem arquivos que não são do formato.\nPáginas totais: {pagina_total} -> Páginas processadas: {soma_contadores}. Total de {soma_arquivos} arquivos na pasta.\n -Arquivos incorretos: {nao_identificados}")

    if nao_processados:
        print(f"\n--- NÃO PROCESSADOS: {len(nao_processados)} ---")
        for item in nao_processados:
            print(item)



# Chama a função
pasta_entrada = r""
pasta_saida = r""
try:
    documento(pasta_entrada, pasta_saida, ano)
except Exception as e:
    print(f"Algo inesperado aconteceu para separar os pdfs. {e}")

# Adicionar o caminho das pastas de origem e destino
pasta_pdfs = r""
saida_pdfs = r""
try: 
    consolidar_informes(pasta_pdfs, saida_pdfs)
except Exception as e:
    print(f"Algo inesperado aconteceu para unir os pdfs. {e}")

# Adicionar o caminho das pastas de origem e destino
pasta_zip = r""
saida_zip = r""
try: 
    comprimir_pdfs(pasta_zip, saida_zip)
except Exception as e:
    print(f"Algo inesperado aconteceu para zipar os pdfs. {e}")