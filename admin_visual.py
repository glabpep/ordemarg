import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import os
import json
import requests

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="G-LAB PEPTIDES", layout="wide", page_icon="🧪")

# Esconder elementos do Streamlit
st.markdown("""
    <style>
        .block-container { padding: 0rem; }
        iframe { border: none; }
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        [data-testid="stSidebar"] { background-color: #f8f9fa; }
    </style>
""", unsafe_allow_html=True)

# --- FUNÇÕES DE NÚCLEO (ESTOQUE E FRETE) ---
def carregar_dados():
    caminho = os.path.join(os.path.dirname(__file__), 'stock_0202 - NOVA.xlsx')
    if os.path.exists(caminho):
        try:
            df = pd.read_excel(caminho)
            df.columns = [str(col).strip().upper() for col in df.columns]
            if 'QTD' in df.columns:
                df['QTD'] = pd.to_numeric(df['QTD'], errors='coerce').fillna(0).astype(int)
            return df
        except: return pd.DataFrame()
    return pd.DataFrame()

def salvar_dados(df):
    caminho = os.path.join(os.path.dirname(__file__), 'stock_0202 - NOVA.xlsx')
    df.to_excel(caminho, index=False)

# --- GERADOR DO SITE COMPLETO ---
def gerar_site_vendas(df_estoque):
    # Processamento de produtos para o catálogo
    produtos_info = []
    for _, row in df_estoque.iterrows():
        qtd = int(row.get('QTD', 0))
        produtos_info.append({
            "nome": str(row.get('PRODUTO', 'N/A')),
            "espec": f"{row.get('VOLUME', '')} {row.get('MEDIDA', '')}",
            "preco": float(row.get('PREÇO (R$)', 0)),
            "disponivel": qtd > 0
        })
    produtos_json = json.dumps(produtos_info)

    html_content = f"""
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        <style>
            :root {{ --main-blue: #004a99; --accent-green: #25d366; }}
            body {{ font-family: 'Segoe UI', sans-serif; background: #f4f7f6; margin: 0; display: flex; overflow-x: hidden; }}
            
            /* Catálogo Lateral */
            .catalog-container {{ flex: 1; padding: 30px; max-width: 850px; margin: 0 auto; margin-right: 370px; }}
            .logo-header {{ text-align: center; margin-bottom: 20px; }}
            .logo-header img {{ max-width: 220px; }}
            
            .product-table {{ width: 100%; border-collapse: collapse; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }}
            .product-table th {{ background: var(--main-blue); color: white; padding: 15px; text-align: left; }}
            .product-row td {{ padding: 15px; border-bottom: 1px solid #eee; }}
            
            .badge {{ padding: 4px 8px; border-radius: 4px; font-size: 10px; font-weight: bold; }}
            .bg-success {{ background: #e6fcf5; color: #0ca678; border: 1px solid #0ca678; }}
            .bg-danger {{ background: #fff5f5; color: #fa5252; border: 1px solid #fa5252; }}
            
            .btn-add {{ background: var(--accent-green); color: white; border: none; padding: 8px 12px; border-radius: 6px; cursor: pointer; font-weight: bold; }}
            .btn-disabled {{ background: #dee2e6; color: #adb5bd; cursor: not-allowed; }}

            /* Sidebar do Carrinho - DESIGN DAS FOTOS */
            .cart-sidebar {{ width: 360px; background: var(--main-blue); color: white; height: 100vh; position: fixed; right: 0; top: 0; padding: 25px; box-sizing: border-box; display: flex; flex-direction: column; z-index: 100; }}
            .cart-header {{ font-size: 18px; font-weight: bold; margin-bottom: 20px; display: flex; justify-content: space-between; }}
            .cart-items {{ flex: 1; overflow-y: auto; background: rgba(255,255,255,0.05); border-radius: 10px; padding: 10px; margin-bottom: 15px; }}
            .cart-item {{ display: flex; justify-content: space-between; margin-bottom: 12px; font-size: 13px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 8px; }}
            
            .cart-inputs {{ background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; margin-bottom: 15px; }}
            input {{ width: 100%; padding: 10px; margin-bottom: 8px; border-radius: 6px; border: none; box-sizing: border-box; }}
            
            .total-box {{ font-size: 20px; font-weight: bold; border-top: 1px solid rgba(255,255,255,0.3); padding-top: 15px; margin-top: 5px; }}
            .btn-pay {{ background: white; color: var(--main-blue); border: none; width: 100%; padding: 16px; border-radius: 8px; font-weight: bold; cursor: pointer; font-size: 16px; transition: 0.3s; }}
            .btn-pay:hover {{ background: #eef2f3; }}

            /* Modal Finalização */
            #modalPayment {{ display:none; position:fixed; z-index:1001; left:0; top:0; width:100%; height:100%; background:rgba(0,0,0,0.8); }}
            .modal-content {{ background:white; margin: 3% auto; padding: 30px; width: 90%; max-width: 480px; border-radius: 20px; color: #333; }}
        </style>
    </head>
    <body>
        <div class="catalog-container">
            <div class="logo-header"><img src="https://github.com/glabpep/ordem/blob/main/1.png?raw=true"></div>
            <table class="product-table">
                <thead><tr><th>PRODUTO</th><th>STATUS</th><th>VALOR</th><th>ADICIONAR</th></tr></thead>
                <tbody id="lista-corpo"></tbody>
            </table>
        </div>

        <div class="cart-sidebar">
            <div class="cart-header"><span><i class="fas fa-shopping-bag"></i> SEU PEDIDO</span> <span id="cart-count">0</span></div>
            <div id="cart-items" class="cart-items"></div>
            
            <div class="cart-inputs">
                <input type="text" id="cep" placeholder="Informe seu CEP" onblur="calcularFreteAPI()">
                <div id="frete-status" style="font-size: 11px; color: #ffeb3b; margin-bottom: 10px;"></div>
                <input type="text" id="cupom" placeholder="CUPOM DE DESCONTO" oninput="recalcular()">
            </div>

            <div class="total-box">
                <div style="font-size:12px; font-weight:normal; opacity:0.8;">Subtotal + Frete:</div>
                <div id="total-val">R$ 0,00</div>
            </div>
            <button class="btn-pay" onclick="abrirPagamento()">IR PARA PAGAMENTO</button>
        </div>

        <div id="modalPayment">
            <div class="modal-content">
                <h3 style="margin-top:0; color:var(--main-blue);"><i class="fas fa-map-marker-alt"></i> Dados para Entrega</h3>
                <input type="text" id="f_nome" placeholder="Nome Completo">
                <input type="text" id="f_end" placeholder="Endereço Completo (Rua, Nº, Bairro)">
                <div style="display:grid; grid-template-columns: 1fr 1fr; gap:10px;">
                    <input type="text" id="f_cid" placeholder="Cidade">
                    <input type="text" id="f_uf" placeholder="UF">
                </div>
                <input type="text" id="f_whats" placeholder="WhatsApp">
                <select id="f_pgto" style="width:100%; padding:12px; border-radius:6px; margin-top:5px; border:1px solid #ddd;">
                    <option value="Pix (5% Desconto)">Pix (5% Desconto)</option>
                    <option value="Cartão de Crédito">Cartão de Crédito</option>
                </select>
                <button onclick="enviarWA()" style="background:var(--accent-green); color:white; width:100%; padding:16px; border:none; border-radius:10px; margin-top:20px; font-weight:bold; cursor:pointer;">FINALIZAR NO WHATSAPP</button>
                <center><a href="javascript:void(0)" onclick="fecharPagamento()" style="color:#999; font-size:13px; text-decoration:none; display:block; margin-top:15px;">Voltar ao carrinho</a></center>
            </div>
        </div>

        <script>
            const PRODS = {produtos_json};
            let cart = [];
            let freteValor = 0;
            let cupomDesc = 0;

            function render() {{
                const tbody = document.getElementById('lista-corpo');
                tbody.innerHTML = PRODS.map((p, i) => `
                    <tr class="product-row">
                        <td><b>${{p.nome}}</b><br><small style="color:#888;">${{p.espec}}</small></td>
                        <td><span class="badge ${{p.disponivel ? 'bg-success' : 'bg-danger'}}">${{p.disponivel ? 'DISPONÍVEL' : 'EM ESPERA'}}</span></td>
                        <td>R$ ${{p.preco.toFixed(2)}}</td>
                        <td><button class="${{p.disponivel ? 'btn-add' : 'btn-add btn-disabled'}}" onclick="${{p.disponivel ? `addCart(${{i}})` : ''}}">${{p.disponivel ? '+' : '✕'}}</button></td>
                    </tr>
                `).join('');
            }}

            function addCart(i) {{
                cart.push(PRODS[i]);
                document.getElementById('cart-count').innerText = cart.length;
                recalcular();
            }}

            async function calcularFreteAPI() {{
                const cep = document.getElementById('cep').value.replace(/\D/g,'');
                if(cep.length !== 8) return;
                
                document.getElementById('frete-status').innerText = "Calculando frete...";
                try {{
                    const res = await fetch(\`https://viacep.com.br/ws/${{cep}}/json/\`);
                    const data = await res.json();
                    if(data.erro) throw new Error();
                    
                    const sul_sudeste = ['SP','RJ','MG','ES','PR','SC','RS'];
                    freteValor = sul_sudeste.includes(data.uf) ? 90.00 : 165.00;
                    document.getElementById('frete-status').innerText = \`✓ Frete para ${{data.uf}}: R$ ${{freteValor.toFixed(2)}}\`;
                    document.getElementById('f_cid').value = data.localidade;
                    document.getElementById('f_uf').value = data.uf;
                    recalcular();
                }} catch(e) {{
                    document.getElementById('frete-status').innerText = "CEP não localizado. Frete padrão R$ 90,00";
                    freteValor = 90;
                    recalcular();
                }}
            }}

            function recalcular() {{
                let sub = cart.reduce((a, b) => a + b.preco, 0);
                const cp = document.getElementById('cupom').value.toUpperCase();
                cupomDesc = (cp === "CABRAL5" || cp === "BRUNA5") ? 0.05 : 0;
                
                let total = (sub * (1 - cupomDesc)) + (cart.length > 0 ? freteValor : 0);
                document.getElementById('total-val').innerText = "R$ " + total.toLocaleString('pt-BR', {{minimumFractionDigits: 2}});
                
                const itemsDiv = document.getElementById('cart-items');
                itemsDiv.innerHTML = cart.map((item, idx) => \`
                    <div class="cart-item">
                        <span>\${{item.nome}}</span>
                        <span>R$ \${{item.preco.toFixed(2)}} <i class="fas fa-trash" onclick="remove(\${{idx}})" style="color:#ff6b6b; cursor:pointer;"></i></span>
                    </div>
                \`).join('');
            }}

            function remove(idx) {{ cart.splice(idx,1); recalcular(); }}
            function abrirPagamento() {{ if(cart.length > 0) document.getElementById('modalPayment').style.display='block'; }}
            function fecharPagamento() {{ document.getElementById('modalPayment').style.display='none'; }}

            function enviarWA() {{
                let n = document.getElementById('f_nome').value;
                if(!n) return alert("Preencha seu nome");
                let msg = "*NOVO PEDIDO G-LAB*%0A%0A*Cliente:* " + n + "%0A*WhatsApp:* " + document.getElementById('f_whats').value + "%0A%0A*ITENS:*%0A" + cart.map(i => "- " + i.nome).join("%0A");
                msg += "%0A%0A*TOTAL:* " + document.getElementById('total-val').innerText;
                window.open("https://wa.me/17746222523?text=" + msg);
            }}

            render();
        </script>
    </body>
    </html>
    """
    return html_content

# --- LÓGICA DE NAVEGAÇÃO E ADMIN ---
df_estoque = carregar_dados()

with st.sidebar:
    st.image("https://github.com/glabpep/ordem/blob/main/1.png?raw=true", width=120)
    escolha = st.radio("Navegação", ["🛒 Site de Vendas", "🔐 Área Restrita"])

if escolha == "🛒 Site de Vendas":
    components.html(gerar_site_vendas(df_estoque), height=1800, scrolling=True)

else:
    if "logado" not in st.session_state: st.session_state.logado = False
    
    if not st.session_state.logado:
        st.subheader("Login G-LAB")
        user = st.text_input("Usuário")
        pw = st.text_input("Senha", type="password")
        if st.button("Acessar"):
            if user == "admin" and pw == "glab2026":
                st.session_state.logado = True
                st.rerun()
            else: st.error("Incorreto")
    else:
        st.title("🛠️ Painel de Controle de Estoque")
        tab1, tab2 = st.tabs(["📊 Ver Estoque", "📦 Registrar Venda"])
        
        with tab1:
            st.dataframe(df_estoque, use_container_width=True)
            if st.button("Sair"):
                st.session_state.logado = False
                st.rerun()
        
        with tab2:
            st.write("Baixa de Estoque por Venda Manual:")
            prod_sel = st.selectbox("Selecione o Produto", df_estoque['PRODUTO'].tolist())
            qtd_venda = st.number_input("Quantidade vendida", min_value=1, value=1)
            
            if st.button("Confirmar Baixa e Salvar no Excel"):
                idx = df_estoque[df_estoque['PRODUTO'] == prod_sel].index[0]
                if df_estoque.at[idx, 'QTD'] >= qtd_venda:
                    df_estoque.at[idx, 'QTD'] -= qtd_venda
                    salvar_dados(df_estoque) # PERSISTÊNCIA NO EXCEL
                    st.success(f"Estoque de {prod_sel} atualizado! Novo saldo: {df_estoque.at[idx, 'QTD']}")
                    st.rerun()
                else:
                    st.error("Quantidade maior que o estoque disponível!")
