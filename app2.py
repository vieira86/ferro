import random
import streamlit as st
import numpy as np
import plotly.graph_objects as go

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

# Inicializar estado da sessão
if "tipo_experimento" not in st.session_state:
    st.session_state.tipo_experimento = None
if "beta_1" not in st.session_state:
    st.session_state.beta_1 = None

# Seção principal do Streamlit
st.title("Experimentos de Calibração")

# Botões para selecionar o tipo de experimento
col1, col2 = st.columns(2)

with col1:
    if st.button("Selecionar Experimento A"):
        st.session_state.tipo_experimento = "Experimento A"
with col2:
    if st.button("Selecionar Experimento B"):
        st.session_state.tipo_experimento = "Experimento B"

# Mostrar o restante da interface se um tipo de experimento foi selecionado
if st.session_state.tipo_experimento:
    st.write(f"Você selecionou o {st.session_state.tipo_experimento}")

    # Definir concentração comum
    concentracao = np.array([0, 0.1, 0.2, 0.4, 0.6, 0.8, 1])

    # Definir os valores de absorbância de acordo com o experimento
    if st.session_state.tipo_experimento == "Experimento A":
        absorbancia = np.array([0, 0.027, 0.045, 0.083, 0.132, 0.191, 0.222])
    elif st.session_state.tipo_experimento == "Experimento B":
        absorbancia = np.array([0, 0.073, 0.074, 0.108, 0.163, 0.160, 0.226])

    # Calcular a regressão e armazenar o valor de beta_1 no estado da sessão
    st.session_state.beta_1 = calcular_regressao(concentracao, absorbancia)

    # Perguntar quantas análises de água serão feitas
    num_analises = st.number_input("Quantas análises de água serão feitas?", min_value=1, step=1)

    # Inserir os valores de absorbância para cada análise
    absorbancias_analise = []
    for i in range(num_analises):
        # Alterar o step para 0,001
        valor = st.number_input(
            f"Insira o valor da absorbância para a análise {i+1} (5 casas decimais):", 
            format="%.4f", 
            step=0.001,  # Definindo o incremento para 0,001
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

        # Gerar gráfico de barras com cores aleatórias
        if concentracoes_calculadas:
            cores_aleatorias = [gerar_cor_aleatoria() for _ in range(num_analises)]  # Gerar cores aleatórias para as barras
            fig_barras = go.Figure(data=[
                go.Bar(x=[f'Análise {i+1}' for i in range(num_analises)], y=concentracoes_calculadas, marker_color=cores_aleatorias)
            ])

            fig_barras.update_layout(
                title="Concentrações Calculadas nas Análises de Água",
                xaxis_title="Análise",
                yaxis_title="Concentração (mg/L)",
                showlegend=False
            )

            st.plotly_chart(fig_barras)
