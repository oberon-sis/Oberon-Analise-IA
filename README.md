
## 🧠 Oberon - Analise-IA

Repositório dedicado ao **Motor de Inteligência Analítica** do projeto Oberon. Ele é responsável por processar os dados brutos, aplicar algoritmos de **IA/Machine Learning** e calcular todas as métricas avançadas (previsão, tendência e correlação).

## ✨ Funcionalidades Chave

Este repositório é o núcleo de inteligência do sistema, transformando dados em *insights*:

  * **Cálculo de Tendências:** Determina a evolução e o comportamento futuro das métricas de desempenho (*Uptime*, Alertas, etc.) usando **Regressão Linear** e outros modelos.
  * **Previsão de Desempenho:** Utiliza modelos de **Séries Temporais** e **Machine Learning (ML)** para projetar o desempenho futuro dos componentes.
  * **Análise de Correlação:** Identifica relações e dependências entre diferentes variáveis de hardware e alertas.
  * **Geração de Métricas Preditivas:** Cria os indicadores (`Metrics`) e interpretações textuais (`Interpretações`) que alimentam o **Dashboard Web**.
  * **Integração com Banco de Dados:** Acessa os dados brutos de monitoramento fornecidos pelo repositório `Oberon-Banco-De-Dados`.

## 🚀 Tecnologias e Dependências

Este projeto é desenvolvido integralmente em **Python** e utiliza bibliotecas específicas para ciência de dados e aprendizado de máquina.

### Linguagens & Ambiente

  * **Python 3.8+**
  * **SQL** (Interação com o Banco de Dados do projeto)

### Bibliotecas Python (Data Science e ML)

  * **Pandas** (Manipulação e estruturação de dados)
  * **Scikit-learn** (Implementação de modelos de Machine Learning, como Regressão)
  * **Statsmodels** (Para análise de séries temporais e modelos estatísticos)
  * **NumPy** (Suporte para operações numéricas de alto desempenho)

-----

## 🛠️ Como Funciona (Fluxo Básico)

O módulo atua em uma rotina programada, seguindo o fluxo:

1.  **Ingestão:** Conecta-se ao banco de dados e obtém o histórico de dados de desempenho.
2.  **Processamento:** Realiza o pré-processamento, limpeza e estruturação dos dados.
3.  **Modelagem:** Executa os modelos de ML/Estatísticos para calcular **Tendência**, **Correlação** e **Previsão**.
4.  **Entrega:** Exporta os resultados e as interpretações geradas para serem consumidas pela **`Oberon-Aplicacao-Web`**.

-----

## 💻 Como Rodar o Projeto

1.  **Clone o repositório:**
    ```bash
    git clone https://github.com/oberon-sis/Oberon-Analise-IA.git
    ```
2.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Configure o Ambiente:**
      * Preencha o arquivo `.env` com as credenciais de acesso ao Banco de Dados do projeto.
4.  **Execute o Processamento Principal:**
    ```bash
    python main.py
    ```