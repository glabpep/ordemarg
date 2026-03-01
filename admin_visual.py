import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import os
import json

# --- 1. CONFIGURAÇÃO (OCULTA STREAMLIT) ---
st.set_page_config(page_title="G-LAB", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
        /* Esconde elementos do Streamlit */
        header, footer, #MainMenu, .stDeployButton, [data-testid="stHeader"] { visibility: hidden; display: none; }
        .block-container { padding: 0px; max-width: 100%; }
        /* Botões de navegação superiores */
        .stButton button { border-radius: 0px; height: 45px; font-weight: bold; border: none; }
    </style>
""", unsafe_allow_html=True)

if "aba" not in st.session_state: st.session_state.aba = "LOJA"
if "auth" not in st.session_state: st.session_state.auth = False

# Menu de alternância (Visível apenas para você gerenciar)
c1, c2 = st.columns(2)
with c1: 
    if st.button("🛒 VER LOJA", use_container_width=True): st.session_state.aba = "LOJA"
with c2: 
    if st.button("🔐 ADMIN", use_container_width=True): st.session_state.aba = "ADMIN"

# --- 2. BANCO DE DADOS ---
def get_data():
    path = 'stock_0202 - NOVA.xlsx'
    if os.path.exists(path):
        df = pd.read_excel(path)
        df.columns = [str(c).strip() for c in df.columns]
        return df, path
    return pd.DataFrame(), None

# --- 3. LOGICA DA LOJA ---
if st.session_state.aba == "LOJA":
    df_estoque, _ = get_data()
    produtos_lista = []
    
    for _, r in df_estoque.iterrows():
        nome_prod = str(r.get('PRODUTO', '')).strip()
        # Link Raw do GitHub (Maiúsculas)
        img_url = f"https://raw.githubusercontent.com/glabpep/ordem/main/{nome_prod.replace(' ', '%20').upper()}.webp"
        
        produtos_lista.append({
            "nome": nome_prod,
            "espec": f"{r.get('VOLUME','')} {r.get('MEDIDA','')}",
            "preco": float(r.get('Preço (R$)', 0)),
            "qtd": int(r.get('QTD', 0)) if pd.notna(r.get('QTD')) else 0,
            "status": str(r.get('ESTOQUE', '')).upper(),
            "img": img_url
        })

    if os.path.exists('index.html'):
        with open('index.html', 'r', encoding='utf-8') as f:
            html_base = f.read()
        
        # INJEÇÃO DE CSS E JS PARA CARRINHO FIXO E MINIMIZÁVEL
        injecao_frontend = f"""
        <style>
            /* FORÇA O CARRINHO A FICAR FIXO E SEMPRE NO TOPO VISUAL */
            #cart-bar {{
                position: fixed !important;
                bottom: 0 !important;
                left: 0 !important;
                right: 0 !important;
                z-index: 1000000 !important;
                background: var(--primary, #004a99) !important;
                box-shadow: 0 -5px 25px rgba(0,0,0,0.4) !important;
                transition: transform 0.3s ease-in-out !important;
                padding: 15px !important;
                display: block !important;
            }}
            .cart-minimized {{ transform: translateY(75%); }}
            .btn-toggle-cart {{
                position: absolute; top: -35px; right: 20px;
                background: #004a99; color: white; border: none;
                padding: 8px 15px; border-radius: 12px 12px 0 0;
                font-weight: bold; cursor: pointer; font-size: 14px;
            }}
        </style>
        <script>
            window.produtosBase = {json.dumps(produtos_lista)};
            
            function toggleMinCart() {{
                const bar = document.getElementById('cart-bar');
                bar.classList.toggle('cart-minimized');
                document.getElementById('icon-min').innerText = bar.classList.contains('cart-minimized') ? '▲ ABRIR' : '▼ FECHAR';
            }}

            window.addEventListener('load', function() {{
                const bar = document.getElementById('cart-bar');
                if(bar) {{
                    const btn = document.createElement('button');
                    btn.className = 'btn-toggle-cart';
                    btn.innerHTML = '<span id="icon-min">▼ FECHAR</span>';
                    btn.onclick = toggleMinCart;
                    bar.appendChild(btn);
                }}
                // Força a renderização do seu script original
                if(typeof renderizarProdutos === 'function') renderizarProdutos();
            }});
        </script>
        """
        # Adiciona a injeção antes do fim do head para garantir prioridade de CSS
        html_final = html_base.replace("</head>", f"{injecao_frontend}</head>")
        components.html(html_final, height=2000, scrolling=True)
    else:
        st.error("Arquivo index.html não encontrado!")

# --- 4. LOGICA DO ADMIN ---
else:
    if not st.session_state.auth:
        st.subheader("Acesso Restrito")
        u = st.text_input("Usuário")
        p = st.text_input("Senha", type="password")
        if st.button("LOGAR"):
            if u == "admin" and p == "glab2026":
                st.session_state.auth = True
                st.rerun()
    else:
        st.title("⚙️ Gestão G-LAB")
        df_adm, path_adm = get_data()

        # REGISTRAR VENDA COM BAIXA AUTOMÁTICA
        with st.container(border=True):
            st.subheader("📝 Registrar Venda")
            p_venda = st.selectbox("Produto", df_adm['PRODUTO'].unique())
            q_venda = st.number_input("Quantidade", min_value=1, value=1)
            if st.button("DAR BAIXA NO ESTOQUE"):
                idx = df_adm.index[df_adm['PRODUTO'] == p_venda].tolist()[0]
                if df_adm.at[idx, 'QTD'] >= q_venda:
                    df_adm.at[idx, 'QTD'] -= q_venda
                    df_adm.to_excel(path_adm, index=False)
                    st.success("Venda registrada e estoque atualizado!")
                    st.rerun()
                else:
                    st.error("Estoque insuficiente!")

        st.divider()
        st.subheader("📊 Tabela Geral do Excel")
        df_edit = st.data_editor(df_adm, hide_index=True, use_container_width=True)
        if st.button("💾 SALVAR ALTERAÇÕES MANUAIS"):
            df_edit.to_excel(path_adm, index=False)
            st.success("Excel salvo!")
        
        if st.button("Sair"):
            st.session_state.auth = False
            st.rerun()
