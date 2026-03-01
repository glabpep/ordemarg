import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import os
import json

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="G-LAB PEPTIDES", layout="wide", page_icon="🧪")

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

# Limpa o visual do Streamlit
st.markdown("""
    <style>
        .block-container { padding: 0rem; max-width: 100%; }
        footer {visibility: hidden;}
        header {visibility: hidden;}
        [data-testid="stSidebar"] { background-color: #f8f9fa; }
    </style>
""", unsafe_allow_html=True)

# --- 2. CARREGAR DADOS DO EXCEL ---
def carregar_estoque():
    # Procura pelos nomes de arquivos que você costuma usar
    for nome in ['stock_0202 - NOVA.xlsx', 'stock_2901.xlsx']:
        if os.path.exists(nome):
            df = pd.read_excel(nome)
            df.columns = [str(col).strip() for col in df.columns]
            return df, nome
    return pd.DataFrame(), None

# --- 3. INJETAR DADOS NO SEU INDEX.HTML ---
def preparar_html_dinamico(produtos_json):
    if os.path.exists('index.html'):
        with open('index.html', 'r', encoding='utf-8') as f:
            conteudo = f.read()
        
        # O SEGREDO: Injetamos os dados do Excel antes do fechamento do Body
        # Isso substitui a variável 'produtosBase' (ou similar) que seu script usa
        script_dados = f"""
        <script>
            // Sobrescrevemos a lista estática pela lista do Excel
            var produtosBase = {produtos_json};
            
            // Forçamos o seu HTML a redesenhar a lista com os novos dados
            // assim que a página carregar, mantendo suas funções de carrinho
            window.onload = function() {{
                if (typeof renderizarProdutos === 'function') {{
                    renderizarProdutos(); 
                }}
            }};
        </script>
        """
        return conteudo.replace("</body>", f"{script_dados}</body>")
    return "<h1>Erro: index.html não encontrado!</h1>"

# --- 4. PROCESSAMENTO DOS PRODUTOS ---
df_estoque, arquivo_nome = carregar_estoque()
lista_final = []

if not df_estoque.empty:
    col_preco = 'Preço (R$)' if 'Preço (R$)' in df_estoque.columns else 'PREÇO'
    
    for _, row in df_estoque.iterrows():
        nome_p = str(row.get('PRODUTO', '')).strip()
        # Mapeamento idêntico ao que seu index.html espera
        lista_final.append({
            "nome": nome_p,
            "espec": f"{row.get('VOLUME', '')} {row.get('MEDIDA', '')}",
            "preco": float(row.get(col_preco, 0)),
            "estoque": str(row.get('ESTOQUE', 'EM ESPERA')).upper(),
            "qtd": int(row.get('QTD', 0)) if pd.notna(row.get('QTD')) else 0,
            "img": f"https://raw.githubusercontent.com/glabpep/ordem/main/{nome_p.replace(' ', '%20')}.webp"
        })

# --- 5. INTERFACE ---
with st.sidebar:
    st.image("https://github.com/glabpep/ordem/blob/main/1.png?raw=true", use_container_width=True)
    menu = st.radio("NAVEGAÇÃO", ["🛒 LOJA ONLINE", "🔐 PAINEL ADMIN"])

if menu == "🛒 LOJA ONLINE":
    html_pronto = preparar_html_dinamico(json.dumps(lista_final))
    # Renderiza o seu HTML com os dados do Excel injetados
    components.html(html_pronto, height=1500, scrolling=True)

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
        st.write(f"Editando arquivo: **{arquivo_nome}**")
        
        df_editado = st.data_editor(df_estoque, use_container_width=True, hide_index=True)
        
        if st.button("💾 SALVAR E ATUALIZAR SITE"):
            df_editado.to_excel(arquivo_nome, index=False)
            st.success("Estoque atualizado com sucesso! Vá na aba 'LOJA' para ver.")
            st.rerun()
            
        if st.button("Sair"):
            st.session_state.autenticado = False
            st.rerun()
