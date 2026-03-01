import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- 1. CONFIGURAÇÃO DA PÁGINA (Sempre a primeira linha) ---
st.set_page_config(page_title="G-LAB Peptides", layout="wide", page_icon="🧪")

# Importação da lógica do estoque.py
try:
    from estoque import gerar_site_vendas_completo
except ImportError:
    st.error("⚠️ Arquivo 'estoque.py' não encontrado.")

# --- 2. FUNÇÕES DE SUPORTE ---
def localizar_planilha():
    diretorio_atual = os.path.dirname(os.path.abspath(__file__))
    for nome in ['stock_0202 - NOVA.xlsx', 'stock_2901.xlsx']:
        caminho = os.path.join(diretorio_atual, nome)
        if os.path.exists(caminho):
            return caminho
    return None

# --- 3. ESTADOS DE NAVEGAÇÃO ---
if "pagina_atual" not in st.session_state:
    st.session_state.pagina_atual = "vendas"  # Começa na página de vendas (cliente)
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

# --- 4. BARRA LATERAL (BOTÃO DE ADMIN) ---
st.sidebar.image("1.png", width=120)
if st.session_state.pagina_atual == "vendas":
    if st.sidebar.button("🔐 Área do Colaborador"):
        st.session_state.pagina_atual = "login"
        st.rerun()
else:
    if st.sidebar.button("⬅️ Voltar ao Site"):
        st.session_state.pagina_atual = "vendas"
        st.rerun()

# --- 5. LÓGICA DE EXIBIÇÃO DE TELAS ---

# TELA A: SITE DE VENDAS (INTERFACE DO CLIENTE)
if st.session_state.pagina_atual == "vendas":
    st.title("🧪 G-LAB Peptides - Pedidos Online")
    st.info("Previsão de chegada de novos itens: 09/03/2026")
    
    caminho_planilha = localizar_planilha()
    if caminho_planilha:
        df = pd.read_excel(caminho_planilha)
        df.columns = [str(col).strip().upper() for col in df.columns]
        
        # Simulação da vitrine que o cliente vê
        st.write("### Itens Disponíveis")
        # Aqui você pode manter a lógica de exibição que já tinha no index.html
        st.dataframe(df[['PRODUTO', 'VOLUME', 'MEDIDA', 'PREÇO (R$)']], use_container_width=True)
        st.warning("⚠️ Informe seu CEP no carrinho para calcular o frete.")
    else:
        st.error("Erro ao carregar catálogo de produtos.")

# TELA B: LOGIN PARA ADMIN
elif st.session_state.pagina_atual == "login" and not st.session_state.autenticado:
    st.title("🔐 Acesso Restrito G-LAB")
    with st.form("login_admin"):
        user = st.text_input("Usuário")
        pw = st.text_input("Senha", type="password")
        if st.form_submit_button("Entrar"):
            if user == "admin" and pw == "glab2026":
                st.session_state.autenticado = True
                st.session_state.pagina_atual = "admin"
                st.rerun()
            else:
                st.error("Credenciais inválidas.")

# TELA C: PAINEL ADMINISTRATIVO (SÓ EXIBE SE AUTENTICADO)
elif st.session_state.pagina_atual == "admin" or st.session_state.autenticado:
    st.title("🧪 Painel de Controle G-LAB")
    
    # Abas do Admin - Estoque é a PRIMEIRA
    tab1, tab2, tab3 = st.tabs(["📊 Estoque Atual", "💰 Registrar Venda", "📜 Histórico"])
    
    caminho_planilha = localizar_planilha()
    df = pd.read_excel(caminho_planilha)
    df.columns = [str(col).strip().upper() for col in df.columns]
    if 'QTD' in df.columns:
        df['QTD'] = pd.to_numeric(df['QTD'], errors='coerce').fillna(0)

    with tab1:
        st.subheader("Situação do Inventário")
        st.dataframe(df.style.highlight_between(left=0, right=0, color='#ffcccc', subset=['QTD']), use_container_width=True)
        if st.button("🔄 Sincronizar com o Site Principal"):
            gerar_site_vendas_completo()
            st.success("Site sincronizado!")

    with tab2:
        st.subheader("Baixa Manual de Estoque")
        # Lógica de venda (seu código anterior de formulário aqui)
        st.info("Use esta aba para registrar vendas feitas por fora do site.")

    with tab3:
        st.subheader("Histórico de Vendas")
        try:
            df_hist = pd.read_excel(caminho_planilha, sheet_name='PEDIDOS_PAGOS')
            st.dataframe(df_hist, use_container_width=True)
        except:
            st.write("Sem histórico.")

    if st.sidebar.button("Sair do Admin"):
        st.session_state.autenticado = False
        st.session_state.pagina_atual = "vendas"
        st.rerun()
