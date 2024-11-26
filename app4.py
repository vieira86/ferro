import random
import streamlit as st
import numpy as np
import plotly.graph_objects as go
from PIL import Image

# Inicializar estado da sessão
if "tipo_experimento" not in st.session_state:
    st.session_state.tipo_experimento = None
if "beta_1" not in st.session_state:
    st.session_state.beta_1 = None

# Exibir imagem inicial
image = Image.open('icone.png')  # Certifique-se de que o arquivo está no diretório correto
image = image.resize((800, 300))
st.image(image)

# Barra lateral para menu e seleção de experimento
menu = ["Home", "Experimento A", "Experimento B", "About"]
choice = st.sidebar.radio("Menu", menu)

# Seção "Home"
if choice == "Home":
    st.title("Bem-vindo ao Analisador de Ferro na Água!")
    st.write("""
        Este aplicativo permite automatizar os cálculos
        de concentração de ferro na água com base em absorbâncias medidas.
    """)

# Função para calcular a regressão linear sem intercepto e gerar o gráfico de regressão
def calcular_regressao(concentracao, absorbancia):
    numerador = np.sum(concentracao * absorbancia)
    denominador = np.sum(concentracao ** 2)
    beta_1 = numerador / denominador
    previsao = beta_1 * concentracao

    ss_total_excel = np.sum(absorbancia ** 2)
    ss_residual_excel = np.sum((absorbancia - previsao) ** 2)
    r2_excel = 1 - (ss_residual_excel / ss_total_excel)

    equacao = f'Absorbância = {beta_1:.4f} * Concentração'
    st.write(f"Equação da reta de calibração: {equacao}")
    st.write(f"Coeficiente de determinação (R² - método Excel): {r2_excel:.4f}")

    # Plotar a curva de calibração
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=concentracao, y=absorbancia, mode='markers', name='Dados experimentais'))
    fig.add_trace(go.Scatter(x=concentracao, y=previsao, mode='lines', name='Regressão linear (Sem Intercepto)'))

    fig.update_layout(
        title=f'Curva de Calibração (R² = {r2_excel:.4f})',
        xaxis_title='Concentração (mg/L)',
        yaxis_title='Absorbância',
        showlegend=True
    )
    st.plotly_chart(fig)

    return beta_1

# Função para gerar cores aleatórias em formato hexadecimal
def gerar_cor_aleatoria():
    return f"#{''.join([random.choice('0123456789ABCDEF') for _ in range(6)])}"

# Seção de Experimentos
if choice in ["Experimento A", "Experimento B"]:
    st.title(f"Análise - {choice}")
    st.session_state.tipo_experimento = choice

    # Definir concentração comum
    concentracao = np.array([0, 0.1, 0.2, 0.4, 0.6, 0.8, 1])

    # Definir os valores de absorbância de acordo com o experimento
    if choice == "Experimento A":
        absorbancia = np.array([0, 0.073, 0.074, 0.108, 0.163, 0.160, 0.226])
    elif choice == "Experimento B":
        absorbancia = np.array([0, 0.027, 0.045, 0.083, 0.132, 0.191, 0.222])

    # Calcular a regressão e armazenar o valor de beta_1 no estado da sessão
    st.session_state.beta_1 = calcular_regressao(concentracao, absorbancia)

    # Perguntar quantas análises de água serão feitas
    num_analises = st.number_input("Quantas análises de água serão feitas?", min_value=1, step=1)

    # Inserir os valores de absorbância para cada análise
    absorbancias_analise = []
    for i in range(num_analises):
        valor = st.number_input(
            f"Insira o valor da absorbância para a análise {i+1} (5 casas decimais):",
            format="%.4f",
            step=0.001,
            key=f"abs{i}"
        )
        absorbancias_analise.append(valor)

    # Calcular e exibir a concentração para cada valor de absorbância inserido
    if st.button("Calcular concentrações"):
        concentracoes_calculadas = []
        for i, abs_val in enumerate(absorbancias_analise):
            concentracao_calculada = abs_val / st.session_state.beta_1
            concentracoes_calculadas.append(concentracao_calculada)
            st.write(f"Concentração calculada para a análise {i+1}: {concentracao_calculada:.3f} mg/L")

        # Gerar gráfico de barras com cores aleatórias e limite de 0,3 mg/L
        if concentracoes_calculadas:
            cores_aleatorias = [gerar_cor_aleatoria() for _ in range(num_analises)]
            fig_barras = go.Figure(data=[
                go.Bar(x=[f'Análise {i+1}' for i in range(num_analises)], y=concentracoes_calculadas, marker_color=cores_aleatorias)
            ])

            # Adicionar a linha limite
            fig_barras.add_shape(
                type="line",
                x0=-0.5,
                x1=num_analises - 0.5,
                y0=0.3,
                y1=0.3,
                line=dict(color="red", width=2, dash="dash"),
            )

            fig_barras.update_layout(
                title="Concentrações Calculadas nas Análises de Água",
                xaxis_title="Análise",
                yaxis_title="Concentração (mg/L)",
                showlegend=False
            )

            st.plotly_chart(fig_barras)

            # Determinar e exibir se a água é própria ou imprópria
            for i, conc in enumerate(concentracoes_calculadas):
                status = "Própria" if conc <= 0.3 else "Imprópria"
                st.write(f"A amostra da análise {i+1} é: **{status} para consumo**.")


# Seção "About"
if choice == "About":
    st.title("Sobre")
    st.write("""
        Este aplicativo foi desenvolvido com base nos experimentos realizados nos projetos de pesquisa do IFRO, 
        para isso, esse sistema automatiza cálculos de regressão linear e concentração e as 
        relaciona com dados experimentais de absorbância para determinação do teor de ferro em água.
    """)
