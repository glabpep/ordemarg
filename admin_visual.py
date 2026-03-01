import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import os
import json

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="G-LAB ADMIN", layout="wide")

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

# --- 2. CARREGAR DADOS DO EXCEL ---
def carregar_dados():
    caminho = 'stock_0202 - NOVA.xlsx'
    if os.path.exists(caminho):
        df = pd.read_excel(caminho)
        df.columns = [str(col).strip() for col in df.columns]
        return df
    return pd.DataFrame()

# --- 3. GERAR O HTML DINÂMICO ---
def gerar_site_vivo():
    df = carregar_dados()
    produtos_lista = []
    
    for _, row in df.iterrows():
        nome_item = str(row.get('PRODUTO', '')).strip()
        # Link RAW do GitHub em MAIÚSCULAS para evitar erro de 404
        url_img = f"https://raw.githubusercontent.com/glabpep/ordem/main/{nome_item.replace(' ', '%20').upper()}.webp"
        
        produtos_lista.append({
            "nome": nome_item,
            "espec": f"{row.get('VOLUME', '')} {row.get('MEDIDA', '')}",
            "preco": float(row.get('Preço (R$)', 0)),
            "status": str(row.get('ESTOQUE', 'EM ESPERA')).upper(),
            "qtd": int(row.get('QTD', 0)) if pd.notna(row.get('QTD')) else 0,
            "img": url_img
        })

    if not os.path.exists('index.html'):
        return "<h1>Erro: index.html não encontrado na pasta!</h1>"

    with open('index.html', 'r', encoding='utf-8') as f:
        html_original = f.read()

    # SCRIPT DE REATIVAÇÃO DO SITE
    # Este bloco força o JavaScript do seu HTML a reconhecer os dados do Excel
    script_ativador = f"""
    <script>
        // 1. Injetar dados do Excel
        window.produtosBase = {json.dumps(produtos_lista)};
        
        // 2. Função para reconstruir a lista e ativar botões e imagens
        function reativarSite() {{
            const container = document.querySelector('.product-list') || document.getElementById('lista-produtos');
            if(!container) return;

            container.innerHTML = ""; // Limpa o lixo estático

            window.produtosBase.forEach((p, i) => {{
                const card = document.createElement('div');
                card.className = 'product-card';
                card.style = "display:flex; align-items:center; border-bottom:1px solid #eee; padding:15px 0; gap:15px;";
                
                card.innerHTML = `
                    <img src="${{p.img}}" style="width:80px; height:80px; object-fit:contain;" onerror="this.src='https://via.placeholder.com/80?text=GLAB'">
                    <div style="flex-grow:1;">
                        <h4 style="margin:0; text-transform:uppercase;">${{p.nome}}</h4>
                        <small style="color:#004a99; font-weight:bold;">${{p.espec}}</small>
                        <div style="font-weight:900; font-size:1.1rem; margin-top:5px;">R$ ${{p.preco.toFixed(2)}}</div>
                    </div>
                    <button onclick="adicionarAoCarrinho(${{i}})" style="background:#004a99; color:white; border:none; width:40px; height:40px; border-radius:10px; font-weight:bold; font-size:1.2rem;">+</button>
                `;
                container.appendChild(card);
            }});
        }}

        // 3. Forçar o carrinho a funcionar
        window.adicionarAoCarrinho = function(index) {{
            const item = window.produtosBase[index];
            if(typeof carrinho !== 'undefined') {{
                carrinho.push(item);
                if(typeof atualizarCarrinho === 'function') atualizarCarrinho();
                if(typeof abrirCarrinho === 'function') abrirCarrinho();
            }} else {{
                alert("Adicionado: " + item.nome);
            }}
        }};

        // Executa a reativação assim que o DOM estiver pronto
        if (document.readyState === 'loading') {{
            document.addEventListener('DOMContentLoaded', reativarSite);
        }} else {{
            reativarSite();
        }}
    </script>
    """
    return html_original.replace("</body>", f"{script_ativador}</body>")

# --- 4. INTERFACE ---
with st.sidebar:
    st.image("https://raw.githubusercontent.com/glabpep/ordem/main/1.png", use_container_width=True)
    menu = st.radio("Navegação", ["🛒 Loja Viva", "🔐 Admin"])

if menu == "🛒 Loja Viva":
    components.html(gerar_site_vivo(), height=2000, scrolling=True)

else:
    if not st.session_state.autenticado:
        u = st.text_input("Usuário")
        p = st.text_input("Senha", type="password")
        if st.button("Entrar"):
            if u == "admin" and p == "glab2026":
                st.session_state.autenticado = True
                st.rerun()
    else:
        st.title("Painel Admin")
        df = carregar_dados()
        
        # REGISTRAR VENDA
        st.subheader("Registrar Venda")
        p_sel = st.selectbox("Produto", df['PRODUTO'].unique())
        q_venda = st.number_input("Qtd", min_value=1, value=1)
        if st.button("Baixar Estoque"):
            idx = df.index[df['PRODUTO'] == p_sel].tolist()[0]
            df.at[idx, 'QTD'] -= q_venda
            df.to_excel('stock_0202 - NOVA.xlsx', index=False)
            st.success("Venda registada!")
            st.rerun()

        st.divider()
        df_edit = st.data_editor(df, hide_index=True)
        if st.button("Salvar Tudo"):
            df_edit.to_excel('stock_0202 - NOVA.xlsx', index=False)
            st.success("Excel guardado!")
