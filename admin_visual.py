import streamlit as st
import pandas as pd
import os
from datetime import datetime
import json

# Importa a função do seu arquivo estoque.py (certifique-se que o nome do arquivo seja estoque.py)
try:
    from estoque import gerar_site_vendas_completo
except ImportError:
    # Caso o arquivo tenha outro nome, ajuste aqui ou manteremos a função interna
    st.error("Arquivo estoque.py não encontrado. Certifique-se que o nome está correto.")

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="G-LAB - Gestão de Estoque", layout="wide", page_icon="🧪")

# --- SISTEMA DE LOGIN ---
def verificar_login():
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False

    if not st.session_state.autenticado:
        st.title("🔐 Acesso Restrito G-LAB")
        with st.form("login"):
            usuario = st.text_input("Usuário")
            senha = st.text_input("Senha", type="password")
            if st.form_submit_button("Entrar"):
                if usuario == "admin" and senha == "glab2026": # <--- MUDE SUA SENHA AQUI
                    st.session_state.autenticado = True
                    st.rerun()
                else:
                    st.error("Usuário ou senha incorretos")
        return False
    return True

def localizar_planilha():
    diretorio_atual = os.path.dirname(os.path.abspath(__file__))
    for nome in ['stock_0202 - NOVA.xlsx', 'stock_2901.xlsx']:
        caminho = os.path.join(diretorio_atual, nome)
        if os.path.exists(caminho):
            return caminho
    return None

def main():
    if not verificar_login():
        return

    st.sidebar.image("1.png", width=150) # Tenta carregar sua logo na lateral
    st.sidebar.title("Menu")
    
    caminho_planilha = localizar_planilha()
    if not caminho_planilha:
        st.error("Planilha de estoque não encontrada!")
        return

    # Carregamento de dados com correção para o erro de conversão '5000ui'
    df = pd.read_excel(caminho_planilha)
    for col in ['VOLUME', 'MEDIDA', 'PRODUTO']:
        if col in df.columns:
            df[col] = df[col].astype(str)

    st.title("🧪 Painel de Controle G-LAB")

    tab1, tab2, tab3 = st.tabs(["📊 Estoque Atual", "💰 Registrar Venda", "📜 Histórico"])

    with tab1:
        st.subheader("Situação do Inventário")
        # Correção do aviso de depreciação: width='stretch' ou valor numérico
        st.dataframe(df.style.highlight_between(left=0, right=0, color='#ffcccc', subset=['QTD']), use_container_width=True)
        
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
            valor = st.number_input("Valor Total (R$)", min_value=0.0)
            pgto = st.selectbox("Pagamento", ["PIX", "CARTÃO", "OUTRO"])
            
            if st.form_submit_button("Confirmar e Abater"):
                idx = df[df['PRODUTO'] == prod].index[0]
                if df.at[idx, 'QTD'] >= qtd:
                    df.at[idx, 'QTD'] -= qtd
                    
                    # Salvar na planilha
                    with pd.ExcelWriter(caminho_planilha, engine='openpyxl') as writer:
                        df.to_excel(writer, sheet_name='ESTOQUE', index=False)
                        # Log de vendas simples
                        venda = {"DATA": datetime.now().strftime("%d/%m/%Y %H:%M"), "CLIENTE": cliente, "PRODUTO": prod, "QTD": qtd, "VALOR": valor, "PGTO": pgto}
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

    with tab3:
        try:
            df_pedidos = pd.read_excel(caminho_planilha, sheet_name='PEDIDOS_PAGOS')
            st.dataframe(df_pedidos, use_container_width=True)
        except:
            st.info("Nenhum histórico de vendas encontrado.")

    if st.sidebar.button("Sair"):
        st.session_state.autenticado = False
        st.rerun()

if __name__ == "__main__":
    main()
