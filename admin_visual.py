import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import os
import json

# --- 1. CONFIGURAÇÃO E LIMPEZA DE INTERFACE ---
st.set_page_config(page_title="G-LAB PEPTIDES", layout="wide", page_icon="🧪")

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

st.markdown("""
    <style>
        .block-container { padding: 0rem; max-width: 100%; }
        footer {visibility: hidden;}
        header {visibility: hidden;}
        [data-testid="stSidebar"] { background-color: #f8f9fa; }
    </style>
""", unsafe_allow_html=True)

# --- 2. BACKEND: BANCO DE DADOS ---
def carregar_dados():
    caminho = 'stock_0202 - NOVA.xlsx'
    if os.path.exists(caminho):
        df = pd.read_excel(caminho)
        df.columns = [str(col).strip() for col in df.columns]
        return df
    return pd.DataFrame()

def salvar_dados(df):
    df.to_excel('stock_0202 - NOVA.xlsx', index=False)

# --- 3. DICIONÁRIO TÉCNICO E IMAGENS ---
INFOS_TECNICAS = {
    "5-AMINO": "Inibidor Seletivo de NNMT: Auxilia na reversão da obesidade e gasto energético.",
    "AICAR": "Ativador de AMPK: Melhora a resistência cardiovascular e oxidação de gordura.",
    "AOD 9604": "Fragmento Lipolítico: Focado na queima de gordura visceral.",
    "BPC-157": "Regeneração Ativa: Cicatrização de tendões, músculos e mucosa gástrica.",
    "CJC-1295": "Liberação de GH: Estimula a hipófise para produção endógena.",
    "GHK-CU": "Peptídeo de Cobre: Rejuvenescimento celular e síntese de colágeno.",
    "IPAMORELIN": "Agonista Seletivo: Aumento de GH sem pico de cortisol.",
    "MELANOTAN": "Bronzeamento e Libido: Atua nos receptores de melanocortina.",
    "TB-500": "Reparo Tecidual: Recuperação acelerada de lesões inflamatórias.",
    "MK-677": "Ibutamoren: Aumento sustentado de IGF-1 e massa magra."
}

# --- 4. PREPARAÇÃO DO SITE (HTML DINÂMICO) ---
def preparar_site_vendas():
    df = carregar_dados()
    produtos_json = []
    
    for _, row in df.iterrows():
        nome_original = str(row.get('PRODUTO', '')).strip()
        nome_up = nome_original.upper()
        
        # Define a descrição técnica
        desc = "Peptídeo de alta pureza para fins de pesquisa."
        for k, v in INFOS_TECNICAS.items():
            if k in nome_up:
                desc = v
                break
        
        # Link da Imagem no GitHub (Garante Maiúsculas para evitar erro de link)
        url_img = f"https://raw.githubusercontent.com/glabpep/ordem/main/{nome_original.replace(' ', '%20').upper()}.webp"
        
        produtos_json.append({
            "nome": nome_original,
            "espec": f"{row.get('VOLUME', '')} {row.get('MEDIDA', '')}",
            "preco": float(row.get('Preço (R$)', 0)),
            "estoque": str(row.get('ESTOQUE', 'EM ESPERA')).upper(),
            "qtd": int(row.get('QTD', 0)) if pd.notna(row.get('QTD')) else 0,
            "desc": desc,
            "img": url_img
        })

    if os.path.exists('index.html'):
        with open('index.html', 'r', encoding='utf-8') as f:
            html = f.read()
    else:
        return "<h1>Arquivo index.html não encontrado!</h1>"

    # INJEÇÃO DE CORREÇÃO PARA MOBILE E IMAGENS
    script_correcao = f"""
    <script>
        // 1. Backend injeta os dados reais aqui
        window.produtosBase = {json.dumps(produtos_json)};
        
        // 2. Sobrescreve a função de renderização para garantir Mobile e Imagens
        function renderizarProdutos() {{
            const container = document.getElementById('lista-produtos') || document.querySelector('.product-list');
            if(!container) return;
            
            container.innerHTML = ""; // Limpa o estático
            
            window.produtosBase.forEach((p, index) => {{
                const card = document.createElement('div');
                card.className = 'product-card'; // Mantendo sua classe do CSS
                card.style = 'display: flex; align-items: center; padding: 10px; border: 1px solid #eee; margin-bottom: 10px; border-radius: 12px; background: #fff; gap: 10px;';
                
                card.innerHTML = `
                    <div style="width: 70px; height: 70px; flex-shrink: 0;">
                        <img src="${{p.img}}" style="width: 100%; height: 100%; object-fit: contain;" onerror="this.src='https://via.placeholder.com/80?text=LAB'">
                    </div>
                    <div style="flex-grow: 1;">
                        <h4 style="margin: 0; font-size: 0.95rem; text-transform: uppercase;">${{p.nome}}</h4>
                        <p style="margin: 0; color: #004a99; font-weight: bold; font-size: 0.8rem;">${{p.espec}}</p>
                        <p style="margin: 4px 0 0 0; font-weight: 900; font-size: 1rem;">R$ ${{p.preco.toLocaleString('pt-BR', {{minimumFractionDigits:2}})}}</p>
                    </div>
                    <div style="text-align: center;">
                        ${{ (p.qtd > 0 || p.estoque === 'DISPONÍVEL') 
                            ? `<button onclick="adicionarAoCarrinho(${{index}})" style="background: #004a99; color: white; border: none; padding: 10px 15px; border-radius: 8px; font-weight: bold;">+</button>` 
                            : `<span style="color: red; font-size: 0.7rem; font-weight: bold;">OFF</span>` 
                        }}
                    </div>
                `;
                container.appendChild(card);
            }});
        }}

        // 3. Sobrescreve a função de informações para exibir a imagem
        function abrirInfo(index) {{
            const p = window.produtosBase[index];
            // Aqui garantimos que a imagem apareça no modal de características
            const imgModal = document.getElementById('modal-img');
            if(imgModal) imgModal.src = p.img;
            
            alert(p.nome + ": " + p.desc);
        }}

        // Inicializa
        window.onload = renderizarProdutos;
    </script>
    """
    return html.replace("</body>", f"{script_correcao}</body>")

# --- 5. INTERFACE STREAMLIT ---
with st.sidebar:
    st.image("https://github.com/glabpep/ordem/blob/main/1.png?raw=true", use_container_width=True)
    aba = st.radio("NAVEGAÇÃO", ["🛒 SITE DE VENDAS", "🔐 ÁREA ADMIN"])

if aba == "🛒 SITE DE VENDAS":
    components.html(preparar_site_vendas(), height=1500, scrolling=True)

else:
    if not st.session_state.autenticado:
        u = st.text_input("Usuário")
        p = st.text_input("Senha", type="password")
        if st.button("Entrar"):
            if u == "admin" and p == "glab2026":
                st.session_state.autenticado = True
                st.rerun()
    else:
        st.title("🛠 Gestão G-LAB")
        df_atual = carregar_dados()

        # REGISTRO DE VENDA
        st.subheader("📝 Registrar Venda (Baixa Automática)")
        c1, c2 = st.columns([2, 1])
        with c1:
            p_venda = st.selectbox("Produto", df_atual['PRODUTO'].unique())
        with c2:
            q_venda = st.number_input("Qtd", min_value=1, value=1)
            
        if st.button("Confirmar Baixa no Estoque"):
            idx = df_atual.index[df_atual['PRODUTO'] == p_venda].tolist()[0]
            estoque_hoje = int(df_atual.at[idx, 'QTD']) if pd.notna(df_atual.at[idx, 'QTD']) else 0
            
            if estoque_hoje >= q_venda:
                df_atual.at[idx, 'QTD'] = estoque_hoje - q_venda
                if df_atual.at[idx, 'QTD'] == 0:
                    df_atual.at[idx, 'ESTOQUE'] = "EM ESPERA"
                salvar_dados(df_atual)
                st.success(f"Venda de {p_venda} registrada!")
                st.rerun()
            else:
                st.error("Estoque insuficiente!")

        st.divider()
        st.subheader("📊 Tabela Geral")
        df_editado = st.data_editor(df_atual, use_container_width=True, hide_index=True)
        if st.button("💾 Salvar Alterações da Tabela"):
            salvar_dados(df_editado)
            st.success("Excel atualizado!")
