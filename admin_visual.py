import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import os
import json

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="G-LAB PEPTIDES", layout="wide", page_icon="🧪")

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

# Limpeza de interface Streamlit
st.markdown("""
    <style>
        .block-container { padding: 0rem; max-width: 100%; }
        footer {visibility: hidden;}
        header {visibility: hidden;}
        [data-testid="stSidebar"] { background-color: #f8f9fa; }
    </style>
""", unsafe_allow_html=True)

# --- 2. BACKEND: CARREGAR EXCEL ---
def carregar_estoque():
    for nome in ['stock_0202 - NOVA.xlsx', 'stock_2901.xlsx']:
        if os.path.exists(nome):
            df = pd.read_excel(nome)
            df.columns = [str(col).strip() for col in df.columns]
            return df, nome
    return pd.DataFrame(), None

# --- 3. BACKEND: INJEÇÃO DE DADOS E CORREÇÃO DE FUNÇÃO ---
def preparar_html_com_backend(produtos_json):
    if os.path.exists('index.html'):
        with open('index.html', 'r', encoding='utf-8') as f:
            conteudo = f.read()
        
        # O ajuste do backend no JS:
        # 1. Definimos 'produtosBase' (ou o nome que seu HTML usa)
        # 2. Forçamos a variável 'carrinho' a estar pronta
        # 3. Rodamos a sua função de renderização original
        script_backend = f"""
        <script>
            // Injeção do Backend para o Front
            window.produtosBase = {produtos_json}; 
            var produtos = window.produtosBase; // Compatibilidade com nomes comuns
            
            // Garante que as funções de clique funcionem após o carregamento
            document.addEventListener("DOMContentLoaded", function() {{
                if (typeof renderizarProdutos === 'function') {{
                    renderizarProdutos();
                }} else if (typeof render === 'function') {{
                    render();
                }}
                console.log("Backend G-LAB conectado com sucesso.");
            }});
        </script>
        """
        return conteudo.replace("</body>", f"{script_backend}</body>")
    return "<h1>Erro: index.html não encontrado!</h1>"

# --- 4. PROCESSAMENTO ---
df_estoque, arquivo_nome = carregar_estoque()
produtos_lista = []

if not df_estoque.empty:
    col_p = 'Preço (R$)' if 'Preço (R$)' in df_estoque.columns else 'PREÇO'
    for _, row in df_estoque.iterrows():
        nome_item = str(row.get('PRODUTO', '')).strip()
        produtos_lista.append({
            "nome": nome_item,
            "espec": f"{{}} {{}}".format(row.get('VOLUME', ''), row.get('MEDIDA', '')),
            "preco": float(row.get(col_p, 0)),
            "estoque": str(row.get('ESTOQUE', 'EM ESPERA')).upper(),
            "qtd": int(row.get('QTD', 0)) if pd.notna(row.get('QTD')) else 0,
            "img": f"https://raw.githubusercontent.com/glabpep/ordem/main/{{}}.webp".format(nome_item.replace(' ', '%20').upper())
        })

# --- 5. INTERFACE ---
with st.sidebar:
    st.image("https://github.com/glabpep/ordem/blob/main/1.png?raw=true", use_container_width=True)
    menu = st.radio("NAVEGAÇÃO", ["🛒 LOJA ONLINE", "🔐 PAINEL ADMIN"])

if menu == "🛒 LOJA ONLINE":
    # Aqui o backend entrega o HTML "vivo"
    html_final = preparar_html_com_backend(json.dumps(produtos_lista))
    components.html(html_final, height=2000, scrolling=True)

else:
    if not st.session_state.autenticado:
        st.subheader("Acesso Restrito")
        u = st.text_input("Usuário")
        p = st.text_input("Senha", type="password")
        if st.button("Entrar"):
            if u == "admin" and p == "glab2026":
                st.session_state.autenticado = True
                st.rerun()
    else:
        st.title("⚙️ Gerenciar Estoque")
        df_editado = st.data_editor(df_estoque, use_container_width=True, hide_index=True)
        if st.button("💾 SALVAR E ATUALIZAR"):
            df_editado.to_excel(arquivo_nome, index=False)
            st.success("Dados salvos no Excel!")
            st.rerun()
