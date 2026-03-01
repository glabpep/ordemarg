import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import os
import json

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="G-LAB PEPTIDES", layout="wide", page_icon="🧪")

# Esconde elementos padrão do Streamlit para o site ser o foco
st.markdown("""
    <style>
        .block-container { padding: 0rem; }
        iframe { border: none; }
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- FUNÇÕES DE DADOS (CARREGAR E SALVAR) ---
def carregar_dados_estoque():
    caminho = os.path.join(os.path.dirname(__file__), 'stock_0202 - NOVA.xlsx')
    if os.path.exists(caminho):
        try:
            df = pd.read_excel(caminho)
            df.columns = [str(col).strip().upper() for col in df.columns]
            # Limpeza da coluna QTD para evitar o ValueError
            if 'QTD' in df.columns:
                df['QTD'] = pd.to_numeric(df['QTD'], errors='coerce').fillna(0).astype(int)
            return df
        except Exception as e:
            st.error(f"Erro ao ler Excel: {e}")
    return pd.DataFrame()

def salvar_dados_estoque(df):
    caminho = os.path.join(os.path.dirname(__file__), 'stock_0202 - NOVA.xlsx')
    df.to_excel(caminho, index=False)

# --- GERADOR DO SITE (HTML/JS/CSS) ---
def gerar_html_vendas(df_estoque):
    # Filtra apenas o que tem estoque para o cliente
    prods = []
    for _, row in df_estoque.iterrows():
        if row.get('QTD', 0) > 0:
            prods.append({
                "nome": str(row.get('PRODUTO', 'N/A')),
                "espec": f"{row.get('VOLUME', '')} {row.get('MEDIDA', '')}",
                "preco": float(row.get('PREÇO (R$)', 0)),
                "status": "DISPONÍVEL"
            })
    produtos_json = json.dumps(prods)

    # O código abaixo usa {{ }} para o CSS não causar SyntaxError
    html_content = f"""
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: 'Arial', sans-serif; background-color: #f4f7f6; margin: 0; padding: 10px; }}
            .container {{ max-width: 800px; margin: auto; background: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }}
            .logo {{ display: block; margin: 0 auto 10px; max-width: 200px; }}
            .card {{ border: 1px solid #eee; padding: 15px; border-radius: 10px; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center; }}
            .btn-add {{ background: #007bff; color: white; border: none; padding: 8px 15px; border-radius: 5px; cursor: pointer; font-weight: bold; }}
            .carrinho-float {{ position: fixed; bottom: 20px; right: 20px; background: #25d366; color: white; padding: 15px 25px; border-radius: 50px; cursor: pointer; font-weight: bold; z-index: 99; }}
            #modalCheckout {{ display:none; position:fixed; z-index:100; left:0; top:0; width:100%; height:100%; background:rgba(0,0,0,0.6); }}
            .modal-content {{ background:white; margin:10% auto; padding:20px; width:90%; max-width:450px; border-radius:10px; }}
            input, select {{ width: 100%; padding: 10px; margin: 8px 0; border: 1px solid #ddd; border-radius: 5px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <img src="https://github.com/glabpep/ordem/blob/main/1.png?raw=true" class="logo">
            <h3 style="text-align:center;">Catálogo G-LAB Peptides</h3>
            <div id="lista-produtos"></div>
        </div>

        <div class="carrinho-float" onclick="abrirCheckout()">🛒 Carrinho (<span id="cart-count">0</span>)</div>

        <div id="modalCheckout">
            <div class="modal-content">
                <h3>Finalizar Pedido</h3>
                <div id="resumo-itens"></div>
                <input type="text" id="cupom" placeholder="CUPOM DE DESCONTO" oninput="atualizarTotal()">
                <div id="total-final" style="font-weight:bold; margin: 10px 0;"></div>
                <input type="text" id="f_nome" placeholder="SEU NOME">
                <select id="f_pgto"><option value="PIX">PIX</option><option value="CARTÃO">CARTÃO</option></select>
                <button onclick="enviarWhatsapp()" style="background:#25d366; color:white; width:100%; border:none; padding:15px; border-radius:5px; font-weight:bold; cursor:pointer;">ENVIAR WHATSAPP</button>
                <button onclick="fecharCheckout()" style="width:100%; background:none; border:none; color:red; cursor:pointer; margin-top:10px;">CANCELAR</button>
            </div>
        </div>

        <script>
            const PRODS = {produtos_json};
            let cart = [];
            const CUPONS = {{ "GLAB10": 0.1, "BRUNA5": 0.05 }};

            function render() {{
                const div = document.getElementById('lista-produtos');
                div.innerHTML = PRODS.map((p, i) => `
                    <div class="card">
                        <div><b>${{p.nome}}</b><br><small>${{p.espec}}</small><br>R$ ${{p.preco.toFixed(2)}}</div>
                        <button class="btn-add" onclick="addCart(${{i}})">ADICIONAR</button>
                    </div>
                `).join('');
            }}

            function addCart(i) {{
                cart.push(PRODS[i]);
                document.getElementById('cart-count').innerText = cart.length;
            }}

            function abrirCheckout() {{
                if(cart.length === 0) return alert("Carrinho vazio!");
                document.getElementById('modalCheckout').style.display = 'block';
                atualizarTotal();
            }}

            function atualizarTotal() {{
                let sub = cart.reduce((a, b) => a + b.preco, 0);
                let cupom = document.getElementById('cupom').value.toUpperCase();
                let desc = CUPONS[cupom] ? sub * CUPONS[cupom] : 0;
                document.getElementById('total-final').innerText = "Total: R$ " + (sub - desc + 90).toFixed(2) + " (com frete)";
            }}

            function fecharCheckout() {{ document.getElementById('modalCheckout').style.display = 'none'; }}

            function enviarWhatsapp() {{
                let nome = document.getElementById('f_nome').value;
                if(!nome) return alert("Nome obrigatório");
                let txt = "Novo Pedido G-LAB:%0ACliente: " + nome + "%0AItens:%0A" + cart.map(i => "- " + i.nome).join("%0A");
                window.open("https://wa.me/17746222523?text=" + txt);
            }}

            render();
        </script>
    </body>
    </html>
    """
    return html_content

# --- LÓGICA DE NAVEGAÇÃO ---
if "logado" not in st.session_state:
    st.session_state.logado = False

df = carregar_dados_estoque()

with st.sidebar:
    st.image("1.png", width=100)
    escolha = st.radio("Menu", ["🛒 Ir para Loja", "🔐 Área do Funcionário"])

if escolha == "🛒 Ir para Loja":
    components.html(gerar_html_vendas(df), height=1500, scrolling=True)

else:
    if not st.session_state.logado:
        u = st.text_input("Usuário")
        s = st.text_input("Senha", type="password")
        if st.button("Entrar"):
            if u == "admin" and s == "glab2026":
                st.session_state.logado = True
                st.rerun()
    else:
        st.title("Painel de Controle")
        tab1, tab2 = st.tabs(["Estoque", "Registrar Venda"])
        
        with tab1:
            st.dataframe(df)
            if st.button("Sair"):
                st.session_state.logado = False
                st.rerun()
        
        with tab2:
            st.subheader("Dar baixa no estoque")
            prod_sel = st.selectbox("Produto", df['PRODUTO'].tolist())
            qtd_venda = st.number_input("Quantidade", min_value=1, value=1)
            
            if st.button("Confirmar Venda"):
                idx = df[df['PRODUTO'] == prod_sel].index[0]
                if df.at[idx, 'QTD'] >= qtd_venda:
                    df.at[idx, 'QTD'] -= qtd_venda
                    salvar_dados_estoque(df) # SALVA NO EXCEL
                    st.success("Venda registrada! O estoque foi atualizado.")
                else:
                    st.error("Estoque insuficiente!")
