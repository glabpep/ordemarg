import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import os
import json

# --- 1. CONFIGURAÇÃO DE TELA ---
st.set_page_config(page_title="G-LAB ADMIN", layout="wide")

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

# --- 2. CARREGAR EXCEL ---
def carregar_dados():
    # Procura o arquivo na pasta atual
    for nome in ['stock_0202 - NOVA.xlsx', 'stock_2901.xlsx']:
        if os.path.exists(nome):
            df = pd.read_excel(nome)
            df.columns = [str(col).strip() for col in df.columns]
            return df, nome
    return pd.DataFrame(), None

# --- 3. PREPARAR DADOS PARA O FRONT-END ---
df_estoque, arquivo_nome = carregar_dados()
produtos_para_site = []

if not df_estoque.empty:
    col_p = 'Preço (R$)' if 'Preço (R$)' in df_estoque.columns else 'PREÇO'
    for _, row in df_estoque.iterrows():
        nome_bruto = str(row.get('PRODUTO', '')).strip()
        
        # CORREÇÃO CRÍTICA: Link RAW do GitHub para as imagens .webp
        # Se o arquivo no GitHub for "AICAR.webp", o link precisa ser exatamente assim
        link_imagem = f"https://raw.githubusercontent.com/glabpep/ordem/main/{nome_bruto.replace(' ', '%20').upper()}.webp"
        
        produtos_para_site.append({
            "nome": nome_bruto,
            "espec": f"{row.get('VOLUME', '')} {row.get('MEDIDA', '')}",
            "preco": float(row.get(col_p, 0)),
            "estoque": str(row.get('ESTOQUE', 'EM ESPERA')).upper(),
            "qtd": int(row.get('QTD', 0)) if pd.notna(row.get('QTD')) else 0,
            "img": link_imagem
        })

# --- 4. INJEÇÃO NO SEU INDEX.HTML ---
def gerar_html_final():
    if not os.path.exists('index.html'):
        return "<h1>Erro: index.html não encontrado na pasta!</h1>"
    
    with open('index.html', 'r', encoding='utf-8') as f:
        html_conteudo = f.read()

    # Este script "hackeia" o seu index.html para ele aceitar os dados do Excel
    script_fix = f"""
    <script>
        // 1. Injeta os dados do Excel na variável que o seu HTML usa
        window.produtosBase = {json.dumps(produtos_para_site)};
        var produtos = window.produtosBase; 

        // 2. Função para garantir que as imagens apareçam no Modal de Informações
        function abrirInfo(nome) {{
            const p = window.produtosBase.find(x => x.nome === nome);
            if(p) {{
                // Tenta achar o elemento de imagem do seu modal e troca o SRC
                const imgModal = document.querySelector('.info-modal-img') || document.getElementById('img-caract');
                if(imgModal) imgModal.src = p.img;
                alert(p.nome + " - " + p.espec + "\\nStatus: " + p.estoque);
            }}
        }}

        // 3. Forçar a renderização assim que o site abrir no Celular
        window.addEventListener('DOMContentLoaded', function() {{
            if (typeof renderizarProdutos === 'function') {{
                renderizarProdutos(); 
            }} else {{
                // Se o seu HTML não tiver a função com esse nome, tentamos rodar o seu script original
                console.log("Tentando inicializar sistema de vendas...");
            }}
        }});
    </script>
    """
    return html_conteudo.replace("</body>", f"{script_fix}</body>")

# --- 5. INTERFACE DO USUÁRIO ---
with st.sidebar:
    st.image("https://raw.githubusercontent.com/glabpep/ordem/main/1.png", use_container_width=True)
    aba = st.radio("Navegar", ["🛒 Ver Loja (Site)", "🔐 Painel Admin"])

if aba == "🛒 Ver Loja (Site)":
    # Mostra o seu site real com os dados injetados
    components.html(gerar_html_final(), height=1200, scrolling=True)

else:
    # AREA DO ADMIN
    if not st.session_state.autenticado:
        u = st.text_input("Usuário")
        p = st.text_input("Senha", type="password")
        if st.button("Logar"):
            if u == "admin" and p == "glab2026":
                st.session_state.autenticado = True
                st.rerun()
    else:
        st.title("Admin G-LAB")
        
        # REGISTRO DE VENDA (BAIXA NO ESTOQUE)
        st.subheader("Registrar Venda Direta")
        c1, c2 = st.columns(2)
        with c1:
            p_venda = st.selectbox("Produto vendido", df_estoque['PRODUTO'].unique())
        with c2:
            q_venda = st.number_input("Qtd", min_value=1, value=1)
        
        if st.button("Dar Baixa no Excel"):
            idx = df_estoque.index[df_estoque['PRODUTO'] == p_venda].tolist()[0]
            df_estoque.at[idx, 'QTD'] = int(df_estoque.at[idx, 'QTD']) - q_venda
            df_estoque.to_excel(arquivo_nome, index=False)
            st.success("Venda registrada! O site foi atualizado.")
            st.rerun()
        
        st.divider()
        st.subheader("Editar Planilha Completa")
        df_edit = st.data_editor(df_estoque, hide_index=True)
        if st.button("Salvar Tabela"):
            df_edit.to_excel(arquivo_nome, index=False)
            st.success("Salvo!")
