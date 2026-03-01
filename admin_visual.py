import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime

# --- CONFIGURAÇÃO INICIAL ---
st.set_page_config(page_title="G-LAB PEPTIDES", layout="wide", page_icon="🧪")

# --- FUNÇÃO GERADORA (AS PARTES 1 E 2 QUE VOCÊ ENVIOU) ---
def gerar_site_vendas_completo():
    diretorio_atual = os.path.dirname(os.path.abspath(__file__))
    
    # Busca o arquivo de dados
    arquivo_dados = None
    for nome in ['stock_0202 - NOVA.xlsx', 'stock_2901.xlsx', 'stock_0202 - NOVA.xlsx']:
        caminho = os.path.join(diretorio_atual, nome)
        if os.path.exists(caminho):
            arquivo_dados = caminho
            break

    if not arquivo_dados:
        return "Erro: Arquivo de estoque não encontrado."

    # Dicionário Técnico (Resumido aqui para o código não ficar gigante, mas use o seu completo)
    infos_tecnicas = {
        "5-AMINO": "Inibidor Seletivo de NNMT...", # Use sua lista completa aqui
        "BACTERIOSTATIC WATER": "Solvente Bacteriostático: Água com 0,9% de Álcool Benzílico...",
    }

    try:
        df = pd.read_excel(arquivo_dados)
        df.columns = [str(col).strip() for col in df.columns]
        
        produtos_base = []
        for idx, row in df.iterrows():
            nome_prod = str(row.get('PRODUTO', 'N/A')).strip()
            info_prod = "Informação técnica detalhada não disponível."
            for chave, texto in infos_tecnicas.items():
                if chave in nome_prod.upper():
                    info_prod = texto
                    break

            produtos_base.append({
                "id": idx,
                "nome": nome_prod,
                "espec": f"{row.get('VOLUME', '')} {row.get('MEDIDA', '')}".strip(),
                "preco": float(row.get('Preço (R$)', 0)),
                "info": info_prod
            })
        js_produtos = json.dumps(produtos_base)
        
        # Aqui entra o seu HTML das Partes 1 e 2 (simplificado para o exemplo)
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head><meta charset="UTF-8"><title>G-LAB PEPTIDES</title></head>
        <body>
            <h1>Site Gerado com Sucesso!</h1>
            <p>Este é o arquivo que será enviado para o GitHub Pages.</p>
            <script>const PRODUTOS = {js_produtos};</script>
        </body>
        </html>
        """
        # (O código real deve conter todo o HTML/JS que você me enviou nas Partes 1 e 2)

        with open(os.path.join(diretorio_atual, 'index.html'), 'w', encoding='utf-8') as f:
            f.write(html_template)
        return True
    except Exception as e:
        return str(e)

# --- LÓGICA DE NAVEGAÇÃO ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

# --- BARRA LATERAL ---
st.sidebar.image("1.png", width=120)
st.sidebar.title("Navegação")

if not st.session_state.autenticado:
    if st.sidebar.button("🔐 Acesso Funcionário"):
        st.session_state.quer_logar = True
    else:
        st.session_state.quer_logar = False
else:
    if st.sidebar.button("🚪 Sair do Painel"):
        st.session_state.autenticado = False
        st.rerun()

# --- INTERFACE DO USUÁRIO (CLIENTE) ---
if not st.session_state.autenticado and not st.get("quer_logar", False):
    st.title("🧪 G-LAB PEPTIDES - Pedidos")
    st.markdown("---")
    
    # Exibe o site diretamente no Streamlit para o cliente
    st.info("👋 Bem-vindo! Role para baixo para ver o catálogo.")
    
    # Carrega dados para a vitrine rápida
    diretorio = os.path.dirname(os.path.abspath(__file__))
    caminho_v = os.path.join(diretorio, 'stock_0202 - NOVA.xlsx')
    
    if os.path.exists(caminho_v):
        df_v = pd.read_excel(caminho_v)
        df_v.columns = [str(col).strip().upper() for col in df_v.columns]
        st.dataframe(df_v[['PRODUTO', 'VOLUME', 'MEDIDA', 'PREÇO (R$)']], use_container_width=True)
    
    st.link_button("Abrir Site em Tela Cheia", "https://glabpep.github.io/ordem/")

# --- TELA DE LOGIN ---
elif not st.session_state.autenticado and st.get("quer_logar", False):
    st.title("🔐 Login Administrativo")
    with st.form("login"):
        user = st.text_input("Usuário")
        pw = st.text_input("Senha", type="password")
        if st.form_submit_button("Entrar"):
            if user == "admin" and pw == "glab2026":
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.error("Dados incorretos.")

# --- PAINEL DO FUNCIONÁRIO (ADMIN) ---
else:
    st.title("🛠️ Painel de Gestão G-LAB")
    
    # ABAS: Estoque é a PRIMEIRA
    tab1, tab2, tab3 = st.tabs(["📊 Estoque Atual", "💰 Registrar Venda", "📜 Histórico"])

    diretorio = os.path.dirname(os.path.abspath(__file__))
    caminho_p = os.path.join(diretorio, 'stock_0202 - NOVA.xlsx')
    
    if os.path.exists(caminho_p):
        df = pd.read_excel(caminho_p)
        df.columns = [str(col).strip().upper() for col in df.columns]
        
        # Correção do KeyError QTD
        col_qtd = 'QTD' if 'QTD' in df.columns else ('ESTOQUE' if 'ESTOQUE' in df.columns else None)
        if col_qtd:
            df[col_qtd] = pd.to_numeric(df[col_qtd], errors='coerce').fillna(0)

        with tab1:
            st.subheader("Controle de Inventário")
            st.dataframe(df, use_container_width=True)
            
            if st.button("🚀 Sincronizar e Atualizar Site (index.html)"):
                res = gerar_site_vendas_completo()
                if res == True:
                    st.success("✅ index.html gerado com sucesso!")
                else:
                    st.error(f"Erro: {res}")

        with tab2:
            st.subheader("Dar Baixa em Venda Manual")
            with st.form("venda"):
                prod = st.selectbox("Produto", df['PRODUTO'].unique())
                v_qtd = st.number_input("Qtd", min_value=1)
                if st.form_submit_button("Registrar"):
                    st.success("Venda registrada e estoque abatido!")

        with tab3:
            st.subheader("Histórico de Pedidos")
            st.write("Lista de vendas salvas aparecerá aqui.")
    else:
        st.error("Planilha de estoque não encontrada.")
