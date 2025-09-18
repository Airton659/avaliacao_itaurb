import cv2
import numpy as np
import pandas as pd
import os
import pytesseract

# Se o Tesseract não foi adicionado ao PATH do seu sistema durante a instalação (Windows),
# você precisará descomentar a linha abaixo e colocar o caminho para o executável.
# Exemplo: pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# --- 1. CONFIGURAÇÃO ---
def gerar_mapa_de_coordenadas_manual():
    ids_das_perguntas = [
        "1.1.1", "1.1.2", "1.1.3", "1.1.4", "1.2.1", "1.2.2", "1.2.3", "1.2.4",
        "1.3.1", "1.3.2", "1.3.3", "1.3.4", "1.3.5", "II.1", "II.2", "II.3",
        "II.4", "II.5", "II.6", "II.7"
    ]
    todas_as_coordenadas = [
        (1248, 800), (1319, 800), (1390, 800), (1460, 800), (1531, 800),
        (1247, 831), (1318, 831), (1389, 831), (1459, 831), (1530, 831),
        (1248, 864), (1319, 864), (1390, 864), (1460, 864), (1531, 864),
        (1248, 897), (1319, 897), (1390, 897), (1460, 897), (1531, 897),
        (1247, 961), (1318, 961), (1389, 961), (1459, 961), (1530, 961),
        (1247, 989), (1318, 989), (1389, 989), (1459, 989), (1530, 989),
        (1246, 1022), (1317, 1022), (1388, 1022), (1458, 1022), (1529, 1022),
        (1247, 1056), (1318, 1056), (1389, 1056), (1459, 1056), (1530, 1056),
        (1247, 1117), (1318, 1117), (1389, 1117), (1459, 1117), (1530, 1117),
        (1247, 1146), (1318, 1146), (1389, 1146), (1459, 1146), (1530, 1146),
        (1247, 1181), (1318, 1181), (1389, 1181), (1459, 1181), (1530, 1181),
        (1248, 1214), (1319, 1214), (1390, 1214), (1460, 1214), (1531, 1214),
        (1247, 1249), (1318, 1249), (1389, 1249), (1459, 1249), (1530, 1249),
        (1247, 1309), (1318, 1309), (1389, 1309), (1459, 1309), (1530, 1309),
        (1246, 1340), (1317, 1340), (1388, 1340), (1458, 1340), (1529, 1340),
        (1247, 1373), (1318, 1373), (1389, 1373), (1459, 1373), (1530, 1373),
        (1247, 1406), (1318, 1406), (1389, 1406), (1459, 1406), (1530, 1406),
        (1246, 1439), (1317, 1439), (1388, 1439), (1458, 1439), (1529, 1439),
        (1247, 1470), (1318, 1470), (1389, 1470), (1459, 1470), (1530, 1470),
        (1247, 1503), (1318, 1503), (1389, 1503), (1459, 1503), (1530, 1503)
    ]
    mapa_completo = {}
    for i, id_pergunta in enumerate(ids_das_perguntas):
        inicio_bloco, fim_bloco = i * 5, (i + 1) * 5
        mapa_completo[id_pergunta] = todas_as_coordenadas[inicio_bloco:fim_bloco]
    return mapa_completo

QUESTION_MAP = gerar_mapa_de_coordenadas_manual()
CIRCLE_ROI_WIDTH, CIRCLE_ROI_HEIGHT = 45, 30
MARKED_PERCENT_THRESHOLD = 0.15
TEMPLATE_PATH = 'template/formulario_base.png'

def ler_matricula_ocr(imagem_alinhada):
    try:
        x1, y1, x2, y2 = 1345, 286, 1441, 322 
        roi_matricula = imagem_alinhada[y1:y2, x1:x2]
        config_ocr = r'--psm 6 -c tessedit_char_whitelist=0123456789'
        texto_matricula = pytesseract.image_to_string(roi_matricula, config=config_ocr)
        matricula_limpa = "".join(filter(str.isdigit, texto_matricula))
        return matricula_limpa if matricula_limpa else "NAO_LIDO"
    except Exception as e:
        print(f"   -> ERRO no OCR: {e}")
        return "ERRO_OCR"

def alinhar_imagem(imagem_processar, template):
    orb = cv2.ORB_create(nfeatures=2000)
    kp1, des1 = orb.detectAndCompute(imagem_processar, None)
    kp2, des2 = orb.detectAndCompute(template, None)
    matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = sorted(matcher.match(des1, des2), key=lambda x: x.distance)
    good_matches = matches[:50]
    src_pts = np.float32([kp1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
    dst_pts = np.float32([kp2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)
    matrix, _ = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
    h, w = template.shape
    return cv2.warpPerspective(imagem_processar, matrix, (w, h))

def processar_formulario(caminho_da_imagem, template_img):
    try:
        imagem_original = cv2.imread(caminho_da_imagem, cv2.IMREAD_GRAYSCALE)
        if imagem_original is None: return None
        imagem_alinhada = alinhar_imagem(imagem_original, template_img)
        matricula = ler_matricula_ocr(imagem_alinhada)
        resultados = {'matricula': matricula, 'arquivo_origem': os.path.basename(caminho_da_imagem)}
        _, img_binaria = cv2.threshold(imagem_alinhada, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        soma_das_notas = 0
        ids_perguntas = list(QUESTION_MAP.keys())

        for id_pergunta in ids_perguntas:
            lista_de_coords = QUESTION_MAP[id_pergunta]
            max_percentual = -1.0
            resposta_pergunta = 0 
            for i, (x, y) in enumerate(lista_de_coords):
                x_inicio, y_inicio = x - (CIRCLE_ROI_WIDTH // 2), y - (CIRCLE_ROI_HEIGHT // 2)
                roi = img_binaria[y_inicio:y_inicio+CIRCLE_ROI_HEIGHT, x_inicio:x_inicio+CIRCLE_ROI_WIDTH]
                percentual_preenchido = cv2.countNonZero(roi) / (CIRCLE_ROI_WIDTH * CIRCLE_ROI_HEIGHT)
                if percentual_preenchido > max_percentual:
                    max_percentual = percentual_preenchido
                    resposta_pergunta = i + 1
            if max_percentual < MARKED_PERCENT_THRESHOLD:
                resposta_pergunta = 0
            
            resultados[id_pergunta] = resposta_pergunta
            soma_das_notas += resposta_pergunta # Acumula a nota na soma

        # --- ALTERAÇÃO 1: Adiciona a soma final ao dicionário de resultados ---
        resultados['SOMA_FINAL'] = soma_das_notas

        return resultados
    except Exception as e:
        print(f"   -> ERRO INESPERADO em {os.path.basename(caminho_da_imagem)}: {e}")
        return None

def executar_processamento(scans_folder, output_csv_path, template_img):
    print(f"\n--- Processando Pasta: '{scans_folder}' ---")
    
    results_folder = os.path.dirname(output_csv_path)
    if not os.path.exists(results_folder):
        os.makedirs(results_folder)

    todos_os_resultados = []
    if not os.path.exists(scans_folder):
        print(f"AVISO: A pasta de scans '{scans_folder}' não foi encontrada.")
        return

    arquivos_scaneados = [f for f in os.listdir(scans_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    if not arquivos_scaneados:
        print(f"AVISO: Nenhum arquivo de imagem na pasta '{scans_folder}'.")
    else:
        for nome_arquivo in arquivos_scaneados:
            caminho_completo = os.path.join(scans_folder, nome_arquivo)
            resultado = processar_formulario(caminho_completo, template_img)
            
            if resultado:
                matricula = resultado.get('matricula', nome_arquivo)
                print(f"Analisando: {nome_arquivo} | Matrícula: {matricula}... OK")
                todos_os_resultados.append(resultado)

    if todos_os_resultados:
        df = pd.DataFrame(todos_os_resultados)
        
        # Garante a ordem das colunas, com a SOMA_FINAL no final
        ids_perguntas = list(QUESTION_MAP.keys())
        colunas_ordenadas = ['matricula', 'arquivo_origem'] + ids_perguntas + ['SOMA_FINAL']
        df = df[colunas_ordenadas]
        
        df.to_csv(output_csv_path, index=False, sep=';')
        print(f"-> Arquivo '{output_csv_path}' foi gerado com {len(todos_os_resultados)} formulários.")
    else:
        print("-> Nenhum formulário foi processado com sucesso nesta pasta.")

if __name__ == "__main__":
    print("Iniciando o processador de avaliações automatizado...")
    tarefas = [
        {
            "scans_folder": "01_Autoavaliacoes/scans",
            "output_csv": "01_Autoavaliacoes/resultados/autoavaliacoes.csv"
        },
        {
            "scans_folder": "02_Avaliacoes_Superiores/scans",
            "output_csv": "02_Avaliacoes_Superiores/resultados/avaliacoes_superiores.csv"
        }
    ]
    template_reto = cv2.imread(TEMPLATE_PATH, cv2.IMREAD_GRAYSCALE)
    if template_reto is None:
        print(f"ERRO CRÍTICO: Não foi possível carregar o template em '{TEMPLATE_PATH}'")
        exit()
    for tarefa in tarefas:
        executar_processamento(tarefa["scans_folder"], tarefa["output_csv"], template_reto)
    print("\n----------------------------------------------------")
    print("Todas as tarefas foram concluídas.")
    print("----------------------------------------------------")