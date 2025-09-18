import cv2
import numpy as np
import pandas as pd
import os
import pytesseract
import tkinter as tk
from tkinter import scrolledtext, font, messagebox
import threading
import queue
import sys # <--- ADICIONADO E ESSENCIAL

# --- Bloco para fazer o Tesseract funcionar no .EXE ---
# Este bloco verifica se o script está rodando como um executável
# e, em caso afirmativo, aponta para o local onde o Tesseract foi empacotado.
if getattr(sys, 'frozen', False):
    tesseract_path = os.path.join(sys._MEIPASS, 'Tesseract-OCR', 'tesseract.exe')
    pytesseract.pytesseract.tesseract_cmd = tesseract_path
# ----------------------------------------------------


# --- CONFIGURAÇÕES GLOBAIS ---
# Parâmetros do Extrator
QUESTION_MAP_IDS = [
    "1.1.1", "1.1.2", "1.1.3", "1.1.4", "1.2.1", "1.2.2", "1.2.3", "1.2.4",
    "1.3.1", "1.3.2", "1.3.3", "1.3.4", "1.3.5", "II.1", "II.2", "II.3",
    "II.4", "II.5", "II.6", "II.7"
]
QUESTION_MAP_COORDS = [
    (1248, 800), (1319, 800), (1390, 800), (1460, 800), (1531, 800), (1247, 831), (1318, 831), (1389, 831), (1459, 831), (1530, 831),
    (1248, 864), (1319, 864), (1390, 864), (1460, 864), (1531, 864), (1248, 897), (1319, 897), (1390, 897), (1460, 897), (1531, 897),
    (1247, 961), (1318, 961), (1389, 961), (1459, 961), (1530, 961), (1247, 989), (1318, 989), (1389, 989), (1459, 989), (1530, 989),
    (1246, 1022), (1317, 1022), (1388, 1022), (1458, 1022), (1529, 1022), (1247, 1056), (1318, 1056), (1389, 1056), (1459, 1056), (1530, 1056),
    (1247, 1117), (1318, 1117), (1389, 1117), (1459, 1117), (1530, 1117), (1247, 1146), (1318, 1146), (1389, 1146), (1459, 1146), (1530, 1146),
    (1247, 1181), (1318, 1181), (1389, 1181), (1459, 1181), (1530, 1181), (1248, 1214), (1319, 1214), (1390, 1214), (1460, 1214), (1531, 1214),
    (1247, 1249), (1318, 1249), (1389, 1249), (1459, 1249), (1530, 1249), (1247, 1309), (1318, 1309), (1389, 1309), (1459, 1309), (1530, 1309),
    (1246, 1340), (1317, 1340), (1388, 1340), (1458, 1340), (1529, 1340), (1247, 1373), (1318, 1373), (1389, 1373), (1459, 1373), (1530, 1373),
    (1247, 1406), (1318, 1406), (1389, 1406), (1459, 1406), (1530, 1406), (1246, 1439), (1317, 1439), (1388, 1439), (1458, 1439), (1529, 1439),
    (1247, 1470), (1318, 1470), (1389, 1470), (1459, 1470), (1530, 1470), (1247, 1503), (1318, 1503), (1389, 1503), (1459, 1503), (1530, 1503)
]
CIRCLE_ROI_WIDTH, CIRCLE_ROI_HEIGHT = 45, 30
MARKED_PERCENT_THRESHOLD = 0.15
TEMPLATE_PATH = 'template/formulario_base.png'

TAREFAS_EXTRACAO = [
    { "nome": "Autoavaliações", "scans_folder": "01_Autoavaliacoes/scans", "output_csv": "01_Autoavaliacoes/resultados/autoavaliacoes.csv" },
    { "nome": "Avaliações dos Superiores", "scans_folder": "02_Avaliacoes_Superiores/scans", "output_csv": "02_Avaliacoes_Superiores/resultados/avaliacoes_superiores.csv" }
]
ARQUIVO_SAIDA_EXCEL = 'Relatorio_Final_Medias.xlsx'


# --- NÚCLEO LÓGICO (Funções do "Marco 0") ---

def gerar_mapa_de_coordenadas():
    mapa = {}
    for i, id_pergunta in enumerate(QUESTION_MAP_IDS):
        inicio, fim = i * 5, (i + 1) * 5
        mapa[id_pergunta] = QUESTION_MAP_COORDS[inicio:fim]
    return mapa

def ler_matricula_ocr(imagem_alinhada):
    try:
        x1, y1, x2, y2 = 1345, 286, 1441, 322 
        roi = imagem_alinhada[y1:y2, x1:x2]
        config = r'--psm 6 -c tessedit_char_whitelist=0123456789'
        texto = pytesseract.image_to_string(roi, config=config)
        return "".join(filter(str.isdigit, texto)) or "NAO_LIDO"
    except Exception:
        return "ERRO_OCR"

def alinhar_imagem(imagem, template):
    orb = cv2.ORB_create(nfeatures=2000)
    kp1, des1 = orb.detectAndCompute(imagem, None)
    kp2, des2 = orb.detectAndCompute(template, None)
    matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = sorted(matcher.match(des1, des2), key=lambda x: x.distance)[:50]
    src_pts = np.float32([kp1[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
    dst_pts = np.float32([kp2[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)
    matrix, _ = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
    h, w = template.shape
    return cv2.warpPerspective(imagem, matrix, (w, h))

def processar_formulario(caminho_imagem, template, question_map):
    try:
        imagem_original = cv2.imread(caminho_imagem, cv2.IMREAD_GRAYSCALE)
        if imagem_original is None: return None
        imagem_alinhada = alinhar_imagem(imagem_original, template)
        matricula = ler_matricula_ocr(imagem_alinhada)
        resultados = {'matricula': matricula, 'arquivo_origem': os.path.basename(caminho_imagem)}
        _, img_binaria = cv2.threshold(imagem_alinhada, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        soma_das_notas = 0
        for id_pergunta, coords in question_map.items():
            max_percentual, resposta = -1.0, 0
            for i, (x, y) in enumerate(coords):
                x_inicio, y_inicio = x - (CIRCLE_ROI_WIDTH // 2), y - (CIRCLE_ROI_HEIGHT // 2)
                roi = img_binaria[y_inicio:y_inicio+CIRCLE_ROI_HEIGHT, x_inicio:x_inicio+CIRCLE_ROI_WIDTH]
                percentual = cv2.countNonZero(roi) / (CIRCLE_ROI_WIDTH * CIRCLE_ROI_HEIGHT)
                if percentual > max_percentual:
                    max_percentual, resposta = percentual, i + 1
            
            resposta_final = resposta if max_percentual >= MARKED_PERCENT_THRESHOLD else 0
            resultados[id_pergunta] = resposta_final
            soma_das_notas += resposta_final
        
        resultados['SOMA_FINAL'] = soma_das_notas
        return resultados
    except Exception as e:
        print(f"Erro inesperado processando {os.path.basename(caminho_imagem)}: {e}")
        return None

# --- LÓGICA DAS TAREFAS (Para rodar em Threads) ---

def logica_extrator(queue):
    try:
        queue.put("--- INICIANDO ETAPA 1: EXTRAÇÃO DOS DADOS ---\n")
        template_reto = cv2.imread(TEMPLATE_PATH, cv2.IMREAD_GRAYSCALE)
        if template_reto is None:
            queue.put(f"ERRO CRÍTICO: Template '{TEMPLATE_PATH}' não encontrado.\n")
            return

        question_map = gerar_mapa_de_coordenadas()
        
        for tarefa in TAREFAS_EXTRACAO:
            scans_folder = tarefa["scans_folder"]
            output_csv = tarefa["output_csv"]
            queue.put(f"\nProcessando pasta: '{scans_folder}'...\n")
            
            results_folder = os.path.dirname(output_csv)
            if not os.path.exists(results_folder): os.makedirs(results_folder)
            if not os.path.exists(scans_folder):
                queue.put(f"AVISO: Pasta de scans '{scans_folder}' não encontrada. Pulando.\n")
                continue

            arquivos = [f for f in os.listdir(scans_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
            if not arquivos:
                queue.put(f"AVISO: Nenhum arquivo de imagem encontrado em '{scans_folder}'.\n")
                continue

            resultados_finais = []
            for nome_arquivo in arquivos:
                caminho = os.path.join(scans_folder, nome_arquivo)
                resultado = processar_formulario(caminho, template_reto, question_map)
                if resultado:
                    queue.put(f"  Lido: {nome_arquivo} | Matrícula: {resultado.get('matricula', 'N/A')}... OK\n")
                    resultados_finais.append(resultado)
            
            if resultados_finais:
                df = pd.DataFrame(resultados_finais)
                cols = ['matricula', 'arquivo_origem'] + QUESTION_MAP_IDS + ['SOMA_FINAL']
                df = df.reindex(columns=cols)
                df.to_csv(output_csv, index=False, sep=';')
                queue.put(f"-> SUCESSO: Arquivo '{output_csv}' gerado com {len(resultados_finais)} registros.\n")
        
        queue.put("\n--- ETAPA 1 CONCLUÍDA ---\n")
    except Exception as e:
        queue.put(f"\n!!! ERRO FATAL NA ETAPA 1: {e} !!!\n")
    finally:
        queue.put("ETAPA_1_FIM")


def logica_gerador_relatorio(queue):
    try:
        queue.put("\n--- INICIANDO ETAPA 2: GERAÇÃO DO RELATÓRIO FINAL ---\n")
        
        csv1 = TAREFAS_EXTRACAO[0]['output_csv']
        csv2 = TAREFAS_EXTRACAO[1]['output_csv']

        if not os.path.exists(csv1) or not os.path.exists(csv2):
            queue.put(f"ERRO: Arquivos CSV de entrada não encontrados. Execute a Etapa 1 primeiro.\n")
            return
            
        queue.put("Lendo arquivos CSV gerados...\n")
        df_auto = pd.read_csv(csv1, sep=';')
        df_sup = pd.read_csv(csv2, sep=';')
        
        queue.put("Cruzando dados pela matrícula...\n")
        df_merged = pd.merge(df_auto, df_sup, on='matricula', suffixes=('_auto', '_sup'))
        
        if df_merged.empty:
            queue.put("ERRO: Nenhuma matrícula em comum encontrada entre os arquivos.\n")
            return
            
        queue.put("Calculando médias...\n")
        colunas_perguntas = QUESTION_MAP_IDS
        for pergunta in colunas_perguntas:
            df_merged[f'Media_{pergunta}'] = (df_merged[f'{pergunta}_auto'] + df_merged[f'{pergunta}_sup']) / 2
        
        colunas_media = ['matricula'] + [f'Media_{p}' for p in colunas_perguntas]
        df_final = df_merged[colunas_media].copy()
        df_final['SOMA_TOTAL_DAS_MEDIAS'] = df_final[[f'Media_{p}' for p in colunas_perguntas]].sum(axis=1)
        
        df_final.to_excel(ARQUIVO_SAIDA_EXCEL, index=False, sheet_name='Medias Finais')
        queue.put(f"-> SUCESSO: Relatório '{ARQUIVO_SAIDA_EXCEL}' foi gerado com {len(df_final)} funcionários.\n")
        
        queue.put("\n--- ETAPA 2 CONCLUÍDA ---\n")
    except Exception as e:
        queue.put(f"\n!!! ERRO FATAL NA ETAPA 2: {e} !!!\n")
    finally:
        queue.put("ETAPA_2_FIM")


# --- APLICAÇÃO GRÁFICA (GUI) ---

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Processador de Avaliações de Desempenho v1.0")
        self.root.geometry("800x600")
        self.queue = queue.Queue()
        
        main_frame = tk.Frame(root, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        self.log_text = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, state='disabled', bg='black', fg='light green', font=("Courier New", 9))
        self.log_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X)

        self.btn_etapa1 = tk.Button(button_frame, text="Etapa 1: Extrair Dados dos Scans", command=lambda: self.iniciar_tarefa(logica_extrator, self.btn_etapa1), font=("Helvetica", 10, "bold"), height=2)
        self.btn_etapa1.pack(fill=tk.X, pady=2)
        
        self.btn_etapa2 = tk.Button(button_frame, text="Etapa 2: Gerar Relatório Final (Soma das Médias)", command=lambda: self.iniciar_tarefa(logica_gerador_relatorio, self.btn_etapa2), font=("Helvetica", 10, "bold"), height=2)
        self.btn_etapa2.pack(fill=tk.X, pady=2)
        
        self.status_bar = tk.Label(main_frame, text="Pronto.", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def adicionar_log(self, mensagem):
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, mensagem)
        self.log_text.config(state='disabled')
        self.log_text.see(tk.END)

    def processar_fila(self, tarefa_btn):
        try:
            msg = self.queue.get_nowait()
            if msg in ["ETAPA_1_FIM", "ETAPA_2_FIM"]:
                tarefa_btn.config(state='normal')
                self.status_bar.config(text="Pronto.")
                if msg == "ETAPA_1_FIM":
                     messagebox.showinfo("Concluído", "Etapa 1 (Extração) finalizada.")
                else:
                     messagebox.showinfo("Concluído", f"Etapa 2 (Geração de Relatório) finalizada! Arquivo '{ARQUIVO_SAIDA_EXCEL}' está pronto.")
            else:
                self.adicionar_log(msg)
                self.root.after(100, lambda: self.processar_fila(tarefa_btn))
        except queue.Empty:
            self.root.after(100, lambda: self.processar_fila(tarefa_btn))

    def iniciar_tarefa(self, logica, botao):
        botao.config(state='disabled')
        self.status_bar.config(text="Processando...")
        self.adicionar_log("") # Adiciona uma linha em branco para separar logs
        
        self.thread = threading.Thread(target=logica, args=(self.queue,))
        self.thread.start()
        self.processar_fila(botao)

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()