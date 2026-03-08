import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import os
import json
from datetime import datetime
# Importamos a função do seu arquivo admin.py reescrito
from admin import gerar_site_vendas_completo

# --- 1. CONFIGURAÇÃO DE INTERFACE (OCULTA STREAMLIT) ---
st.set_page_config(page_title="G-LAB PEPTIDES ADMIN", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
        header, footer, #MainMenu, .stDeployButton, [data-testid="stHeader"] { visibility: hidden; display: none; }
        .block-container { padding: 0px; max-width: 100%; }
        .stButton button { border-radius: 8px; font-weight: bold; }
        .nav-admin { display: flex; background: #004a99; padding: 10px; gap: 10px; }
    </style>
""", unsafe_allow_html=True)

if "aba" not in st.session_state: st.session_state.aba = "LOJA"
if "auth" not in st.session_state: st.session_state.auth = False

# Menu de navegação superior
c1, c2 = st.columns(2)
with c1: 
    if st.button("🛒 VER LOJA (PÚBLICO)", use_container_width=True): st.session_state.aba = "LOJA"
with c2: 
    if st.button("🔐 PAINEL ADMIN", use_container_width=True): st.session_state.aba = "ADMIN"

# --- 2. FUNÇÕES DE DADOS ---
def get_data():
    # Prioriza o arquivo mais recente conforme lógica do admin.py
    for nome in ['stock_0202 - NOVA.xlsx', 'stock_0202.xlsx']:
        if os.path.exists(nome):
            df = pd.read_excel(nome)
            df.columns = [str(c).strip() for c in df.columns]
            return df, nome
    return pd.DataFrame(), None

# --- 3. RENDERIZAÇÃO DA LOJA (VIEWER) ---
if st.session_state.aba == "LOJA":
    df_estoque, _ = get_data()
    
    if os.path.exists('index.html'):
        with open('index.html', 'r', encoding='utf-8') as f:
            html_content = f.read()

        # Injeção de CSS para o comportamento do carrinho e Botão Minimizar
        injecao_js_css = """
        <style>
            #cart-panel {
                position: fixed !important;
                bottom: 0 !important;
                left: 50% !important;
                transform: translateX(-50%) !important;
                width: 100% !important;
                max-width: 900px !important;
                z-index: 999999 !important;
                transition: bottom 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
            }
            .cart-escondido {
                bottom: -220px !important; /* Esconde mas deixa a ponta ou botão */
            }
            .btn-min-cart {
                position: absolute;
                top: -35px;
                right: 20px;
                background: #ffc107;
                color: #000;
                border: none;
                padding: 8px 15px;
                border-radius: 10px 10px 0 0;
                font-weight: bold;
                font-size: 12px;
                cursor: pointer;
                box-shadow: 0 -5px 10px rgba(0,0,0,0.2);
            }
        </style>
        <script>
            function toggleCarrinho() {
                const panel = document.getElementById('cart-panel');
                const btnTxt = document.getElementById('btn-min-txt');
                if(panel.classList.contains('cart-escondido')) {
                    panel.classList.remove('cart-escondido');
                    btnTxt.innerText = 'MINIMIZAR';
                } else {
                    panel.classList.add('cart-escondido');
                    btnTxt.innerText = 'ABRIR PEDIDO';
                }
            }

            window.addEventListener('DOMContentLoaded', (event) => {
                const panel = document.getElementById('cart-panel');
                if(panel) {
                    const btn = document.createElement('button');
                    btn.className = 'btn-min-cart';
                    btn.innerHTML = '<span id="btn-min-txt">MINIMIZAR</span>';
                    btn.onclick = toggleCarrinho;
                    panel.appendChild(btn);
                }
            });
        </script>
        """
        html_final = html_content.replace("</head>", f"{injecao_js_css}</head>")
        components.html(html_final, height=1200, scrolling=True)
    else:
        st.warning("⚠️ El archivo 'index.html' no foi encontrado. Vá ao ADMIN e clique em 'Sincronizar Site'.")

# --- 4. ÁREA ADMIN (CONTROLE) ---
else:
    if not st.session_state.auth:
        st.markdown("<h2 style='text-align:center;'>Acesso Restrito</h2>", unsafe_allow_html=True)
        col_l, col_c, col_r = st.columns([1,2,1])
        with col_c:
            u = st.text_input("Usuário")
            p = st.text_input("Senha", type="password")
            if st.button("ENTRAR NO PAINEL", use_container_width=True):
                if u == "admin" and p == "glab2026":
                    st.session_state.auth = True
                    st.rerun()
                else:
                    st.error("Credenciais inválidas")
    else:
        st.title("⚙️ Gestão de Estoque e Vendas")
        df, caminho_planilha = get_data()

        if df.empty:
            st.error("Não foi possível carregar a planilha de estoque.")
            st.stop()

        tab1 , tab2 = st.tabs(["📊 ESTOQUE ATUAL", "📝 NOVA BAIXA"])

        with tab1:
            st.subheader("Editor de Produtos")
            df_editado = st.data_editor(df, hide_index=True, use_container_width=True)
            

        with tab2:
            st.subheader("Registrar Venda (Baixa Direta)")
            with st.form("venda_form"):
                col_v1, col_v2 = st.columns(2)
                with col_v1:
                    prod = st.selectbox("Selecione o Produto", df['PRODUTO'].unique())
                    qtd = st.number_input("Quantidade", min_value=1, step=1)
                    cliente = st.text_input("Nome do Cliente").upper()
                
                with col_v2:
                    # Lógica solicitada: Entrada em R$ e conversão para USD
                    valor_reais = st.number_input("Valor da Venda (U$)", min_value=0.0)
                    valor_usd = valor_reais
                    st.info(f"Valor em Dólar: U$ {valor_usd:.2f}")
                    pgto = st.selectbox("Método de Pago", ["TRANSFERENCIA", "CRIPTOMONEDAS", "TARJETA", "EFECTIVO"])
                
                if st.form_submit_button("CONFIRMAR E ABATER ESTOQUE"):
                    idx = df[df['PRODUTO'] == prod].index[0]
                    if df.at[idx, 'QTD'] >= qtd:
                        # 1. Abate no DataFrame
                        df.at[idx, 'QTD'] -= qtd
                        
                        # 2. Salva Planilha com Histórico
                        with pd.ExcelWriter(caminho_planilha, engine='openpyxl') as writer:
                            df.to_excel(writer, sheet_name='ESTOQUE', index=False)
                            
                            venda_log = {
                                "DATA": datetime.now().strftime("%d/%m/%Y %H:%M"),
                                "CLIENTE": cliente,
                                "PRODUTO": prod,
                                "QTD": qtd,
                                "VALOR_USD": round(valor_usd, 2),
                                "PGTO": pgto
                            }
                            
                            try:
                                df_hist = pd.read_excel(caminho_planilha, sheet_name='PEDIDOS_PAGOS')
                                df_hist = pd.concat([df_hist, pd.DataFrame([venda_log])], ignore_index=True)
                            except:
                                df_hist = pd.DataFrame([venda_log])
                            
                            df_hist.to_excel(writer, sheet_name='PEDIDOS_PAGOS', index=False)
                        
                        st.success(f"Venda de {prod} registrada!")
                        # 3. Sincroniza o site automaticamente
                        gerar_site_vendas_completo()
                        st.rerun()
                    else:
                        st.error("Erro: Quantidade em estoque insuficiente!")

        

        if st.sidebar.button("Logoff"):
            st.session_state.auth = False
            st.rerun()

if __name__ == "__main__":
    pass # Streamlit roda o script diretamente








