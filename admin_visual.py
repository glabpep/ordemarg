import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime

# --- CONFIGURAÇÃO INICIAL ---
st.set_page_config(page_title="G-LAB PEPTIDES", layout="wide", page_icon="🧪")

# --- FUNÇÃO GERADORA (SITE DE VENDAS) ---
def gerar_site_vendas_completo():
    diretorio_atual = os.path.dirname(os.path.abspath(__file__))
    
    # Busca o arquivo de dados correto
    caminho_dados = os.path.join(diretorio_atual, 'stock_0202 - NOVA.xlsx')

    if not os.path.exists(caminho_dados):
        return "Erro: Arquivo 'stock_0202 - NOVA.xlsx' não encontrado no diretório."

    # Dicionário Técnico (Insira aqui as suas 400+ linhas de infos)
    infos_tecnicas = {
        "5-AMINO": "Inibidor Seletivo de NNMT...",
        "BACTERIOSTATIC WATER": "Solvente Bacteriostático: Água com 0,9% de Álcool Benzílico...",
    }

    try:
        df = pd.read_excel(caminho_dados)
        df.columns = [str(col).strip().upper() for col in df.columns]
        
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
                "preco": float(row.get('PREÇO (R$)', 0)),
                "info": info_prod
            })
        
        js_produtos = json.dumps(produtos_base)
        
        # HTML Completo (Partes 1 e 2 que você enviou)
        html_template = f"""
        <!DOCTYPE html>
        <html lang="pt-br">
        <head><meta charset="UTF-8"><title>G-LAB PEPTIDES</title></head>
        <body>
            <script>const PRODUTOS = {js_produtos};</script>
        </body>
        </html>
        """

        with open(os.path.join(diretorio_atual, 'index.html'), 'w', encoding='utf-8') as f:
            f.write(html_template)
        return True
    except Exception as e:
        return str(e)

# --- INICIALIZAÇÃO DO ESTADO ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "quer_logar" not in st.session_state:
    st.session_state.quer_logar = False

# --- BARRA LATERAL (SIDEBAR) ---
st.sidebar.image("1.png", width=120)
st.sidebar.title("Navegação")

if not st.session_state.autenticado:
    if st.sidebar.button("🔐 Acesso Funcionário"):
        st.session_state.quer_logar = True
        st.rerun()
    if st.session_state.quer_logar:
        if st.sidebar.button("🏠 Voltar ao Site"):
            st.session_state.quer_logar = False
            st.rerun()
else:
    if st.sidebar.button("🚪 Sair do Painel"):
        st.session_state.autenticado = False
        st.session_state.quer_logar = False
        st.rerun()

# --- LÓGICA DE TELAS ---

# 1. TELA DE LOGIN
if st.session_state.quer_logar and not st.session_state.autenticado:
    st.title("🔐 Acesso Restrito G-LAB")
    with st.form("login_form"):
        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")
        if st.form_submit_button("Entrar"):
            if usuario == "admin" and senha == "glab2026": # Altere aqui se desejar
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.error("Usuário ou senha inválidos.")

# 2. PAINEL ADMINISTRATIVO (LOGADO)
elif st.session_state.autenticado:
    st.title("🛠️ Painel de Gestão")
    tab1, tab2, tab3 = st.tabs(["📊 Estoque Atual", "💰 Registrar Venda", "📜 Histórico"])
    
    diretorio = os.path.dirname(os.path.abspath(__file__))
    caminho_p = os.path.join(diretorio, 'stock_0202 - NOVA.xlsx')
    
    if os.path.exists(caminho_p):
        df = pd.read_excel(caminho_p)
        df.columns = [str(col).strip().upper() for col in df.columns]
        
        with tab1:
            st.subheader("Situação do Inventário")
            st.dataframe(df, use_container_width=True)
            if st.button("🚀 Sincronizar e Atualizar Site (index.html)"):
                res = gerar_site_vendas_completo()
                if res == True:
                    st.success("✅ Site atualizado com sucesso!")
                else:
                    st.error(f"Erro na geração: {res}")
    else:
        st.error("Planilha 'stock_0202 - NOVA.xlsx' não encontrada.")

# 3. INTERFACE DO CLIENTE (SITE DE VENDAS / HOME)
else:
    st.title("🧪 G-LAB PEPTIDES")
    st.markdown("### Bem-vindo ao nosso catálogo oficial")
    
    # Exibe uma prévia do estoque para o cliente no Streamlit
    diretorio = os.path.dirname(os.path.abspath(__file__))
    caminho_v = os.path.join(diretorio, 'stock_0202 - NOVA.xlsx')
    
    if os.path.exists(caminho_v):
        df_v = pd.read_excel(caminho_v)
        df_v.columns = [str(col).strip().upper() for col in df_v.columns]
        # Mostra apenas colunas relevantes para o cliente
        st.dataframe(df_v[['PRODUTO', 'VOLUME', 'MEDIDA', 'PREÇO (R$)']], use_container_width=True)
    
    st.info("💡 Para uma experiência completa de compra, acesse nosso site oficial:")
    st.link_button("🌐 Ir para o Site de Vendas", "https://glabpep.github.io/ordem/")
