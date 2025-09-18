# ⚙️ Processador de Avaliações de Desempenho (ITAURB)

Bem-vindo! Este é o guia completo para o programa que automatiza a leitura e o cálculo das avaliações de desempenho.

---

## 🎯 O Que Este Programa Faz?

Imagine que você tem duas pilhas de formulários de papel preenchidos: uma com a autoavaliação de cada funcionário e outra com a avaliação que o chefe dele fez. Este programa faz o seguinte:

1.  **Lê as Imagens:** Ele "olha" para cada formulário digitalizado (`.jpg` ou `.png`).
2.  **Extrai os Dados:** Ele identifica o número da matrícula do funcionário e lê qual bolha (de 1 a 5) foi marcada em cada pergunta.
3.  **Calcula as Médias:** Ele pega a nota da autoavaliação e a nota da avaliação do chefe para cada pergunta, e calcula a média entre elas.
4.  **Gera um Relatório Final:** Ele cria um único arquivo **Excel (`.xlsx`)** com uma tabela limpa, mostrando a matrícula de cada funcionário e a média final para cada pergunta, além de uma soma total das médias.

O objetivo é transformar pilhas de papel em um relatório final pronto para análise, de forma rápida e sem erros de digitação.

---

## 🚀 Como Usar o Programa (Passo a Passo para a Comissão)

Você só precisa do arquivo `ProcessadorAvaliacoes.exe`. Não é preciso instalar mais nada.

### Passo 1: Organize as Pastas

Antes de começar, você precisa criar uma estrutura de pastas simples. O programa precisa saber onde encontrar os formulários.

1.  Crie uma pasta principal, por exemplo: `Avaliacoes_Setembro_2025`.
2.  Dentro dela, coloque o arquivo `ProcessadorAvaliacoes.exe`.
3.  Dentro dela, crie uma pasta chamada `template` e coloque o arquivo `formulario_base.png` dentro.
4.  Dentro dela, crie as duas pastas para os scans:
    * `01_Autoavaliacoes` e dentro dela, uma pasta `scans`.
    * `02_Avaliacoes_Superiores` e dentro dela, uma pasta `scans`.

A estrutura final deve ser esta:

```
Avaliacoes_Setembro_2025/
│
├── 01_Autoavaliacoes/
│   └── scans/
│       └── (coloque aqui os scans da autoavaliação)
│
├── 02_Avaliacoes_Superiores/
│   └── scans/
│       └── (coloque aqui os scans dos superiores)
│
├── template/
│   └── formulario_base.png
│
└── ProcessadorAvaliacoes.exe  <-- (O seu programa)
```

### Passo 2: Execute o Programa

Dê um duplo clique no `ProcessadorAvaliacoes.exe`. Uma janela com uma tela preta de log vai aparecer.

### Passo 3: Execute a Extração dos Dados

1.  Clique no primeiro botão: **"Etapa 1: Extrair Dados dos Scans"**.
2.  O programa vai começar a ler todos os arquivos das duas pastas `scans`. Você verá o progresso na tela de log.
3.  Quando terminar, ele mostrará uma mensagem de sucesso e terá criado dois arquivos `.csv` (planilhas de dados brutos) dentro das pastas `resultados` que ele mesmo cria. Você não precisa mexer nesses arquivos, eles são temporários.

### Passo 4: Gere o Relatório Final

1.  Após a Etapa 1 ser concluída com sucesso, clique no segundo botão: **"Etapa 2: Gerar Relatório Final (Soma das Médias)"**.
2.  O programa vai ler os arquivos `.csv` temporários, calcular todas as médias e a soma final.
3.  Ao final, ele mostrará uma mensagem de sucesso. O arquivo **`Relatorio_Final_Medias.xlsx`** aparecerá na pasta principal (`Avaliacoes_Setembro_2025/`).

**Pronto!** O seu relatório em Excel está pronto para ser utilizado pela comissão.

---

## 💻 Para Desenvolvedores: Como Gerar o Executável

Se você fez alguma alteração no código-fonte (`app.py`) e precisa gerar um novo `.exe`, siga os passos abaixo.

### Pré-requisitos
1.  **Python 3.11+** instalado.
2.  **Tesseract OCR:** Essencial para a leitura das matrículas.
    * **Windows:** Baixe e instale a partir [deste link](https://github.com/UB-Mannheim/tesseract/wiki). Durante a instalação, **marque a opção para adicionar o Tesseract ao PATH do sistema**.

### Passos para Configuração
1.  **Clone o repositório e crie um ambiente virtual:**
    ```bash
    git clone [https://github.com/Airton659/avaliacao_itaurb.git](https://github.com/Airton659/avaliacao_itaurb.git)
    cd avaliacao_itaurb
    python -m venv venv
    .\venv\Scripts\activate
    ```

2.  **Instale as dependências Python a partir do `requirements.txt`:**
    ```bash
    pip install -r requirements.txt
    ```

### Compilando o `.exe` com PyInstaller
1.  **Instale o PyInstaller:**
    ```bash
    pip install pyinstaller
    ```
2.  **Execute o comando de compilação:**
    No terminal, na pasta raiz do projeto, execute o comando abaixo. Lembre-se de **verificar e, se necessário, corrigir o caminho para a sua pasta de instalação do Tesseract**.

    ```bash
    # Exemplo para Windows com Tesseract instalado no local padrão do AppData
    pyinstaller --onefile --windowed --name="ProcessadorAvaliacoes" --add-data "C:/Users/SEU_USUARIO/AppData/Local/Programs/Tesseract-OCR;Tesseract-OCR" --add-data "template;template" app.py
    ```

    * **`--onefile`**: Cria um único arquivo `.exe`.
    * **`--windowed`**: Esconde a janela de console preta ao executar o programa.
    * **`--name`**: Define o nome do arquivo final.
    * **`--add-data`**: Comando crucial para incluir arquivos e pastas essenciais (como o Tesseract e a pasta `template`) dentro do executável.

3.  **Localize o arquivo:** O executável final, `ProcessadorAvaliacoes.exe`, estará na nova pasta `dist`.