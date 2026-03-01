import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import os
import json

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="G-LAB PEPTIDES", layout="wide", page_icon="🧪")

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

# CSS para Mobile e Limpeza
st.markdown("""
    <style>
        .block-container { padding: 0rem; max-width: 100%; }
        footer {visibility: hidden;}
        header {visibility: hidden;}
        [data-testid="stSidebar"] { background-color: #f8f9fa; }
    </style>
""", unsafe_allow_html=True)

# --- 2. BACKEND: DADOS ---
def carregar_dados():
    caminho = 'stock_0202 - NOVA.xlsx'
    if os.path.exists(caminho):
        df = pd.read_excel(caminho)
        df.columns = [str(col).strip() for col in df.columns]
        return df
    return pd.DataFrame()

def salvar_dados(df):
    df.to_excel('stock_0202 - NOVA.xlsx', index=False)

# --- 3. INJEÇÃO DINÂMICA NO INDEX.HTML ---
def gerar_site():
    df = carregar_dados()
    produtos_lista = []
    
    for _, row in df.iterrows():
        nome = str(row.get('PRODUTO', '')).strip()
        # Forçamos a URL da imagem para bater com o padrão do GitHub em Maiúsculas
        url_img = f"https://raw.githubusercontent.com/glabpep/ordem/main/{nome.replace(' ', '%20').upper()}.webp"
        
        produtos_lista.append({
            "nome": nome,
            "espec": f"{row.get('VOLUME', '')} {row.get('MEDIDA', '')}",
            "preco": float(row.get('Preço (R$)', 0)),
            "status": str(row.get('ESTOQUE', 'EM ESPERA')).upper(),
            "qtd": int(row.get('QTD', 0)) if pd.notna(row.get('QTD')) else 0,
            "img": url_img
        })

    if not os.path.exists('index.html'):
        return "<h1>Arquivo index.html não encontrado!</h1>"

    with open('index.html', 'r', encoding='utf-8') as f:
        html_original = f.read()

    # O "CÉREBRO" QUE CONECTA O EXCEL AO SEU DESIGN
    script_conexao = f"""
    <script>
        // Injeção dos dados do Excel
        window.produtosBase = {json.dumps(produtos_lista)};
        
        // FUNÇÃO PARA REDESENHAR A LISTA (Garante Mobile e clique funcional)
        function atualizarListaDinamica() {{
            const listaContainer = document.querySelector('.product-list') || document.getElementById('lista-produtos');
            if(!listaContainer) return;

            listaContainer.innerHTML = ''; // Limpa o estático que não funciona

            window.produtosBase.forEach((prod, index) => {{
                const item = document.createElement('div');
                item.className = 'product-card'; // Usa sua classe original do CSS
                
                // HTML interno idêntico ao seu design, mas com variáveis dinâmicas
                item.innerHTML = `
                    <div class="prod-img-box" style="width:80px; height:80px; flex-shrink:0;">
                        <img src="${{prod.img}}" style="width:100%; height:100%; object-fit:contain;" 
                             onerror="this.src='https://via.placeholder.com/100?text=G-LAB'">
                    </div>
                    <div class="prod-info" style="flex-grow:1; padding-left:10px;">
                        <h4 style="margin:0; font-size:1rem; text-transform:uppercase;">${{prod.nome}}</h4>
                        <p style="margin:2px 0; color:#004a99; font-weight:bold; font-size:0.8rem;">${{prod.espec}}</p>
                        <p style="margin:5px 0 0 0; font-weight:900; font-size:1.1rem;">R$ ${{prod.preco.toLocaleString('pt-BR', {{minimumFractionDigits:2}})}}</p>
                    </div>
                    <div class="prod-action">
                        ${{ (prod.qtd > 0 || prod.status === 'DISPONÍVEL') 
                            ? `<button onclick="adicionarAoCarrinho(${{index}})" style="background:#004a99; color:white; border:none; padding:12px 15px; border-radius:10px; font-weight:bold; font-size:1.2rem; cursor:pointer;">+</button>`
                            : `<span style="color:#dc3545; font-weight:bold; font-size:0.8rem;">OFF</span>`
                        }}
                    </div>
                `;
                listaContainer.appendChild(item);
            }});
        }}

        // CORREÇÃO DAS IMAGENS NO MODAL (Características)
        // Substituímos a função abrirInfo original para usar os dados do Excel
        window.abrirInfo = function(index) {{
            const p = window.produtosBase[index];
            const modalImg = document.getElementById('modal-img-detalhe'); 
            if(modalImg) modalImg.src = p.img;
            
            // Se o seu modal usa outros IDs, ele atualizará aqui
            alert("Produto: " + p.nome + "\\nStatus: " + p.status);
        }};

        // Dispara a atualização assim que o HTML carregar
        window.addEventListener('load', atualizarListaDinamica);
        
        // Sobrescreve a função de adicionar ao carrinho para garantir que use o novo índice
        window.adicionarAoCarrinho = function(index) {{
            const p = window.produtosBase[index];
            if(typeof carrinho !== 'undefined') {{
                carrinho.push(p);
                if(typeof atualizarCarrinho === 'function') atualizarCarrinho();
                if(typeof salvarCarrinho === 'function') salvarCarrinho();
                console.log("Adicionado:", p.nome);
            }} else {{
                alert("Adicionado: " + p.nome + " (R$ " + p.preco + ")");
            }}
        }};
    </script>
    """
    return html_original.replace("</body>", f"{script_conexao}</body>")

# --- 4. INTERFACE ---
with st.sidebar:
    st.image("https://github.com/glabpep/ordem/blob/main/1.png?raw=true", use_container_width=True)
    menu = st.radio("NAVEGAÇÃO", ["🛒 LOJA (MOBILE READY)", "🔐 ADMINISTRAÇÃO"])

if menu == "🛒 LOJA (MOBILE READY)":
    site_html = gerar_site()
    components.html(site_html, height=2000, scrolling=True)

else:
    if not st.session_state.autenticado:
        u = st.text_input("Usuário")
        p = st.text_input("Senha", type="password")
        if st.button("Entrar"):
            if u == "admin" and p == "glab2026":
                st.session_state.autenticado = True
                st.rerun()
    else:
        st.title("🛠 Painel de Controle G-LAB")
        df = carregar_dados()
        
        # REGISTRAR VENDA
        st.subheader("📝 Registrar Venda")
        c1, c2 = st.columns(2)
        with c1:
            p_sel = st.selectbox("Produto", df['PRODUTO'].unique())
        with c2:
            q_venda = st.number_input("Quantidade", min_value=1, value=1)
        
        if st.button("Confirmar Saída de Estoque"):
            idx = df.index[df['PRODUTO'] == p_sel].tolist()[0]
            if df.at[idx, 'QTD'] >= q_venda:
                df.at[idx, 'QTD'] -= q_venda
                salvar_dados(df)
                st.success(f"Venda registrada! {p_sel} atualizado.")
                st.rerun()
            else:
                st.error("Estoque insuficiente!")

        st.divider()
        # TABELA
        df_editado = st.data_editor(df, use_container_width=True, hide_index=True)
        if st.button("💾 Salvar Alterações na Tabela"):
            salvar_dados(df_editado)
            st.success("Excel salvo!")
