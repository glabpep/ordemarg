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

# --- FUNÇÕES DE PERSISTÊNCIA ---
def carregar_dados_estoque():
    caminho = os.path.join(os.path.dirname(__file__), 'stock_0202 - NOVA.xlsx')
    if os.path.exists(caminho):
        df = pd.read_excel(caminho)
        df.columns = [str(col).strip().upper() for col in df.columns]
        # Limpeza da coluna QTD para evitar erros de conversão
        if 'QTD' in df.columns:
            df['QTD'] = pd.to_numeric(df['QTD'], errors='coerce').fillna(0).astype(int)
        return df
    return pd.DataFrame()

def salvar_dados_estoque(df):
    caminho = os.path.join(os.path.dirname(__file__), 'stock_0202 - NOVA.xlsx')
    df.to_excel(caminho, index=False)

# --- INTERFACE DO SITE DE VENDAS (HTML/JS) ---
def gerar_html_vendas(df_estoque):
    # Converte DataFrame para JSON para o JavaScript
    produtos_lista = []
    for _, row in df_estoque.iterrows():
        # Apenas exibe produtos com estoque maior que zero
        if row.get('QTD', 0) > 0:
            produtos_lista.append({
                "nome": str(row.get('PRODUTO', 'N/A')),
                "espec": f"{row.get('VOLUME', '')} {row.get('MEDIDA', '')}",
                "preco": float(row.get('PREÇO (R$)', 0)),
                "qtd_disponivel": int(row.get('QTD', 0))
            })
    produtos_json = json.dumps(produtos_lista)

    # Nota: Uso de {{ }} para CSS para evitar erro de f-string do Python
    html_content = f"""
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f7f6; margin: 0; padding: 10px; }}
            .container {{ max-width: 800px; margin: auto; background: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }}
            .logo {{ display: block; margin: 0 auto 10px; max-width: 220px; }}
            .card {{ border: 1px solid #eee; padding: 15px; border-radius: 10px; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center; transition: 0.3s; }}
            .card:hover {{ border-color: #007bff; }}
            .btn-add {{ background: #007bff; color: white; border: none; padding: 8px 15px; border-radius: 5px; cursor: pointer; font-weight: bold; }}
            .carrinho-float {{ position: fixed; bottom: 20px; right: 20px; background: #25d366; color: white; padding: 15px 25px; border-radius: 50px; box-shadow: 0 4px 10px rgba(0,0,0,0.3); cursor: pointer; font-weight: bold; z-index: 99; display: flex; align-items: center; gap: 10px; }}
            #modalCheckout {{ display:none; position:fixed; z-index:100; left:0; top:0; width:100%; height:100%; background:rgba(0,0,0,0.6); overflow-y:auto; }}
            .modal-content {{ background:white; margin:2% auto; padding:25px; width:90%; max-width:500px; border-radius:12px; box-shadow: 0 5px 15px rgba(0,0,0,0.3); }}
            input, select {{ width: 100%; padding: 12px; margin: 8px 0; border: 1px solid #ddd; border-radius: 6px; box-sizing: border-box; }}
            .item-carrinho {{ display: flex; justify-content: space-between; border-bottom: 1px solid #eee; padding: 8px 0; }}
            .total-destaque {{ color: #2e7d32; font-size: 20px; font-weight: bold; margin-top: 10px; border-top: 2px solid #eee; padding-top: 10px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <img src="https://github.com/glabpep/ordem/blob/main/1.png?raw=true" class="logo">
            <h3 style="text-align:center; color: #333;">Catálogo Online G-LAB</h3>
            <div id="lista-produtos"></div>
        </div>

        <div class="carrinho-float" id="btn-cart-float" style="display: none;" onclick="abrirCheckout()">
            🛒 Ver Carrinho (<span id="cart-count">0</span>)
        </div>

        <div id="modalCheckout">
            <div class="modal-content">
                <h3 style="margin-top:0;">Resumo do Pedido</h3>
                <div id="itens-checkout" style="margin-bottom:15px; max-height: 200px; overflow-y: auto;"></div>
                
                <hr>
                <input type="text" id="cupom" placeholder="CUPOM DE DESCONTO (Ex: BRUNA5)" oninput="recalcularTotal()">
                <div id="info-precos"></div>
                
                <input type="text" id="cep" placeholder="CEP (Para cálculo de região)" oninput="buscarCep()">
                <input type="text" id="f_nome" placeholder="NOME COMPLETO">
                <input type="text" id="f_tel" placeholder="WHATSAPP (Ex: 41999999999)">
                <input type="text" id="f_end" placeholder="ENDEREÇO COMPLETO">
                
                <p style="margin: 5px 0; font-size: 14px;">Forma de Pagamento:</p>
                <select id="f_pgto">
                    <option value="PIX">PIX</option>
                    <option value="CARTÃO DE CRÉDITO">CARTÃO DE CRÉDITO</option>
                </select>
                
                <button onclick="enviarPedido()" style="background:#25d366; color:white; width:100%; border:none; padding:16px; border-radius:8px; font-weight:bold; cursor:pointer; font-size:16px; margin-top:10px;">FECHAR PEDIDO VIA WHATSAPP</button>
                <button onclick="fecharCheckout()" style="width:100%; background:none; border:none; color:#666; cursor:pointer; margin-top:10px;">Voltar às compras</button>
            </div>
        </div>

        <script>
            const PRODUTOS = {produtos_json};
            let carrinho = [];
            let freteValor = 0;
            let freteTexto = "A calcular";
            const CUPONS_DESCONTO = {{ "GLAB10": 0.10, "BRUNA5": 0.05, "PROMO15": 0.15 }};

            function renderizar() {{
                const lista = document.getElementById('lista-produtos');
                lista.innerHTML = "";
                PRODUTOS.forEach((p, index) => {{
                    lista.innerHTML += `
                        <div class="card">
                            <div>
                                <b style="font-size:16px;">${{p.nome}}</b><br>
                                <small style="color:#666;">${{p.espec}}</small><br>
                                <b style="color:#007bff;">R$ ${{p.preco.toFixed(2)}}</b>
                            </div>
                            <button class="btn-add" onclick="addCart(${{index}})">ADICIONAR</button>
                        </div>
                    `;
                }});
            }}

            function addCart(i) {{
                carrinho.push(PRODUTOS[i]);
                document.getElementById('cart-count').innerText = carrinho.length;
                document.getElementById('btn-cart-float').style.display = 'flex';
            }}

            function recalcularTotal() {{
                let subtotal = carrinho.reduce((acc, item) => acc + item.preco, 0);
                let cupomInput = document.getElementById('cupom').value.toUpperCase();
                let descontoValor = 0;
                
                if(CUPONS_DESCONTO[cupomInput]) {{
                    descontoValor = subtotal * CUPONS_DESCONTO[cupomInput];
                }}

                let totalFinal = subtotal - descontoValor + freteValor;
                
                document.getElementById('info-precos').innerHTML = `
                    <div style="display:flex; justify-content:space-between; margin:2px 0;"><span>Subtotal:</span> <span>R$ ${{subtotal.toFixed(2)}}</span></div>
                    <div style="display:flex; justify-content:space-between; margin:2px 0; color:#d32f2f;"><span>Desconto:</span> <span>- R$ ${{descontoValor.toFixed(2)}}</span></div>
                    <div style="display:flex; justify-content:space-between; margin:2px 0;"><span>Frete (${{freteTexto}}):</span> <span>R$ ${{freteValor.toFixed(2)}}</span></div>
                    <div class="total-destaque">TOTAL: R$ ${{totalFinal.toFixed(2)}}</div>
                `;
                return totalFinal;
            }}

            function abrirCheckout() {{
                const container = document.getElementById('itens-checkout');
                container.innerHTML = "";
                carrinho.forEach((item, idx) => {{
                    container.innerHTML += `
                        <div class="item-carrinho">
                            <span>${{item.nome}}</span>
                            <span>R$ ${{item.preco.toFixed(2)}} <button onclick="removerItem(${{idx}})" style="background:none; border:none; color:red; cursor:pointer;">✕</button></span>
                        </div>`;
                }});
                recalcularTotal();
                document.getElementById('modalCheckout').style.display = 'block';
            }}

            function removerItem(idx) {{
                carrinho.splice(idx, 1);
                if(carrinho.length === 0) {{
                    fecharCheckout();
                    document.getElementById('btn-cart-float').style.display = 'none';
                }} else {{
                    abrirCheckout();
                }}
                document.getElementById('cart-count').innerText = carrinho.length;
            }}

            async function buscarCep() {{
                const cepInput = document.getElementById('cep').value.replace(/\D/g,'');
                if(cepInput.length === 8) {{
                    try {{
                        const res = await fetch(\`https://viacep.com.br/ws/${{cepInput}}/json/\`);
                        const data = await res.json();
                        if(!data.erro) {{
                            // Exemplo de lógica de frete por estado
                            const sul_sudeste = ['SP','RJ','MG','ES','PR','SC','RS'];
                            if(sul_sudeste.includes(data.uf)) {{
                                freteValor = 90.00;
                                freteTexto = data.uf;
                            }} else {{
                                freteValor = 165.00;
                                freteTexto = data.uf;
                            }}
                            recalcularTotal();
                        }}
                    }} catch(e) {{ console.log("Erro CEP"); }}
                }}
            }}

            function fecharCheckout() {{ document.getElementById('modalCheckout').style.display = 'none'; }}

            function enviarPedido() {{
                const nome = document.getElementById('f_nome').value;
                const tel = document.getElementById('f_tel').value;
                if(!nome || !tel) return alert("Por favor, preencha nome e WhatsApp.");
                
                let subtotal = carrinho.reduce((acc, item) => acc + item.preco, 0);
                let total = recalcularTotal();
                
                let msg = "*PEDIDO G-LAB PEPTIDES*%0A%0A";
                msg += "*CLIENTE:* " + nome + "%0A";
                msg += "*WHATSAPP:* " + tel + "%0A";
                msg += "*ENDEREÇO:* " + document.getElementById('f_end').value + "%0A";
                msg += "*PAGAMENTO:* " + document.getElementById('f_pgto').value + "%0A%0A";
                msg += "*ITENS:*%0A";
                carrinho.forEach(i => msg += "- " + i.nome + " (R$ " + i.preco.toFixed(2) + ")%0A");
                msg += "%0A*SUBTOTAL:* R$ " + subtotal.toFixed(2);
                msg += "%0A*FRETE:* R$ " + freteValor.toFixed(2);
                msg += "%0A*TOTAL GERAL:* R$ " + total.toFixed(2);
                
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

# Carrega os dados mais recentes
df_estoque = carregar_dados_estoque()

with st.sidebar:
    st.image("1.png", width=120)
    menu = st.radio("Navegação", ["🛒 Site de Vendas", "🔐 Área Restrita"])

if menu == "🛒 Site de Vendas":
    # Aqui usamos o DataFrame para gerar o site dinâmico
    html_final = gerar_html_vendas(df_estoque)
    components.html(html_final, height=2000, scrolling=True)

else:
    if not st.session_state.logado:
        st.subheader("Acesso Administrativo")
        user = st.text_input("Usuário")
        pw = st.text_input("Senha", type="password")
        if st.button("Entrar"):
            if user == "admin" and pw == "glab2026":
                st.session_state.logado = True
                st.rerun()
            else:
                st.error("Credenciais inválidas")
    else:
        st.title("🛠️ Gestão de Inventário")
        tab1, tab2 = st.tabs(["📊 Ver Estoque", "💰 Registrar Venda Manual"])

        with tab1:
            st.dataframe(df_estoque, use_container_width=True)
            if st.button("Sair"):
                st.session_state.logado = False
                st.rerun()

        with tab2:
            st.subheader("Baixa Automática no Estoque")
            with st.form("baixa_form"):
                produto_nome = st.selectbox("Selecione o Produto", df_estoque['PRODUTO'].tolist())
                quantidade = st.number_input("Quantidade para retirar", min_value=1, step=1)
                
                if st.form_submit_button("Confirmar Baixa e Salvar"):
                    # Localiza o produto e subtrai a quantidade
                    idx = df_estoque[df_estoque['PRODUTO'] == produto_nome].index[0]
                    estoque_atual = df_estoque.at[idx, 'QTD']
                    
                    if estoque_atual >= quantidade:
                        novo_estoque = estoque_atual - quantidade
                        df_estoque.at[idx, 'QTD'] = novo_estoque
                        
                        # SALVA DE VOLTA NO EXCEL
                        salvar_dados_estoque(df_estoque)
                        
                        st.success(f"Estoque de {produto_nome} atualizado! Novo saldo: {novo_estoque}")
                    else:
                        st.error(f"Estoque insuficiente! Saldo atual: {estoque_atual}")

