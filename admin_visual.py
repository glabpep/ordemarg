import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import os
import json

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="G-LAB PEPTIDES", layout="wide", page_icon="🧪")

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

# Limpa a interface do Streamlit para o seu site brilhar
st.markdown("""
    <style>
        .block-container { padding: 0rem; max-width: 100%; }
        footer {visibility: hidden;}
        header {visibility: hidden;}
        [data-testid="stSidebar"] { background-color: #f8f9fa; border-right: 1px solid #ddd; }
    </style>
""", unsafe_allow_html=True)

# --- 2. CARREGAR DADOS DO EXCEL ---
def carregar_estoque():
    caminho = 'stock_0202 - NOVA.xlsx'
    if os.path.exists(caminho):
        df = pd.read_excel(caminho)
        df.columns = [str(col).strip() for col in df.columns]
        return df
    return pd.DataFrame()

# --- 3. LER O SEU INDEX.HTML ORIGINAL ---
def carregar_seu_html(json_produtos):
    if os.path.exists('index.html'):
        with open('index.html', 'r', encoding='utf-8') as f:
            html = f.read()
        
        # Aqui está o "pulo do gato": 
        # Substituímos a variável que define os produtos no seu script original
        # Certifique-se que no seu index.html a variável de produtos se chame 'produtosBase' ou similar
        # Vou injetar um script no topo para sobrepor os dados estáticos pelos do Excel
        injecao_dados = f"<script>const produtosBase = {json_produtos};</script>"
        return html.replace("</head>", f"{injecao_dados}</head>")
    return "<h1>Erro: Arquivo index.html não encontrado na pasta!</h1>"

# --- 4. PROCESSAMENTO ---
df_estoque = carregar_estoque()
produtos_para_js = []

if not df_estoque.empty:
    for _, row in df_estoque.iterrows():
        nome_limpo = str(row.get('PRODUTO', '')).strip()
        produtos_para_js.append({
            "nome": nome_limpo,
            "espec": f"{row.get('VOLUME', '')} {row.get('MEDIDA', '')}",
            "preco": float(row.get('Preço (R$)', 0)),
            "estoque": str(row.get('ESTOQUE', 'EM ESPERA')).upper(),
            "qtd": int(row.get('QTD', 0)) if pd.notna(row.get('QTD')) else 0,
            # Mantém seu padrão de imagens do GitHub
            "img": f"https://raw.githubusercontent.com/glabpep/ordem/main/{nome_limpo.replace(' ', '%20')}.webp"
        })

# --- 5. NAVEGAÇÃO ---
with st.sidebar:
    st.image("https://github.com/glabpep/ordem/blob/main/1.png?raw=true", use_container_width=True)
    menu = st.radio("NAVEGAÇÃO", ["🛒 VER SITE (INDEX.HTML)", "🔐 ÁREA DO ADMIN"])

if menu == "🛒 VER SITE (INDEX.HTML)":
    # Aqui ele renderiza o SEU arquivo sem mudar uma linha de CSS
    html_final = carregar_seu_html(json.dumps(produtos_para_js))
    components.html(html_final, height=2000, scrolling=True)

else:
    # ÁREA ADMIN PARA VOCÊ EDITAR O EXCEL
    if not st.session_state.autenticado:
        u = st.text_input("Usuário")
        p = st.text_input("Senha", type="password")
        if st.button("Entrar"):
            if u == "admin" and p == "glab2026":
                st.session_state.autenticado = True
                st.rerun()
    else:
        st.title("📦 Controle de Estoque")
        df_editado = st.data_editor(df_estoque, use_container_width=True, hide_index=True)
        
        if st.button("💾 ATUALIZAR SITE (SALVAR EXCEL)"):
            df_editado.to_excel('stock_0202 - NOVA.xlsx', index=False)
            st.success("Estoque atualizado! O site já está refletindo os novos valores.")
            st.rerun()
        
        if st.button("Sair"):
            st.session_state.autenticado = False
            st.rerun()
