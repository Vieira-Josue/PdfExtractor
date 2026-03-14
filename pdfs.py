import pikepdf
import os
import re

def consolidar_informes(pasta, saida):
    '''
    Itera cada arquivo .pdf e, tendo o mesmo CPF, ele irá juntar todos em um único arquivo .pdf.
    Informar a pasta origem (onde contém os pdfs) e a pasta saída (onde ficarão salvos).
    '''

    arquivos = sorted([f for f in os.listdir(pasta) if f.endswith(".pdf")])
    processados = set()

    for arquivo_atual in arquivos:
        if arquivo_atual in processados:
            continue

        pdf_final = pikepdf.Pdf.new()
        identificador = None
        tipo = None

        if "Nome_do_arquivo" in arquivo_atual:
            # A busca está setada para um cpf. Inserir o que for necessário
            cpf = re.search(r"(\d{3}\.\d{3}\.\d{3}-\d{2})", arquivo_atual)
            if cpf:
                identificador = cpf.group(1)
                grupo = [f for f in arquivos if "Nome_do_arquivo" in f and identificador in f]
            else:
                print(f"CPF não encontrado: {arquivo_atual}")
                continue

        else:
            print(f"Tipo não reconhecido: {arquivo_atual}")
            continue

        print(f"\n{tipo} — Identificador: {identificador} — {len(grupo)} arquivo(s)")
        for arquivo in grupo:
            caminho = os.path.join(pasta, arquivo)
            with pikepdf.Pdf.open(caminho) as pdf:
                pdf_final.pages.extend(pdf.pages)
            print(f"- Adicionado: {arquivo}")
            processados.add(arquivo)

        nome_final = f"Novo_nome_{tipo}_{identificador}.pdf"
        caminho_saida = os.path.join(saida, nome_final)
        pdf_final.save(caminho_saida)
        print(f"Salvo: '{nome_final}' com {len(pdf_final.pages)} páginas!")