import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import os
import json

# --- 1. CONFIGURAÇÃO E OCULTAÇÃO TOTAL DO STREAMLIT ---
st.set_page_config(page_title="G-LAB", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
        /* Remove barras e menus do Streamlit */
        header, footer, #MainMenu, .stDeployButton, [data-testid="stHeader"] { visibility: hidden; display: none; }
        .block-container { padding: 0px; max-width: 100%; }
        
        /* Menu de Navegação Superior Fixo (Para você alternar) */
        .admin-nav {
            position: fixed; top: 0; left: 0; right: 0; height: 40px;
            background: rgba(0, 74, 153, 0.05); z-index: 100000;
            display: flex; justify-content: center; align-items: center; gap: 20px;
        }
        .stButton button { border-radius: 0px; height: 40px; border: none; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

if "aba" not in st.session_state: st.session_state.aba = "LOJA"
if "auth" not in st.session_state: st.session_state.auth = False

# Botoes de navegação discretos no topo
c1, c2 = st.columns(2)
with c1: 
    if st.button("🛒 IR PARA LOJA", use_container_width=True): st.session_state.aba = "LOJA"
with c2: 
    if st.button("🔐 PAINEL ADMIN", use_container_width=True): st.session_state.aba = "ADMIN"

# --- 2. BANCO DE DADOS ---
def get_data():
    path = 'stock_0202 - NOVA.xlsx'
    if os.path.exists(path):
        df = pd.read_excel(path)
        df.columns = [str(c).strip() for c in df.columns]
        return df, path
    return pd.DataFrame(), None

# --- 3. INTERFACE LOJA (COM CARRINHO FIXO E MINIMIZÁVEL) ---
if st.session_state.aba == "LOJA":
    df, _ = get_data()
    prods = []
    for _, r in df.iterrows():
        n = str(r.get('PRODUTO', '')).strip()
        # Link RAW do GitHub (Maiúsculas)
        img = f"https://raw.githubusercontent.com/glabpep/ordem/main/{n.replace(' ', '%20').upper()}.webp"
        prods.append({
            "nome": n, "espec": f"{r.get('VOLUME','')} {r.get('MEDIDA','')}",
            "preco": float(r.get('Preço (R$)', 0)), "qtd": int(r.get('QTD', 0)), "img": img
        })

    if os.path.exists('index.html'):
        with open('index.html', 'r', encoding='utf-8') as f:
            html = f.read()
        
        # INJEÇÃO DE CSS PARA O CARRINHO E DADOS
        # Aqui forçamos o carrinho a ser FIXO, acompanhar a rolagem e ter botão de minimizar
        injection = f"""
        <style>
            /* FORÇAR CARRINHO FIXO E FLUTUANTE */
            #cart-bar {{ 
                position: fixed !important; 
                bottom: 0 !important; 
                left: 0 !important; 
                right: 0 !important; 
                z-index: 999999 !important; 
                background: #004a99 !important;
                box-shadow: 0 -5px 20px rgba(0,0,0,0.3) !important;
                display: block !important;
                transition: transform 0.3s ease;
            }}
            .cart-minimized {{ transform: translateY(80%); }}
            .btn-min {{ 
                position: absolute; top: -30px; right: 20px; 
                background: #004a99; color: white; border: none; 
                padding: 5px 15px; border-radius: 10px 10px 0 0; font-weight: bold;
            }}
        </style>
        <script>
            window.produtosBase = {json.dumps(prods)};
            
            // Função para Minimizar/Maximizar
            function toggleCart() {{
                const bar = document.getElementById('cart-bar');
                bar.classList.toggle('cart-minimized');
                document.getElementById('btn-min-txt').innerText = bar.classList.contains('cart-minimized') ? '▲' : '▼';
            }}

            window.addEventListener('load', function() {{
                // Adiciona botão de minimizar no carrinho
                const bar = document.getElementById('cart-bar');
                if(bar) {{
                    const btn = document.createElement('button');
                    btn.className = 'btn-min';
                    btn.innerHTML = '<span id="btn-min-txt">▼</span>';
                    btn.onclick = toggleCart;
                    bar.appendChild(btn);
                }}
                if(typeof renderizarProdutos === 'function') renderizarProdutos();
            }});
        </script>
        """
        html_final = html.replace("</head>", f"{injection}</head>")
        components.html(html_final, height=2000, scrolling=True)
    else:
        st.error("Arquivo index.html não encontrado!")

# --- 4. PAINEL ADMIN ---
else:
    if not st.session_state.auth:
        u = st.text_input("User")
        p = st.text_input("Pass", type="password")
        if st.button("Entrar"):
            if u == "admin" and p == "glab2026":
                st.session_state.auth = True
                st.rerun()
    else:
        st.title("📦 Gestão de Vendas")
        df_admin, path_admin = get_data()

        # Registrar Venda Rapida
        with st.expander("📝 REGISTRAR NOVA VENDA (BAIXA AUTOMÁTICA)", expanded=True):
            p_sel = st.selectbox("Produto", df_admin['PRODUTO'].unique())
            q_sel = st.number_input("Quantidade", min_value=1, value=1)
            if st.button("BAIXAR ESTOQUE"):
                idx = df_admin.index[df_admin['PRODUTO'] == p_sel].tolist()[0]
                df_admin.at[idx, 'QTD'] -= q_sel
                df_admin.to_excel(path_admin, index=False)
                st.success("Estoque Atualizado!")
                st.rerun()

        st.divider()
        df_edit = st.data_editor(df_admin, hide_index=True, use_container_width=True)
        if st.button("💾 SALVAR TUDO"):
            df_edit.to_excel(path_admin, index=False)
            st.success("Excel salvo!")
        
        if st.button("Sair"):
            st.session_state.auth = False
            st.rerun()
