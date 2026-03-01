import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import os
import json

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="G-LAB PEPTIDES - Admin", layout="wide", page_icon="🧪")

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

# CSS para esconder elementos desnecessários do Streamlit
st.markdown("""
    <style>
        .block-container { padding: 0rem; max-width: 100%; }
        footer {visibility: hidden;}
        header {visibility: hidden;}
        [data-testid="stSidebar"] { background-color: #f8f9fa; }
    </style>
""", unsafe_allow_html=True)

# --- 2. FUNÇÕES DE BANCO DE DADOS (EXCEL) ---
def carregar_dados():
    caminho = 'stock_0202 - NOVA.xlsx'
    if os.path.exists(caminho):
        df = pd.read_excel(caminho)
        df.columns = [str(col).strip() for col in df.columns]
        return df
    return pd.DataFrame()

def salvar_dados(df):
    df.to_excel('stock_0202 - NOVA.xlsx', index=False)

# --- 3. LOGICA DE INFORMAÇÕES TÉCNICAS ---
INFOS_TECNICAS = {
    "5-AMINO": "Inibidor Seletivo de NNMT: Atua bloqueando a enzima nicotinamida N-metiltransferase.",
    "AICAR": "Ativador de AMPK: Melhora a captação de glicose e oxidação de gordura.",
    "AOD 9604": "Análogo Lipolítico do hGH: Focado na queima de gordura sem efeitos glicêmicos.",
    "BPC-157": "Peptídeo Regenerativo: Alta eficácia na cicatrização de tecidos e tendões.",
    "CJC-1295": "Análogo de GHRH: Estimula a liberação natural de GH.",
    "GHK-CU": "Peptídeo de Cobre: Síntese de colágeno e anti-inflamatório.",
    "IPAMORELIN": "Agonista de Grelina: Estimula GH de forma seletiva.",
    "MELANOTAN": "Análogo de MSH: Bronzeamento e melhora da libido.",
    "TB-500": "Timosina Beta-4: Reparo celular e angiogênese.",
    "MK-677": "Secretagogo de GH Oral: Aumenta IGF-1 e GH."
}

# --- 4. PREPARAÇÃO DO HTML DINÂMICO ---
def preparar_html():
    df = carregar_dados()
    produtos_lista = []
    
    for _, row in df.iterrows():
        nome = str(row.get('PRODUTO', '')).strip()
        nome_up = nome.upper()
        
        # Busca descrição técnica
        desc = "Informações técnicas em atualização para este peptídeo."
        for chave, texto in INFOS_TECNICAS.items():
            if chave in nome_up:
                desc = texto
                break
        
        produtos_lista.append({
            "nome": nome,
            "espec": f"{row.get('VOLUME', '')} {row.get('MEDIDA', '')}",
            "preco": float(row.get('Preço (R$)', 0)),
            "estoque": str(row.get('ESTOQUE', 'EM ESPERA')).upper(),
            "qtd": int(row.get('QTD', 0)) if pd.notna(row.get('QTD')) else 0,
            "desc_longa": desc,
            "img": f"https://raw.githubusercontent.com/glabpep/ordem/main/{nome.replace(' ', '%20').upper()}.webp"
        })

    # Lê o seu index.html físico
    if os.path.exists('index.html'):
        with open('index.html', 'r', encoding='utf-8') as f:
            html_base = f.read()
    else:
        return "<h1>Erro: index.html não encontrado!</h1>"

    # INJEÇÃO DE BACKEND NO JAVASCRIPT
    script_fix = f"""
    <script>
        // Sobrescreve os dados do Front com os do Excel (Backend)
        window.produtosBase = {json.dumps(produtos_lista)};
        
        // CORREÇÃO DAS IMAGENS E INFOS
        function verMais(nome) {{
            const p = window.produtosBase.find(x => x.nome === nome);
            if(p) {{
                alert(p.nome + "\\n\\n" + p.desc_longa);
            }}
        }}

        // CORREÇÃO DO CARRINHO (FORÇA A RENDERIZAÇÃO)
        document.addEventListener("DOMContentLoaded", function() {{
            if(typeof renderizarProdutos === 'function') renderizarProdutos();
            else if(typeof render === 'function') render();
        }});
    </script>
    """
    return html_base.replace("</body>", f"{script_fix}</body>")

# --- 5. INTERFACE DO USUÁRIO ---
with st.sidebar:
    st.image("https://github.com/glabpep/ordem/blob/main/1.png?raw=true", use_container_width=True)
    opcao = st.radio("MENU", ["🛒 LOJA VIRTUAL", "🔐 PAINEL DE CONTROLE"])

if opcao == "🛒 LOJA VIRTUAL":
    components.html(preparar_html(), height=1200, scrolling=True)

else:
    if not st.session_state.autenticado:
        u = st.text_input("Admin User")
        p = st.text_input("Senha", type="password")
        if st.button("Acessar"):
            if u == "admin" and p == "glab2026":
                st.session_state.autenticado = True
                st.rerun()
    else:
        st.title("📦 GESTÃO DE ESTOQUE E VENDAS")
        df_atual = carregar_dados()

        # --- ABA DE REGISTRAR VENDA (BAIXA AUTOMÁTICA) ---
        st.subheader("📝 Registrar Nova Venda")
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            prod_sel = st.selectbox("Selecione o Produto vendido", df_atual['PRODUTO'].tolist())
        with col2:
            qtd_venda = st.number_input("Quantidade", min_value=1, value=1)
        with col3:
            st.write(" ") # Alinhamento
            if st.button("Confirmar Venda"):
                # Lógica de baixa no estoque
                idx = df_atual.index[df_atual['PRODUTO'] == prod_sel].tolist()[0]
                estoque_atual = int(df_atual.at[idx, 'QTD']) if pd.notna(df_atual.at[idx, 'QTD']) else 0
                
                if estoque_atual >= qtd_venda:
                    df_atual.at[idx, 'QTD'] = estoque_atual - qtd_venda
                    # Se chegar a zero, muda status
                    if df_atual.at[idx, 'QTD'] <= 0:
                        df_atual.at[idx, 'ESTOQUE'] = "ESGOTADO"
                    
                    salvar_dados(df_atual)
                    st.success(f"Venda registrada! {prod_sel}: -{qtd_venda} unidades.")
                    st.rerun()
                else:
                    st.error("Erro: Estoque insuficiente!")

        st.divider()
        
        # --- TABELA DE EDIÇÃO MANUAL ---
        st.subheader("📊 Edição Manual do Banco de Dados")
        df_editado = st.data_editor(df_atual, use_container_width=True, hide_index=True)
        
        if st.button("💾 Salvar Alterações Manuais"):
            salvar_dados(df_editado)
            st.success("Excel atualizado!")
            st.rerun()

        if st.button("Sair do Admin"):
            st.session_state.autenticado = False
            st.rerun()
