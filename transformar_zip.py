import os
import zipfile


def comprimir_pdfs(pasta, saida):
    '''
    Pega `cada` arquivo .pdf do diretório informado e o transforma em .zip.
    Informar a pasta origem (onde contém os pdfs) e a pasta saída (onde ficarão salvos em zip).
    '''

    arquivos = [f for f in os.listdir(pasta) if f.endswith(".pdf")]

    if not arquivos:
        print("Nenhum PDF encontrado.")
        return

    for arquivo in arquivos:
        caminho_pdf = os.path.join(pasta, arquivo)
        nome_zip = arquivo.replace(".pdf", ".zip")
        caminho_zip = os.path.join(saida, nome_zip)

        with zipfile.ZipFile(caminho_zip, "w", zipfile.ZIP_DEFLATED) as zip_final:
            zip_final.write(caminho_pdf, arquivo)

        print(f"- {arquivo} salvo como {nome_zip}")

    print(f"\n{len(arquivos)} arquivos comprimidos!")