# --- CONFIGURE O AJUSTE AQUI ---
# Para deslocar para a esquerda, use um valor negativo (ex: -2)
# Para deslocar para a direita, use um valor positivo (ex: 2)
AJUSTE_X = -2

# Para deslocar para cima, use um valor negativo (ex: -2)
# Para deslocar para baixo, use um valor positivo (ex: 2)
AJUSTE_Y = 0
# ----------------------------------


# Lista original do nosso "Marco 0"
coordenadas_originais = [
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

print("Copiando e ajustando coordenadas...\n")
print("QUESTION_MAP_COORDS = [")

# Itera sobre a lista, aplicando o ajuste e imprimindo no formato correto
for i, (x, y) in enumerate(coordenadas_originais):
    novo_x = x + AJUSTE_X
    novo_y = y + AJUSTE_Y
    
    # Imprime a coordenada ajustada
    print(f"    ({novo_x}, {novo_y}),", end="")
    
    # Adiciona uma quebra de linha a cada 5 coordenadas
    if (i + 1) % 5 == 0:
        print() # Quebra de linha

print("]")
print("\nConcluído! Copie a lista 'QUESTION_MAP_COORDS' acima e cole no seu app.py")