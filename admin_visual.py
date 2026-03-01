import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import os
import json

# --- 1. CONFIGURAÇÃO E OCULTAÇÃO TOTAL DO STREAMLIT ---
st.set_page_config(page_title="G-LAB", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
        /* Remove tudo do Streamlit */
        header {visibility: hidden;}
        footer {visibility: hidden;}
        #MainMenu {visibility: hidden;}
        .stDeployButton {display:none;}
        [data-testid="stHeader"] {display:none;}
        .block-container {padding: 0px; max-width: 100%;}
        
        /* Menu de Navegação customizado e discreto */
        .nav-container {
            display: flex; justify-content: center; gap: 10px;
            background: #004a99; padding: 10px; position: sticky; top: 0; z-index: 9999;
        }
        .nav-btn {
            background: #fff; color: #004a99; border: none; padding: 5px 15px;
            border-radius: 5px; font-weight: bold; cursor: pointer; text-decoration: none;
        }
    </style>
""", unsafe_allow_html=True)

if "aba_atual" not in st.session_state:
    st.session_state.aba_atual = "🛒 LOJA"
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

# --- 2. MENU DE NAVEGAÇÃO INTERNO ---
col1, col2 = st.columns(2)
with col1:
    if st.button("🛒 ACESSAR LOJA", use_container_width=True):
        st.session_state.aba_atual = "🛒 LOJA"
with col2:
    if st.button("🔐 ÁREA ADMIN", use_container_width=True):
        st.session_state.aba_atual = "🔐 ADMIN"

# --- 3. LOGICA DE DADOS ---
def carregar_dados():
    caminho = 'stock_0202 - NOVA.xlsx'
    if os.path.exists(caminho):
        df = pd.read_excel(caminho)
        df.columns = [str(col).strip() for col in df.columns]
        return df
    return pd.DataFrame()

# --- 4. RENDERIZAÇÃO DA LOJA ---
if st.session_state.aba_atual == "🛒 LOJA":
    df = carregar_dados()
    produtos_json = []
    
    for _, row in df.iterrows():
        nome = str(row.get('PRODUTO', '')).strip()
        # Link RAW GitHub Forçado em MAIÚSCULAS
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
        
        # Injeta os dados e força o JS do carrinho a acordar
        injecao = f"""
        <script>
            window.produtosBase = {json.dumps(produtos_json)};
            window.addEventListener('load', function() {{
                if(typeof renderizarProdutos === 'function') renderizarProdutos();
            }});
        </script>
        """
        html_final = html.replace("</head>", f"{injecao}</head>")
        components.html(html_final, height=1200, scrolling=True)
    else:
        st.error("index.html não encontrado!")

# --- 5. ÁREA ADMINISTRATIVA ---
else:
    if not st.session_state.autenticado:
        st.subheader("Login Administrativo")
        u = st.text_input("Usuário")
        p = st.text_input("Senha", type="password")
        if st.button("ENTRAR"):
            if u == "admin" and p == "glab2026":
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.error("Acesso negado")
    else:
        st.title("⚙️ Painel de Controle G-LAB")
        df_admin = carregar_dados()

        # BAIXA DE ESTOQUE
        st.subheader("📝 Registrar Venda Rapida")
        p_venda = st.selectbox("Selecione o produto", df_admin['PRODUTO'].unique())
        q_venda = st.number_input("Qtd vendida", min_value=1, value=1)
        if st.button("Confirmar Baixa"):
            idx = df_admin.index[df_admin['PRODUTO'] == p_venda].tolist()[0]
            if df_admin.at[idx, 'QTD'] >= q_venda:
                df_admin.at[idx, 'QTD'] -= q_venda
                df_admin.to_excel('stock_0202 - NOVA.xlsx', index=False)
                st.success("Venda registrada!")
                st.rerun()
            else:
                st.error("Estoque insuficiente!")

        st.divider()
        # EDIÇÃO DA TABELA
        df_edit = st.data_editor(df_admin, hide_index=True, use_container_width=True)
        if st.button("💾 Salvar Alterações na Planilha"):
            df_edit.to_excel('stock_0202 - NOVA.xlsx', index=False)
            st.success("Tabela atualizada!")
        
        if st.button("Sair"):
            st.session_state.autenticado = False
            st.rerun()
