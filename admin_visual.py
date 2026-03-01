import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import os
import json

# --- 1. BLOQUEIO VISUAL DO STREAMLIT ---
st.set_page_config(page_title="G-LAB PEPTIDES", layout="wide", initial_sidebar_state="collapsed")

# Este bloco remove: Barra superior, Menu de opções, Rodapé e Padding extra
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .stDeployButton {display:none;}
        [data-testid="stHeader"] {display:none;}
        .block-container {padding: 0px; max-width: 100%;}
        iframe {border: none;}
        /* Esconde o botão de expandir do Streamlit em mobile */
        button[title="View fullscreen"] { display: none !important; }
    </style>
""", unsafe_allow_html=True)

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

# --- 2. BANCO DE DADOS ---
def carregar_estoque():
    caminho = 'stock_0202 - NOVA.xlsx'
    if os.path.exists(caminho):
        df = pd.read_excel(caminho)
        df.columns = [str(col).strip() for col in df.columns]
        return df
    return pd.DataFrame()

# --- 3. INJEÇÃO DE DADOS NO SEU HTML ---
def renderizar_site_glab():
    df = carregar_estoque()
    produtos_json = []
    
    for _, row in df.iterrows():
        nome = str(row.get('PRODUTO', '')).strip()
        # Link RAW do GitHub (Maiúsculas para evitar erro 404)
        img_url = f"https://raw.githubusercontent.com/glabpep/ordem/main/{nome.replace(' ', '%20').upper()}.webp"
        
        produtos_json.append({
            "nome": nome,
            "espec": f"{row.get('VOLUME', '')} {row.get('MEDIDA', '')}",
            "preco": float(row.get('Preço (R$)', 0)),
            "estoque": str(row.get('ESTOQUE', 'EM ESPERA')).upper(),
            "qtd": int(row.get('QTD', 0)) if pd.notna(row.get('QTD')) else 0,
            "img": img_url
        })

    if os.path.exists('index.html'):
        with open('index.html', 'r', encoding='utf-8') as f:
            html = f.read()
        
        # --- O PULO DO GATO ---
        # Substituímos o array vazio do seu HTML pelo array do Excel
        # Isso reativa o botão "+" e as imagens
        dados_vivos = f"<script>var produtosBase = {json.dumps(produtos_json)};</script>"
        html_final = html.replace("<head>", f"<head>{dados_vivos}")
        
        # Garante que as funções de renderização do seu index.html sejam chamadas
        script_boot = """
        <script>
            window.onload = function() {
                if(typeof renderizarProdutos === 'function') renderizarProdutos();
                if(typeof carregarCarrinho === 'function') carregarCarrinho();
            };
        </script>
        """
        return html_final.replace("</body>", f"{script_boot}</body>")
    return "<h1>Erro: index.html não encontrado!</h1>"

# --- 4. ESTRUTURA DE NAVEGAÇÃO ---
# Criamos um menu lateral que o usuário comum não vai mexer
with st.sidebar:
    st.title("G-LAB MENU")
    opcao = st.radio("Ir para:", ["🛒 Loja", "⚙️ Painel Admin"])

if opcao == "🛒 Loja":
    # Renderiza seu site ocupando 100% da tela
    components.html(renderizar_site_glab(), height=2500, scrolling=True)

else:
    # --- ÁREA ADMINISTRATIVA ---
    if not st.session_state.autenticado:
        st.subheader("Acesso Restrito")
        user = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")
        if st.button("Entrar"):
            if user == "admin" and senha == "glab2026":
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.error("Login inválido.")
    else:
        st.title("Painel de Controle")
        df_atual = carregar_estoque()
        
        # REGISTRAR VENDA COM BAIXA NO ESTOQUE
        st.subheader("Registrar Venda (Baixa Automática)")
        prod_venda = st.selectbox("Selecione o produto vendido", df_atual['PRODUTO'].unique())
        qtd_venda = st.number_input("Quantidade", min_value=1, value=1)
        
        if st.button("Confirmar Venda"):
            idx = df_atual.index[df_atual['PRODUTO'] == prod_venda].tolist()[0]
            if df_atual.at[idx, 'QTD'] >= qtd_venda:
                df_atual.at[idx, 'QTD'] -= qtd_venda
                df_atual.to_excel('stock_0202 - NOVA.xlsx', index=False)
                st.success(f"Venda de {prod_venda} registrada com sucesso!")
                st.rerun()
            else:
                st.error("Estoque insuficiente!")

        st.divider()
        st.subheader("Edição Manual da Planilha")
        df_editado = st.data_editor(df_atual, use_container_width=True, hide_index=True)
        if st.button("Salvar Tabela Completa"):
            df_editado.to_excel('stock_0202 - NOVA.xlsx', index=False)
            st.success("Tabela salva!")

        if st.button("Sair"):
            st.session_state.autenticado = False
            st.rerun()
