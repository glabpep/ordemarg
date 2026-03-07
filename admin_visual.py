
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import os
import json

# --- 1. CONFIGURAÇÃO DE INTERFACE (OCULTA STREAMLIT) ---
st.set_page_config(page_title="G-LAB", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
        header, footer, #MainMenu, .stDeployButton, [data-testid="stHeader"] { visibility: hidden; display: none; }
        .block-container { padding: 0px; max-width: 100%; }
        .nav-admin { display: flex; background: #004a99; }
        .nav-admin button { flex: 1; height: 50px; background: #004a99; color: white; border: 1px solid #003366; font-weight: bold; cursor: pointer; }
    </style>
""", unsafe_allow_html=True)

if "aba" not in st.session_state: st.session_state.aba = "LOJA"
if "auth" not in st.session_state: st.session_state.auth = False

# Menu de navegação superior (Só você vê no admin)
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

# --- 3. RENDERIZAÇÃO DA LOJA ---
if st.session_state.aba == "LOJA":
    df_estoque, _ = get_data()
    produtos_lista = []
    
    for _, r in df_estoque.iterrows():
        n = str(r.get('PRODUTO', '')).strip()
        # Link RAW GitHub (Força Maiúsculas para evitar erro de imagem)
        img = f"https://raw.githubusercontent.com/glabpep/ordem/main/{n.replace(' ', '%20').upper()}.webp"
        produtos_lista.append({
            "nome": n,
            "espec": f"{r.get('VOLUME','')} {r.get('MEDIDA','')}",
            "preco": float(r.get('Preço (R$)', 0)),
            "qtd": int(r.get('QTD', 0)) if pd.notna(r.get('QTD')) else 0,
            "img": img
        })

    if os.path.exists('index.html'):
        with open('index.html', 'r', encoding='utf-8') as f:
            html = f.read()
        

        # INJEÇÃO DE CSS PARA FIXAR O CARRINHO E ADICIONAR MINIMIZADOR
        injecao = f"""
        <style>
            /* FORÇA O CARRINHO A SER FIXO NO RODAPÉ, INDEPENDENTE DA ROLAGEM */
            #cart-bar {{
                position: fixed !important;
                bottom: 0 !important;
                left: 50% !important;
                transform: translateX(-50%) !important;
                width: 100% !important;
                max-width: 900px !important; /* Mesma largura do seu container */
                z-index: 2147483647 !important; /* Máximo possível */
                background: #004a99 !important;
                box-shadow: 0 -10px 30px rgba(0,0,0,0.5) !important;
                padding-top: 35px !important;
                transition: bottom 0.3s ease !important;
            }}
            
            .cart-escondido {{
                bottom: -150px !important;
            }}
=======
        if st.button("🔄 Sincronizar com o Site (Gerar index.html)"):
            with st.spinner("Atualizando site..."):
                try:
                    gerar_site_vendas_completo()
                    st.success("✅ Site index.html atualizado com sucesso!")
                except Exception as e:
                    st.error(f"Erro ao gerar site: {e}")

    with tab2:
        st.subheader("Nova Baixa de Estoque")
        with st.form("venda_form"):
            prod = st.selectbox("Produto", df['PRODUTO'].unique())
            qtd = st.number_input("Quantidade", min_value=1, step=1)
            cliente = st.text_input("Nome do Cliente").upper()
            
            # Ajuste solicitado: Rótulo agora indica USD e valor é dividido por 5.5
            valor_original = st.number_input("Valor Original (R$)", min_value=0.0)
            valor_convertido = valor_original / 5.5
            st.info(f"Valor convertido para o sistema: $ {valor_convertido:.2f}")
            
            pgto = st.selectbox("Pagamento", ["PIX", "CARTÃO", "OUTRO"])
            
            if st.form_submit_button("Confirmar e Abater"):
                idx = df[df['PRODUTO'] == prod].index[0]
                if df.at[idx, 'QTD'] >= qtd:
                    df.at[idx, 'QTD'] -= qtd
                    
                    # Salvar na planilha
                    with pd.ExcelWriter(caminho_planilha, engine='openpyxl') as writer:
                        df.to_excel(writer, sheet_name='ESTOQUE', index=False)
                        # Log de vendas com o valor em Dólar
                        venda = {
                            "DATA": datetime.now().strftime("%d/%m/%Y %H:%M"), 
                            "CLIENTE": cliente, 
                            "PRODUTO": prod, 
                            "QTD": qtd, 
                            "VALOR_USD": round(valor_convertido, 2), 
                            "PGTO": pgto
                        }
                        try:
                            df_hist = pd.read_excel(caminho_planilha, sheet_name='PEDIDOS_PAGOS')
                            df_hist = pd.concat([df_hist, pd.DataFrame([venda])], ignore_index=True)
                        except:
                            df_hist = pd.DataFrame([venda])
                        df_hist.to_excel(writer, sheet_name='PEDIDOS_PAGOS', index=False)
                    
                    st.success("Estoque atualizado!")
                    # Auto-atualiza o site após a venda
                    gerar_site_vendas_completo()
                    st.info("O site index.html também foi atualizado automaticamente.")
                    st.rerun()
                else:
                    st.error("Estoque insuficiente!")


            .btn-min-cart {{
                position: absolute;
                top: 0;
                right: 20px;
                background: #ffcc00;
                color: #000;
                border: none;
                padding: 5px 15px;
                border-radius: 0 0 10px 10px;
                font-weight: bold;
                font-size: 12px;
                cursor: pointer;
            }}
        </style>
        <script>
            window.produtosBase = {json.dumps(produtos_lista)};
            
            function toggleCarrinho() {{
                const bar = document.getElementById('cart-bar');
                const btn = document.getElementById('btn-min-txt');
                if(bar.classList.contains('cart-escondido')) {{
                    bar.classList.remove('cart-escondido');
                    btn.innerText = 'MINIMIZAR';
                }} else {{
                    bar.classList.add('cart-escondido');
                    btn.innerText = 'ABRIR CARRINHO';
                }}
            }}

            window.addEventListener('load', function() {{
                const bar = document.getElementById('cart-bar');
                if(bar) {{
                    // Cria o botão de minimizar dinamicamente
                    const btn = document.createElement('button');
                    btn.className = 'btn-min-cart';
                    btn.innerHTML = '<span id="btn-min-txt">MINIMIZAR</span>';
                    btn.onclick = toggleCarrinho;
                    bar.appendChild(btn);
                }}
                if(typeof renderizarProdutos === 'function') renderizarProdutos();
            }});
        </script>
        """
        html_final = html.replace("</head>", f"{injecao}</head>")
        components.html(html_final, height=1500, scrolling=True)
    else:
        st.error("index.html não encontrado!")


# --- 4. ÁREA ADMIN ---
else:
    if not st.session_state.auth:
        u = st.text_input("Usuário")
        p = st.text_input("Senha", type="password")
        if st.button("LOGAR"):
            if u == "admin" and p == "glab2026":
                st.session_state.auth = True
                st.rerun()
    else:
        st.title("⚙️ Painel de Controle")
        df_adm, p_adm = get_data()

        # Baixa de estoque
        with st.expander("📝 REGISTRAR VENDA", expanded=True):
            p_venda = st.selectbox("Produto", df_adm['PRODUTO'].unique())
            q_venda = st.number_input("Qtd", min_value=1, value=1)
            if st.button("CONFIRMAR VENDA"):
                idx = df_adm.index[df_adm['PRODUTO'] == p_venda].tolist()[0]
                df_adm.at[idx, 'QTD'] -= q_venda
                df_adm.to_excel(p_adm, index=False)
                st.success("Venda registrada!")
                st.rerun()

        st.divider()
        df_edit = st.data_editor(df_adm, hide_index=True, use_container_width=True)
        if st.button("💾 SALVAR TUDO"):
            df_edit.to_excel(p_adm, index=False)
            st.success("Excel atualizado!")
        
        if st.button("Sair"):
            st.session_state.auth = False
            st.rerun()

if __name__ == "__main__":
    main()
>>>>>>> a791027 (Atualizando estoque e removendo CEP)



