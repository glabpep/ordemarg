import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import os
import json

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="G-LAB PEPTIDES", layout="wide", page_icon="🧪")

# CSS para esconder elementos do Streamlit e focar no site
st.markdown("""
    <style>
        .block-container { padding: 0rem; }
        iframe { border: none; }
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- FUNÇÃO DE DADOS ---
def carregar_dados_estoque():
    caminho = os.path.join(os.path.dirname(__file__), 'stock_0202 - NOVA.xlsx')
    if os.path.exists(caminho):
        df = pd.read_excel(caminho)
        df.columns = [str(col).strip().upper() for col in df.columns]
        return df
    return pd.DataFrame()

# --- INTERFACE DO SITE DE VENDAS (HTML/JS) ---
def gerar_html_vendas(df_estoque):
    # Converte DataFrame para JSON para o JavaScript
    produtos_lista = []
    for _, row in df_estoque.iterrows():
        produtos_lista.append({
            "nome": str(row.get('PRODUTO', 'N/A')),
            "espec": f"{row.get('VOLUME', '')} {row.get('MEDIDA', '')}",
            "preco": float(row.get('PREÇO (R$)', 0)),
            "qtd": int(row.get('QTD', 0))
        })
    produtos_json = json.dumps(produtos_lista)

    html_content = f"""
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{ font-family: 'Arial', sans-serif; background-color: #f4f7f6; margin: 0; padding: 10px; }}
            .container {{ max-width: 800px; margin: auto; background: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }}
            .logo {{ display: block; margin: 0 auto 10px; max-width: 220px; }}
            .card {{ border: 1px solid #eee; padding: 15px; border-radius: 10px; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center; }}
            .btn-add {{ background: #007bff; color: white; border: none; padding: 8px 15px; border-radius: 5px; cursor: pointer; font-weight: bold; }}
            .btn-add:disabled {{ background: #ccc; }}
            .carrinho-float {{ position: fixed; bottom: 20px; right: 20px; background: #25d366; color: white; padding: 15px 25px; border-radius: 50px; box-shadow: 0 4px 10px rgba(0,0,0,0.3); cursor: pointer; font-weight: bold; z-index: 99; }}
            #modalCheckout {{ display:none; position:fixed; z-index:100; left:0; top:0; width:100%; height:100%; background:rgba(0,0,0,0.6); overflow-y:auto; }}
            .modal-content {{ background:white; margin:2% auto; padding:20px; width:90%; max-width:500px; border-radius:10px; }}
            input, select {{ width: 100%; padding: 10px; margin: 8px 0; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box; }}
            .item-carrinho {{ display: flex; justify-content: space-between; border-bottom: 1px solid #eee; padding: 5px 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <img src="https://github.com/glabpep/ordem/blob/main/1.png?raw=true" class="logo">
            <h3 style="text-align:center;">Catálogo G-LAB Peptides</h3>
            
            <div style="background: #fff3cd; padding: 10px; border-radius: 5px; margin-bottom: 20px; font-size: 14px;">
                🏷️ <b>Cupom de Desconto?</b> Informe no checkout.
            </div>

            <div id="lista-produtos"></div>
        </div>

        <div class="carrinho-float" onclick="abrirCheckout()">🛒 Carrinho (<span id="cart-count">0</span>)</div>

        <div id="modalCheckout">
            <div class="modal-content">
                <h3>Finalizar Pedido</h3>
                <div id="itens-checkout" style="margin-bottom:15px; max-height: 150px; overflow-y: auto;"></div>
                
                <hr>
                <input type="text" id="cupom" placeholder="CUPOM DE DESCONTO" onchange="recalcularTotal()">
                <div id="info-precos" style="font-weight:bold; margin: 10px 0;"></div>
                
                <input type="text" id="cep" placeholder="CEP PARA FRETE" onchange="buscarCep()">
                <input type="text" id="f_nome" placeholder="NOME COMPLETO">
                <input type="text" id="f_tel" placeholder="WHATSAPP">
                <input type="text" id="f_end" placeholder="RUA E NÚMERO">
                <select id="f_pgto">
                    <option value="PIX">PIX</option>
                    <option value="CARTÃO">CARTÃO DE CRÉDITO</option>
                </select>
                
                <button onclick="enviarPedido()" style="background:#25d366; color:white; width:100%; border:none; padding:15px; border-radius:5px; font-weight:bold; cursor:pointer; font-size:16px;">ENVIAR PARA WHATSAPP</button>
                <button onclick="fecharCheckout()" style="width:100%; background:none; border:none; color:red; cursor:pointer; margin-top:10px;">CANCELAR</button>
            </div>
        </div>

        <script>
            const PRODUTOS = {produtos_json};
            let carrinho = [];
            let frete = 0;
            const CUPONS = {{ "GLAB10": 0.10, "BRUNA5": 0.05 }}; // Exemplo de cupons

            function renderizar() {{
                const lista = document.getElementById('lista-produtos');
                lista.innerHTML = "";
                PRODUTOS.forEach((p, index) => {{
                    lista.innerHTML += `
                        <div class="card">
                            <div>
                                <b>${{p.nome}}</b><br><small>${{p.espec}}</small><br>
                                <b>R$ ${{p.preco.toFixed(2)}}</b>
                            </div>
                            <button class="btn-add" onclick="addCart(${{index}})">ADICIONAR</button>
                        </div>
                    `;
                }});
            }}

            function addCart(i) {{
                carrinho.push(PRODUTOS[i]);
                document.getElementById('cart-count').innerText = carrinho.length;
            }}

            function abrirCheckout() {{
                if(carrinho.length === 0) return alert("Adicione itens ao carrinho!");
                const container = document.getElementById('itens-checkout');
                container.innerHTML = "";
                carrinho.forEach(item => {{
                    container.innerHTML += `<div class="item-carrinho"><span>${{item.nome}}</span> <span>R$ ${{item.preco.toFixed(2)}}</span></div>`;
                }});
                recalcularTotal();
                document.getElementById('modalCheckout').style.display = 'block';
            }}

            function recalcularTotal() {{
                let subtotal = carrinho.reduce((acc, item) => acc + item.preco, 0);
                let cupomTexto = document.getElementById('cupom').value.toUpperCase();
                let desconto = CUPONS[cupomTexto] ? subtotal * CUPONS[cupomTexto] : 0;
                let total = subtotal - desconto + frete;
                
                document.getElementById('info-precos').innerHTML = `
                    Subtotal: R$ ${{subtotal.toFixed(2)}}<br>
                    Desconto: R$ ${{desconto.toFixed(2)}}<br>
                    Frete: R$ ${{frete.toFixed(2)}}<br>
                    <span style="color:green; font-size:18px;">TOTAL: R$ ${{total.toFixed(2)}}</span>
                `;
            }}

            async function buscarCep() {{
                const cep = document.getElementById('cep').value.replace(/\D/g,'');
                if(cep.length === 8) {{
                    const res = await fetch(`https://viacep.com.br/ws/${{cep}}/json/`);
                    const data = await res.json();
                    if(!data.erro) {{
                        frete = 90.00; // Valor fixo conforme seu critério
                        recalcularTotal();
                        alert("Frete calculado para " + data.localidade);
                    }}
                }}
            }}

            function fecharCheckout() {{ document.getElementById('modalCheckout').style.display = 'none'; }}

            function enviarPedido() {{
                const nome = document.getElementById('f_nome').value;
                if(!nome) return alert("Preencha seus dados!");
                
                let msg = "*NOVO PEDIDO G-LAB*%0A%0A";
                carrinho.forEach(i => msg += "• " + i.nome + " - R$ " + i.preco.toFixed(2) + "%0A");
                msg += "%0A*PAGAMENTO:* " + document.getElementById('f_pgto').value;
                msg += "%0A*TOTAL COM FRETE:* R$ " + (carrinho.reduce((a,b)=>a+b.preco,0) + frete).toFixed(2);
                
                window.open("https://wa.me/+17746222523?text=" + msg, '_blank');
            }}

            renderizar();
        </script>
    </body>
    </html>
    """
    return html_content

# --- LÓGICA DO STREAMLIT (NAVEGAÇÃO E ADMIN) ---
if "logado" not in st.session_state:
    st.session_state.logado = False

df_estoque = carregar_dados_estoque()

# SIDEBAR
with st.sidebar:
    st.image("1.png", width=120)
    menu = st.radio("Navegação", ["🛒 Site de Vendas", "🔐 Área Restrita"])

# TELA 1: SITE DE VENDAS
if menu == "🛒 Site de Vendas":
    html_final = gerar_html_vendas(df_estoque)
    components.html(html_final, height=2000, scrolling=True)

# TELA 2: ÁREA RESTRITA
else:
    if not st.session_state.logado:
        st.subheader("Login Administrativo")
        user = st.text_input("Usuário")
        pw = st.text_input("Senha", type="password")
        if st.button("Entrar"):
            if user == "admin" and pw == "glab2026":
                st.session_state.logado = True
                st.rerun()
            else:
                st.error("Credenciais inválidas")
    else:
        st.title("🛠️ Gestão G-LAB")
        tab1, tab2 = st.tabs(["📊 Estoque Atual", "💰 Registrar Venda"])

        with tab1:
            st.dataframe(df_estoque, use_container_width=True)
            if st.button("Sair do Painel"):
                st.session_state.logado = False
                st.rerun()

        with tab2:
            st.subheader("Dar Baixa em Item")
            with st.form("baixa_venda"):
                produto_sel = st.selectbox("Selecione o Produto Vendido", df_estoque['PRODUTO'].tolist())
                qtd_venda = st.number_input("Quantidade Vendida", min_value=1, step=1)
                cliente_nome = st.text_input("Nome do Cliente (Opcional)")
                
                if st.form_submit_button("Confirmar Baixa"):
                    # Aqui você implementaria a lógica para salvar de volta no Excel
                    st.success(f"Baixa de {qtd_venda} unidade(s) de {produto_sel} registrada!")
                    st.info("Nota: Para salvar permanentemente, o sistema deve sobrescrever o arquivo .xlsx no GitHub.")

