import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import os
import json

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="G-LAB PEPTIDES", layout="wide", page_icon="🧪")

# Esconde elementos padrão do Streamlit
st.markdown("""
    <style>
        .block-container { padding: 0rem; }
        iframe { border: none; }
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- FUNÇÕES DE DADOS ---
def carregar_dados():
    caminho = os.path.join(os.path.dirname(__file__), 'stock_0202 - NOVA.xlsx')
    if os.path.exists(caminho):
        try:
            df = pd.read_excel(caminho)
            df.columns = [str(col).strip().upper() for col in df.columns]
            # Garante que QTD seja número para evitar ValueError
            if 'QTD' in df.columns:
                df['QTD'] = pd.to_numeric(df['QTD'], errors='coerce').fillna(0).astype(int)
            return df
        except: return pd.DataFrame()
    return pd.DataFrame()

def salvar_dados(df):
    caminho = os.path.join(os.path.dirname(__file__), 'stock_0202 - NOVA.xlsx')
    df.to_excel(caminho, index=False)

# --- GERADOR DO SITE (DESIGN AVANÇADO) ---
def gerar_site_vendas(df_estoque):
    # Prepara lista de produtos para o JavaScript
    produtos_lista = []
    for _, row in df_estoque.iterrows():
        qtd = int(row.get('QTD', 0))
        produtos_lista.append({
            "nome": str(row.get('PRODUTO', 'N/A')),
            "espec": f"{row.get('VOLUME', '')} {row.get('MEDIDA', '')}",
            "preco": float(row.get('PREÇO (R$)', 0)),
            "disponivel": qtd > 0
        })
    produtos_json = json.dumps(produtos_lista)

    html_content = f"""
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        <style>
            :root {{ --blue: #004a99; --green: #28a745; --light-bg: #f8f9fa; }}
            body {{ font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; background: var(--light-bg); margin: 0; display: flex; }}
            
            /* Main Content */
            .main-content {{ flex: 1; padding: 20px; max-width: 900px; margin: 0 auto; }}
            .logo-header {{ text-align: center; margin-bottom: 30px; }}
            .logo-header img {{ max-width: 250px; }}
            
            /* Banner de Aviso */
            .alert-banner {{ background: #e3f2fd; border-left: 5px solid #2196f3; padding: 15px; border-radius: 8px; margin-bottom: 20px; font-size: 14px; color: #0d47a1; }}
            .info-box {{ background: #fff3cd; border: 1px solid #ffeeba; padding: 15px; border-radius: 8px; margin-bottom: 25px; font-size: 13px; position: relative; }}
            
            /* Tabela de Produtos */
            .product-table {{ width: 100%; border-collapse: separate; border-spacing: 0 10px; }}
            .product-table th {{ background: var(--blue); color: white; padding: 12px; text-align: left; font-size: 14px; }}
            .product-table th:first-child {{ border-radius: 8px 0 0 0; }}
            .product-table th:last-child {{ border-radius: 0 8px 0 0; }}
            .product-row {{ background: white; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }}
            .product-row td {{ padding: 15px; border-top: 1px solid #eee; border-bottom: 1px solid #eee; }}
            
            /* Badges e Botões */
            .badge {{ padding: 5px 10px; border-radius: 4px; font-size: 11px; font-weight: bold; border: 1px solid; }}
            .badge-espera {{ color: #dc3545; border-color: #dc3545; background: #fff5f5; }}
            .badge-disponivel {{ color: #28a745; border-color: #28a745; background: #f6fff6; }}
            .btn-action {{ width: 40px; height: 30px; border: none; border-radius: 5px; cursor: pointer; color: white; font-weight: bold; }}
            .btn-plus {{ background: var(--green); }}
            .btn-wait {{ background: #e0e0e0; color: #999; cursor: not-allowed; }}

            /* Carrinho Lateral */
            .cart-sidebar {{ width: 350px; background: var(--blue); color: white; height: 100vh; position: fixed; right: 0; top: 0; padding: 20px; box-sizing: border-box; display: flex; flex-direction: column; }}
            .cart-title {{ font-size: 18px; margin-bottom: 20px; display: flex; justify-content: space-between; }}
            .cart-items {{ flex: 1; overflow-y: auto; background: rgba(255,255,255,0.1); border-radius: 8px; padding: 10px; }}
            .cart-item {{ display: flex; justify-content: space-between; margin-bottom: 10px; font-size: 13px; border-bottom: 1px solid rgba(255,255,255,0.2); padding-bottom: 5px; }}
            .cart-footer {{ margin-top: 20px; padding-top: 15px; border-top: 1px solid white; }}
            .total-row {{ font-size: 20px; font-weight: bold; display: flex; justify-content: space-between; margin: 15px 0; }}
            .btn-checkout {{ background: white; color: var(--blue); border: none; width: 100%; padding: 15px; border-radius: 8px; font-weight: bold; cursor: pointer; }}

            /* Modal Endereço */
            #modalAddress {{ display:none; position:fixed; z-index:1000; left:0; top:0; width:100%; height:100%; background:rgba(0,0,0,0.7); }}
            .modal-content {{ background:white; margin: 5% auto; padding: 25px; width: 90%; max-width: 500px; border-radius: 15px; }}
            .form-grid {{ display: grid; grid-template-columns: 2fr 1fr; gap: 10px; }}
        </style>
    </head>
    <body>
        <div class="main-content">
            <div class="logo-header">
                <img src="https://github.com/glabpep/ordem/blob/main/1.png?raw=true">
            </div>

            <div class="alert-banner">
                <i class="fas fa-truck-loading"></i> Previsão de chegada de novos itens <b>09/03/2026</b>, o estoque do site será atualizado!
            </div>

            <div class="info-box">
                <b>Aviso importante:</b> Os produtos são envasados em forma sólida... <b>NOME DA SOLUÇÃO:</b> BACTERIOSTATIC WATER.
            </div>

            <table class="product-table">
                <thead>
                    <tr><th>Produto</th><th>Status</th><th>Preço</th><th>Ação</th></tr>
                </thead>
                <tbody id="lista-corpo"></tbody>
            </table>
        </div>

        <div class="cart-sidebar">
            <div class="cart-title"><span><i class="fas fa-shopping-cart"></i> Seu Pedido</span> <i class="fas fa-chevron-down"></i></div>
            <div id="cart-items" class="cart-items"></div>
            
            <div class="cart-footer">
                <div style="display:flex; gap:5px; margin-bottom:10px;">
                    <input type="text" id="cupom" placeholder="Cupom" style="flex:1; padding:8px; border-radius:4px; border:none;">
                    <button onclick="aplicarCupom()" style="padding:8px; background:#ffeb3b; border:none; border-radius:4px; font-weight:bold;">Aplicar</button>
                </div>
                <div id="frete-info" style="font-size:12px; color:#ffeb3b; margin-bottom:5px;"></div>
                <div class="total-row"><span>TOTAL GERAL:</span> <span id="total-val">R$ 0,00</span></div>
                <button class="btn-checkout" onclick="abrirCheckout()">Ir para Pagamento</button>
            </div>
        </div>

        <div id="modalAddress">
            <div class="modal-content">
                <h3 style="color:var(--blue); margin-top:0;"><i class="fas fa-box"></i> Dados de Entrega</h3>
                <input type="text" id="f_nome" placeholder="Nome Completo">
                <input type="text" id="f_rua" placeholder="Rua / Logradouro">
                <div class="form-grid">
                    <input type="text" id="f_num" placeholder="Nº">
                    <input type="text" id="f_bairro" placeholder="Bairro">
                </div>
                <div class="form-grid">
                    <input type="text" id="f_cidade" placeholder="Cidade">
                    <input type="text" id="f_uf" placeholder="UF">
                </div>
                <input type="text" id="f_whats" placeholder="WhatsApp com DDD">
                <select id="f_pgto" style="width:100%; padding:10px; margin-top:10px; border-radius:5px;">
                    <option value="Pix (Aprovação Imediata)">Pix (Aprovação Imediata)</option>
                    <option value="Cartão de Crédito">Cartão de Crédito</option>
                </select>
                <button onclick="finalizar()" style="background:var(--blue); color:white; width:100%; padding:15px; border:none; border-radius:8px; margin-top:15px; font-weight:bold; cursor:pointer;">ENVIAR PARA WHATSAPP</button>
                <center><a href="#" onclick="fecharCheckout()" style="color:#999; font-size:12px; display:block; margin-top:10px;">Cancelar / Voltar</a></center>
            </div>
        </div>

        <script>
            const PRODS = {produtos_json};
            let cart = [];
            let desc = 0;
            let frete = 90;

            function render() {{
                const corpo = document.getElementById('lista-corpo');
                corpo.innerHTML = PRODS.map((p, i) => `
                    <tr class="product-row">
                        <td><b>${{p.nome}}</b><br><small style="color:#666;">${{p.espec}}</small></td>
                        <td><span class="badge ${{p.disponivel ? 'badge-disponivel' : 'badge-espera'}}">${{p.disponivel ? 'DISPONÍVEL' : 'EM ESPERA'}}</span></td>
                        <td>R$ ${{p.preco.toFixed(2)}}</td>
                        <td>
                            <button class="btn-action ${{p.disponivel ? 'btn-plus' : 'btn-wait'}}" 
                                    onclick="${{p.disponivel ? `addCart(${{i}})` : ''}}">
                                ${{p.disponivel ? '+' : '✕'}}
                            </button>
                        </td>
                    </tr>
                `).join('');
            }}

            function addCart(i) {{
                cart.push(PRODS[i]);
                atualizarCart();
            }}

            function atualizarCart() {{
                const div = document.getElementById('cart-items');
                div.innerHTML = cart.map((item, idx) => `
                    <div class="cart-item">
                        <span>${{item.nome}}</span>
                        <span>R$ ${{item.preco.toFixed(2)}} <i class="fas fa-times-circle" onclick="remover(${{idx}})" style="cursor:pointer; color:#ff6b6b;"></i></span>
                    </div>
                `).join('');
                
                let sub = cart.reduce((a, b) => a + b.preco, 0);
                let total = (sub - (sub * desc)) + (cart.length > 0 ? frete : 0);
                document.getElementById('total-val').innerText = "R$ " + total.toFixed(2);
                document.getElementById('frete-info').innerText = cart.length > 0 ? "🚚 Frete fixo SUL/SUDESTE: R$ 90,00" : "";
            }}

            function aplicarCupom() {{
                const c = document.getElementById('cupom').value.toUpperCase();
                if(c === "CABRAL5" || c === "BRUNA5") {{ desc = 0.05; alert("Cupom 5% aplicado!"); }}
                else {{ desc = 0; alert("Cupom inválido"); }}
                atualizarCart();
            }}

            function remover(idx) {{ cart.splice(idx, 1); atualizarCart(); }}
            function abrirCheckout() {{ if(cart.length > 0) document.getElementById('modalAddress').style.display = 'block'; }}
            function fecharCheckout() {{ document.getElementById('modalAddress').style.display = 'none'; }}

            function finalizar() {{
                let nome = document.getElementById('f_nome').value;
                if(!nome) return alert("Preencha seu nome");
                let msg = "*NOVO PEDIDO G-LAB*%0A%0A*Cliente:* " + nome + "%0A*Endereço:* " + document.getElementById('f_rua').value + "%0A*WhatsApp:* " + document.getElementById('f_whats').value + "%0A%0A*ITENS:*%0A";
                cart.forEach(i => msg += "- " + i.nome + "%0A");
                msg += "%0A*TOTAL GERAL:* " + document.getElementById('total-val').innerText;
                window.open("https://wa.me/17746222523?text=" + msg);
            }}

            render();
        </script>
    </body>
    </html>
    """
    return html_content

# --- NAVEGAÇÃO STREAMLIT ---
df = carregar_dados()

with st.sidebar:
    st.image("https://github.com/glabpep/ordem/blob/main/1.png?raw=true", width=150)
    menu = st.radio("Navegação", ["🛒 Site de Vendas", "🔐 Área do Funcionário"])

if menu == "🛒 Site de Vendas":
    components.html(gerar_site_vendas(df), height=2000, scrolling=True)

else:
    if "autenticado" not in st.session_state: st.session_state.autenticado = False
    
    if not st.session_state.autenticado:
        st.subheader("Login G-LAB")
        u = st.text_input("Usuário")
        s = st.text_input("Senha", type="password")
        if st.button("Entrar"):
            if u == "admin" and s == "glab2026":
                st.session_state.autenticado = True
                st.rerun()
    else:
        st.title("⚙️ Gestão de Estoque")
        aba1, aba2 = st.tabs(["📊 Ver Inventário", "💰 Registrar Venda"])
        
        with aba1:
            st.dataframe(df, use_container_width=True)
            if st.button("Logout"): 
                st.session_state.autenticado = False
                st.rerun()
        
        with aba2:
            st.write("Selecione o produto para dar baixa:")
            prod_nome = st.selectbox("Produto", df['PRODUTO'].unique())
            qtd_retirar = st.number_input("Quantidade vendida", min_value=1, value=1)
            
            if st.button("Confirmar Baixa"):
                idx = df[df['PRODUTO'] == prod_nome].index[0]
                estoque_atual = df.at[idx, 'QTD']
                
                if estoque_atual >= qtd_retirar:
                    df.at[idx, 'QTD'] = estoque_atual - qtd_retirar
                    salvar_dados(df) # SALVA NO EXCEL REAL
                    st.success(f"Estoque atualizado! Novo saldo de {prod_nome}: {df.at[idx, 'QTD']}")
                    st.rerun()
                else:
                    st.error("Estoque insuficiente!")
