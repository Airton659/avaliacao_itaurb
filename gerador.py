import pandas as pd
import os

# --- CONFIGURAÇÃO ---
PASTA_AUTO = os.path.join('01_Autoavaliacoes', 'resultados')
PASTA_SUPERIOR = os.path.join('02_Avaliacoes_Superiores', 'resultados')

ARQUIVO_AUTOAVALIACAO = os.path.join(PASTA_AUTO, 'autoavaliacoes.csv')
ARQUIVO_AVALIACAO_SUPERIOR = os.path.join(PASTA_SUPERIOR, 'avaliacoes_superiores.csv')
ARQUIVO_SAIDA_EXCEL = 'Relatorio_Final_Medias.xlsx'

# --- LÓGICA PRINCIPAL ---
def gerar_relatorio_final():
    print("Iniciando o Gerador de Relatório de Médias...")

    if not os.path.exists(ARQUIVO_AUTOAVALIACAO) or not os.path.exists(ARQUIVO_AVALIACAO_SUPERIOR):
        print("\n--- ERRO ---")
        print("Não foi possível encontrar os arquivos .csv de entrada.")
        print("Verifique se você já executou o 'extrator.py' e se os arquivos foram gerados nas pastas corretas.")
        print(f"Esperado: '{ARQUIVO_AUTOAVALIACAO}'")
        print(f"Esperado: '{ARQUIVO_AVALIACAO_SUPERIOR}'")
        print("------------")
        exit()

    print(f"Lendo '{ARQUIVO_AUTOAVALIACAO}'...")
    df_auto = pd.read_csv(ARQUIVO_AUTOAVALIACAO, sep=';')

    print(f"Lendo '{ARQUIVO_AVALIACAO_SUPERIOR}'...")
    df_sup = pd.read_csv(ARQUIVO_AVALIACAO_SUPERIOR, sep=';')

    print("Cruzando dados pela matrícula...")
    df_merged = pd.merge(
        df_auto, # Mantém as colunas extras como SOMA_FINAL
        df_sup,
        on='matricula',
        suffixes=('_auto', '_sup')
    )
    
    if df_merged.empty:
        print("\n--- ERRO ---")
        print("Nenhuma matrícula em comum foi encontrada entre os dois arquivos CSV.")
        print("Verifique se as matrículas foram lidas corretamente nos dois arquivos.")
        print("------------")
        exit()

    print("Calculando as médias por pergunta...")
    colunas_perguntas = [col.replace('_auto', '') for col in df_merged.columns if '_auto' in col and col not in ['matricula_auto', 'arquivo_origem_auto', 'SOMA_FINAL_auto']]

    for pergunta in colunas_perguntas:
        col_auto = f'{pergunta}_auto'
        col_sup = f'{pergunta}_sup'
        col_media = f'Media_{pergunta}'
        
        df_merged[col_media] = (df_merged[col_auto] + df_merged[col_sup]) / 2
        df_merged[col_media] = df_merged[col_media].round(2)

    print("Montando o relatório final...")
    colunas_de_media = ['matricula'] + [f'Media_{p}' for p in colunas_perguntas]
    df_final = df_merged[colunas_de_media].copy()

    colunas_apenas_de_media = [f'Media_{p}' for p in colunas_perguntas]
    
    # --- ALTERAÇÃO 2: Troca a MÉDIA pela SOMA na coluna final ---
    df_final['SOMA_TOTAL_DAS_MEDIAS'] = df_final[colunas_apenas_de_media].sum(axis=1)

    try:
        df_final.to_excel(ARQUIVO_SAIDA_EXCEL, index=False, sheet_name='Medias Finais')
        print("\n----------------------------------------------------")
        print(f"SUCESSO! O relatório '{ARQUIVO_SAIDA_EXCEL}' foi gerado.")
        print("----------------------------------------------------")
    except Exception as e:
        print(f"\nERRO ao salvar o arquivo Excel: {e}")

if __name__ == "__main__":
    gerar_relatorio_final()