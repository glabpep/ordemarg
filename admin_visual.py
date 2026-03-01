import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import os
import json

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="G-LAB PEPTIDES", layout="wide", page_icon="🧪")

# CSS para esconder lixo do Streamlit e fixar o layout
st.markdown("""
    <style>
        .block-container { padding: 0rem; }
        footer {visibility: hidden;}
        header {visibility: hidden;}
        [data-testid="stSidebar"] { background-color: #ffffff; border-right: 1px solid #eee; }
    </style>
""", unsafe_allow_html=True)

# --- PERSISTÊNCIA DE DADOS (EXCEL) ---
def carregar_dados():
    caminho = "stock_0202 - NOVA.xlsx"
    if os.path.exists(caminho):
        try:
            df = pd.read_excel(caminho)
            df.columns = [str(col).strip().upper() for col in df.columns]
            # Limpeza de dados para evitar ValueError
            if 'QTD' in df.columns:
                df['QTD'] = pd.to_numeric(df['QTD'], errors='coerce').fillna(0).astype(int)
            return df
        except Exception as e:
            st.error(f"Erro ao ler Excel: {e}")
            return pd.DataFrame()
    return pd.DataFrame()

def salvar_dados(df):
    try:
        df.to_excel("stock_0202 - NOVA.xlsx", index=False)
        return True
    except:
        return False

# --- MOTOR DO SITE (HTML/JS) ---
def gerar_html_vendas(df):
    # Preparar JSON de produtos para o JS
    prods_data = []
    for _, row in df.iterrows():
        prods_data.append({
            "nome": str(row.get('PRODUTO', 'N/A')),
            "espec": f"{row.get('VOLUME', '')} {row.get('MEDIDA', '')}",
            "preco": float(row.get('PREÇO (R$)', 0)),
            "disponivel": int(row.get('QTD', 0)) > 0
        })
    json_payload = json.dumps(prods_data)

    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: white; margin: 0; display: flex; overflow-x: hidden; }}
            .container {{ flex: 1; padding: 20px; max-width: 900px; margin: 0 auto; margin-right: 380px; }}
            
            /* Estilo dos Banners (Conforme Imagens) */
            .logo-wrap {{ text-align: center; margin-bottom: 30px; }}
            .logo-wrap img {{ width: 220px; }}
            .info-blue {{ background: #e8f4fd; color: #1a73e8; padding: 15px; border-radius: 8px; font-weight: 500; margin-bottom: 10px; border-left: 4px solid #1a73e8; font-size: 14px; }}
            .info-yellow {{ background: #fff9e6; color: #856404; padding: 15px; border-radius: 8px; font-size: 13px; border: 1px solid #ffeeba; margin-bottom: 20px; }}
            
            /* CEP e Tabela */
            .cep-section {{ border: 1px solid #004a99; border-radius: 10px; padding: 12px; display: flex; align-items: center; gap: 10px; margin-bottom: 20px; }}
            .cep-section input {{ border: none; outline: none; flex: 1; font-size: 16px; }}
            .btn-localizar {{ background: #28a745; color: white; border: none; padding: 8px 20px; border-radius: 6px; cursor: pointer; font-weight: bold; }}
            
            .table-head {{ background: #004a99; color: white; display: grid; grid-template-columns: 2fr 1fr 1fr 1fr; padding: 12px; border-radius: 8px 8px 0 0; font-weight: bold; }}
            .prod-row {{ display: grid; grid-template-columns: 2fr 1fr 1fr 1fr; padding: 15px 12px; border-bottom: 1px solid #eee; align-items: center; }}
            
            .badge {{ padding: 4px 8px; border-radius: 4px; font-size: 10px; font-weight: bold; }}
            .status-on {{ background: #e6fcf5; color: #0ca678; border: 1px solid #0ca678; }}
            .status-off {{ background: #fff5f5; color: #fa5252; border: 1px solid #fa5252; }}
            
            .btn-add {{ background: #004a99; color: white; border: none; padding: 8px; border-radius: 4px; cursor: pointer; width: 100%; font-weight: bold; }}
            .btn-wait {{ background: #f1f3f5; color: #adb5bd; border: none; padding: 8px; border-radius: 4px; width: 100%; cursor: not-allowed; }}

            /* Carrinho Lateral Azul */
            .sidebar-cart {{ width: 360px; background: #004a99; color: white; height: 100vh; position: fixed; right: 0; top: 0; padding: 25px; box-sizing: border-box; display: flex; flex-direction: column; }}
            .cart-items {{ flex: 1; overflow-y: auto; margin: 20px 0; }}
            .cart-item {{ display: flex; justify-content: space-between; font-size: 13px; margin-bottom: 10px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 5px; }}
            
            .total-area {{ background: rgba(0,0,0,0.2); padding: 15px; border-radius: 10px; }}
            .btn-checkout {{ background: white; color: #004a99; width: 100%; padding: 15px; border: none; border-radius: 8px; font-weight: bold; cursor: pointer; font-size: 16px; margin-top: 15px; }}

            /* Modal Pagamento */
            #modalPay {{ display:none; position:fixed; z-index:1000; left:0; top:0; width:100%; height:100%; background:rgba(0,0,0,0.7); }}
            .modal-box {{ background:white; width: 90%; max-width: 450px; margin: 50px auto; padding: 30px; border-radius: 15px; color: #333; }}
            .modal-box input, .modal-box select {{ width: 100%; padding: 12px; margin: 8px 0; border: 1px solid #ddd; border-radius: 6px; box-sizing: border-box; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="logo-wrap"><img src="https://github.com/glabpep/ordem/blob/main/1.png?raw=true"></div>
            
            <div class="info-blue"><i class="fas fa-truck"></i> Previsão de chegada de novos itens 09/03/2026, o estoque do site será atualizado!</div>
            <div class="info-yellow"><b>Aviso importante:</b> Os produtos são envasados em forma sólida... NOME DA SOLUÇÃO: BACTERIOSTATIC WATER.</div>

            <div class="cep-section">
                <i class="fas fa-map-marker-alt" style="color:#004a99"></i>
                <input type="text" id="cep-input" placeholder="Informe seu CEP para Localizar Região">
                <button class="btn-localizar" onclick="consultarCEP()">Localizar</button>
            </div>

            <div class="table-head">
                <div>PRODUTO</div><div>STATUS</div><div>VALOR</div><div>AÇÃO</div>
            </div>
            <div id="product-list"></div>
        </div>

        <div class="sidebar-cart">
            <div style="font-size: 18px; font-weight: bold; border-bottom: 1px solid rgba(255,255,255,0.3); padding-bottom: 10px;">
                <i class="fas fa-shopping-bag"></i> SEU PEDIDO <span id="cart-count" style="float:right">0</span>
            </div>
            <div id="cart-items" class="cart-items"></div>
            
            <div class="total-area">
                <input type="text" id="input-cupom" placeholder="CUPOM DE DESCONTO" oninput="recalcular()" style="width:100%; padding:8px; border-radius:5px; border:none; margin-bottom:10px;">
                <div id="frete-info" style="font-size: 11px; color: #ffeb3b; margin-bottom: 10px;"></div>
                <div style="display:flex; justify-content:space-between; font-size: 20px; font-weight:bold;">
                    <span>TOTAL:</span><span id="total-val">R$ 0,00</span>
                </div>
                <button class="btn-checkout" onclick="abrirModal()">Ir para Pagamento</button>
            </div>
        </div>

        <div id="modalPay">
            <div class="modal-box">
                <h3 style="margin-top:0; color:#004a99">Dados de Entrega</h3>
                <input type="text" id="f_nome" placeholder="Nome Completo">
                <input type="text" id="f_end" placeholder="Endereço (Rua, Nº, Bairro)">
                <div style="display:flex; gap:10px;">
                    <input type="text" id="f_cidade" placeholder="Cidade">
                    <input type="text" id="f_uf" placeholder="UF" maxlength="2">
                </div>
                <input type="text" id="f_whats" placeholder="WhatsApp (DDD)">
                <select id="f_pgto">
                    <option value="Pix (5% Desconto)">Pix (5% Desconto)</option>
                    <option value="Cartão de Crédito">Cartão de Crédito</option>
                </select>
                <button onclick="finalizar()" style="background:#28a745; color:white; width:100%; padding:15px; border:none; border-radius:10px; font-weight:bold; cursor:pointer; font-size:16px;">FINALIZAR NO WHATSAPP</button>
                <center><a href="javascript:fecharModal()" style="color:#999; font-size:12px; text-decoration:none; display:block; margin-top:15px;">CANCELAR / VOLTAR</a></center>
            </div>
        </div>

        <script>
            const DATA = {json_payload};
            let cart = [];
            let vFrete = 0;

            function render() {{
                const container = document.getElementById('product-list');
                container.innerHTML = DATA.map((p, i) => `
                    <div class="prod-row">
                        <div><b>${{p.nome}}</b><br><small style="color:#666">${{p.espec}}</small></div>
                        <div><span class="badge ${{p.disponivel ? 'status-on' : 'status-off'}}">${{p.disponivel ? 'DISPONÍVEL' : 'EM ESPERA'}}</span></div>
                        <div>R$ ${{p.preco.toFixed(2)}}</div>
                        <div>
                            <button class="${{p.disponivel ? 'btn-add' : 'btn-wait'}}" onclick="${{p.disponivel ? `addCart(${{i}})` : ''}}">
                                ${{p.disponivel ? 'ADICIONAR' : '✕'}}
                            </button>
                        </div>
                    </div>
                `).join('');
            }}

            async function consultarCEP() {{
                const cep = document.getElementById('cep-input').value.replace(/\D/g,'');
                if(cep.length !== 8) return alert("CEP Inválido");
                
                try {{
                    const res = await fetch(\`https://viacep.com.br/ws/${{cep}}/json/\`);
                    const d = await res.json();
                    if(d.erro) throw new Error();

                    const sul_sudeste = ['SP','RJ','MG','ES','PR','SC','RS'];
                    vFrete = sul_sudeste.includes(d.uf) ? 90.00 : 165.00;
                    
                    document.getElementById('frete-info').innerText = \`🚚 Frete para ${{d.uf}}: R$ ${{vFrete.toFixed(2)}}\`;
                    document.getElementById('f_cidade').value = d.localidade;
                    document.getElementById('f_uf').value = d.uf;
                    recalcular();
                }} catch(e) {{ alert("Erro ao buscar CEP"); }}
            }}

            function addCart(i) {{
                cart.push(DATA[i]);
                recalcular();
            }}

            function recalcular() {{
                const list = document.getElementById('cart-items');
                list.innerHTML = cart.map((item, idx) => \`
                    <div class="cart-item">
                        <span>\${{item.nome}}</span>
                        <span>R$ \${{item.preco.toFixed(2)}} <i class="fas fa-times" onclick="remove(\${{idx}})" style="color:red; cursor:pointer; margin-left:5px;"></i></span>
                    </div>
                \`).join('');

                let sub = cart.reduce((a, b) => a + b.preco, 0);
                const cupom = document.getElementById('input-cupom').value.toUpperCase();
                let desc = (cupom === "CABRAL5" || cupom === "BRUNA5") ? 0.05 : 0;
                
                let total = (sub * (1 - desc)) + (cart.length > 0 ? vFrete : 0);
                document.getElementById('total-val').innerText = "R$ " + total.toLocaleString('pt-BR', {{minimumFractionDigits:2}});
                document.getElementById('cart-count').innerText = cart.length;
            }}

            function remove(i) {{ cart.splice(i, 1); recalcular(); }}
            function abrirModal() {{ if(cart.length > 0) document.getElementById('modalPay').style.display='block'; }}
            function fecharModal() {{ document.getElementById('modalPay').style.display='none'; }}

            function finalizar() {{
                const nome = document.getElementById('f_nome').value;
                if(!nome) return alert("Preencha seu nome");
                
                let msg = "*NOVO PEDIDO G-LAB*%0A%0A";
                msg += "*Cliente:* " + nome + "%0A";
                msg += "*Endereço:* " + document.getElementById('f_end').value + " - " + document.getElementById('f_cidade').value + "/" + document.getElementById('f_uf').value + "%0A%0A";
                msg += "*ITENS:*%0A" + cart.map(i => "- " + i.nome).join("%0A");
                msg += "%0A%0A*TOTAL:* " + document.getElementById('total-val').innerText;
                
                window.open("https://wa.me/17746222523?text=" + msg);
            }}

            render();
        </script>
    </body>
    </html>
    """
    return html_code

# --- LÓGICA DO APP ---
df_estoque = carregar_dados()

with st.sidebar:
    st.image("https://github.com/glabpep/ordem/blob/main/1.png?raw=true", width=150)
    menu = st.radio("Menu", ["🛒 Loja Online", "👥 Área do Funcionário"])

if menu == "🛒 Loja Online":
    components.html(gerar_html_vendas(df_estoque), height=1500, scrolling=True)

else:
    # Sistema de Login
    if "autenticado" not in st.session_state: st.session_state.autenticado = False

    if not st.session_state.autenticado:
        st.subheader("Acesso Restrito")
        user = st.text_input("Usuário")
        passw = st.text_input("Senha", type="password")
        if st.button("Entrar"):
            if user == "admin" and passw == "glab2026":
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.error("Credenciais inválidas")
    else:
        st.title("📦 Painel de Controle")
        tab1, tab2 = st.tabs(["Estoque Atual", "Dar Baixa"])

        with tab1:
            st.dataframe(df_estoque, use_container_width=True)
            if st.button("Logout"):
                st.session_state.autenticado = False
                st.rerun()

        with tab2:
            st.write("Registre uma venda manual para atualizar o Excel:")
            prod_sel = st.selectbox("Selecione o Produto", df_estoque['PRODUTO'].tolist())
            qtd_baixa = st.number_input("Quantidade vendida", min_value=1, value=1)
            
            if st.button("Confirmar Baixa e Salvar Excel"):
                idx = df_estoque[df_estoque['PRODUTO'] == prod_sel].index[0]
                if df_estoque.at[idx, 'QTD'] >= qtd_baixa:
                    df_estoque.at[idx, 'QTD'] -= qtd_baixa
                    if salvar_dados(df_estoque):
                        st.success(f"Baixa realizada! {prod_sel} agora tem {df_estoque.at[idx, 'QTD']} unidades.")
                        st.rerun()
                    else:
                        st.error("Erro ao salvar no Excel. Verifique se o arquivo está aberto.")
                else:
                    st.error("Quantidade em estoque insuficiente!")
