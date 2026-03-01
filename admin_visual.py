import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import os
import json

# --- 1. CONFIGURAÇÃO E ESTADO ---
st.set_page_config(page_title="G-LAB PEPTIDES", layout="wide", page_icon="🧪")

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

# CSS para limpar a interface e garantir responsividade no Streamlit
st.markdown("""
    <style>
        .block-container { padding: 0rem; }
        footer {visibility: hidden;}
        header {visibility: hidden;}
        [data-testid="stSidebar"] { background-color: #f8f9fa; border-right: 1px solid #ddd; }
        
        /* Ajuste para mobile no Streamlit */
        @media (max-width: 768px) {
            .stMain { padding: 0px; }
        }
    </style>
""", unsafe_allow_html=True)

# --- 2. BASE DE DADOS (EXCEL) ---
def carregar_estoque():
    caminho = "stock_0202 - NOVA.xlsx"
    if os.path.exists(caminho):
        try:
            df = pd.read_excel(caminho)
            df.columns = [str(col).strip().upper() for col in df.columns]
            if 'QTD' in df.columns:
                df['QTD'] = pd.to_numeric(df['QTD'], errors='coerce').fillna(0).astype(int)
            if 'PREÇO (R$)' in df.columns:
                df['PREÇO (R$)'] = pd.to_numeric(df['PREÇO (R$)'], errors='coerce').fillna(0)
            return df
        except:
            return pd.DataFrame(columns=['PRODUTO', 'VOLUME', 'MEDIDA', 'PREÇO (R$)', 'QTD'])
    return pd.DataFrame()

def salvar_estoque(df):
    df.to_excel("stock_0202 - NOVA.xlsx", index=False)

# --- 3. FRONT-END (HTML/JS/CSS RESPONSIVO) ---
def gerar_interface_vendas(df):
    produtos_json = []
    for _, row in df.iterrows():
        produtos_json.append({
            "nome": str(row.get('PRODUTO', 'Sem Nome')),
            "espec": f"{row.get('VOLUME', '')} {row.get('MEDIDA', '')}",
            "preco": float(row.get('PREÇO (R$)', 0)),
            "estoque": int(row.get('QTD', 0))
        })
    
    json_data = json.dumps(produtos_json)

    html_code = f"""
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; background-color: #fff; display: flex; flex-direction: column; overflow-x: hidden; }}
            
            /* Ajuste de Layout Principal */
            .main-content {{ flex: 1; padding: 15px; max-width: 100%; margin: 0 auto; box-sizing: border-box; padding-bottom: 120px; }}
            
            /* Banners Responsivos */
            .banner-blue {{ background: #e3f2fd; color: #0d47a1; padding: 12px; border-radius: 8px; border-left: 6px solid #2196f3; font-size: 13px; margin-bottom: 10px; font-weight: 500; }}
            .banner-yellow {{ background: #fff9c4; color: #856404; padding: 12px; border-radius: 8px; font-size: 12px; border: 1px solid #ffeeba; margin-bottom: 20px; }}
            
            /* Busca/CEP */
            .cep-container {{ border: 2px solid #004a99; border-radius: 10px; padding: 8px; display: flex; align-items: center; gap: 8px; margin-bottom: 25px; }}
            .cep-container input {{ border: none; outline: none; flex: 1; font-size: 14px; min-width: 50px; }}
            .btn-cep {{ background: #28a745; color: white; border: none; padding: 8px 15px; border-radius: 6px; cursor: pointer; font-weight: bold; font-size: 13px; }}

            /* Tabela de Itens Responsiva (Grid Dinâmico) */
            .tabela-header {{ background: #004a99; color: white; display: grid; grid-template-columns: 2fr 1fr 1fr 1fr; padding: 12px; border-radius: 8px 8px 0 0; font-weight: bold; font-size: 12px; }}
            .tabela-row {{ display: grid; grid-template-columns: 2fr 1fr 1fr 1fr; padding: 12px; border-bottom: 1px solid #eee; align-items: center; font-size: 13px; }}
            
            .badge {{ padding: 4px 6px; border-radius: 4px; font-size: 10px; font-weight: bold; text-align: center; display: inline-block; }}
            .bg-green {{ background: #e6fcf5; color: #0ca678; border: 1px solid #0ca678; }}
            .bg-red {{ background: #fff5f5; color: #fa5252; border: 1px solid #fa5252; }}
            
            .btn-add {{ background: #004a99; color: white; border: none; padding: 8px; border-radius: 5px; cursor: pointer; width: 100%; font-weight: bold; font-size: 12px; }}
            .btn-disabled {{ background: #e9ecef; color: #adb5bd; border: none; padding: 8px; border-radius: 5px; width: 100%; cursor: not-allowed; font-size: 12px; }}

            /* Carrinho: Lateral no Desktop, Barra Inferior no Mobile */
            .sidebar-cart {{ 
                width: 350px; background: #004a99; color: white; height: 100vh; position: fixed; right: 0; top: 0; 
                padding: 25px; box-sizing: border-box; display: flex; flex-direction: column; box-shadow: -5px 0 15px rgba(0,0,0,0.1); 
                transition: transform 0.3s ease; z-index: 1000;
            }}

            /* Media Query para Mobile (Celulares) */
            @media (max-width: 900px) {{
                .main-content {{ margin-right: 0; }}
                .sidebar-cart {{ 
                    width: 100%; height: auto; top: auto; bottom: 0; padding: 15px; 
                    border-radius: 20px 20px 0 0; box-shadow: 0 -5px 15px rgba(0,0,0,0.2);
                }}
                .cart-items {{ display: none; }} /* Esconde lista detalhada no mobile para ganhar espaço */
                .cart-title {{ font-size: 16px; margin-bottom: 10px; padding-bottom: 5px; }}
                .total-row {{ font-size: 18px; margin: 10px 0; }}
                .btn-checkout {{ padding: 12px; font-size: 16px; }}
                .tabela-header {{ font-size: 10px; padding: 8px; }}
                .tabela-row {{ font-size: 11px; padding: 8px; }}
            }}

            .cart-title {{ font-weight: bold; border-bottom: 1px solid rgba(255,255,255,0.2); padding-bottom: 15px; margin-bottom: 15px; }}
            .cart-items {{ flex: 1; overflow-y: auto; font-size: 14px; }}
            .cart-item {{ display: flex; justify-content: space-between; margin-bottom: 12px; padding-bottom: 8px; border-bottom: 1px solid rgba(255,255,255,0.1); }}
            
            .cart-footer {{ background: rgba(0,0,0,0.2); padding: 15px; border-radius: 12px; }}
            .total-row {{ display: flex; justify-content: space-between; font-weight: bold; margin-bottom: 10px; }}
            .btn-checkout {{ background: white; color: #004a99; width: 100%; border: none; border-radius: 10px; font-weight: bold; cursor: pointer; }}

            /* Modal Checkout Responsivo */
            #modalCheckout {{ display:none; position:fixed; z-index:9999; left:0; top:0; width:100%; height:100%; background:rgba(0,0,0,0.8); overflow-y: auto; }}
            .modal-content {{ background:white; width: 95%; max-width: 450px; margin: 20px auto; padding: 20px; border-radius: 15px; color: #333; box-sizing: border-box; }}
            .modal-content input, .modal-content select {{ width: 100%; padding: 12px; margin: 8px 0; border: 1px solid #ddd; border-radius: 8px; box-sizing: border-box; font-size: 14px; }}
        </style>
    </head>
    <body>
        <div class="main-content">
            <center><img src="https://github.com/glabpep/ordem/blob/main/1.png?raw=true" width="180" style="margin-bottom:20px;"></center>
            
            <div class="banner-blue"><i class="fas fa-truck"></i> Novos itens 09/03/2026!</div>
            <div class="banner-yellow"><b>Aviso:</b> Envasados em forma sólida. Use: Bacteriostatic Water.</div>

            <div class="cep-container">
                <i class="fas fa-map-marker-alt" style="color:#004a99"></i>
                <input type="text" id="cepInput" placeholder="Seu CEP">
                <button class="btn-cep" onclick="buscarCEP()">OK</button>
            </div>

            <div class="tabela-header">
                <div>PRODUTO</div><div>STATUS</div><div>VALOR</div><div>AÇÃO</div>
            </div>
            <div id="product-list"></div>
        </div>

        <div class="sidebar-cart">
            <div class="cart-title"><i class="fas fa-shopping-bag"></i> PEDIDO <span id="cart-count" style="float:right">0</span></div>
            <div id="cart-items" class="cart-items">
                <p style="text-align:center; opacity:0.6; margin-top:30px;">Vazio</p>
            </div>
            
            <div class="cart-footer">
                <input type="text" id="cupom" placeholder="CUPOM" oninput="atualizarTotais()" style="width:100%; padding:8px; border-radius:6px; border:none; margin-bottom:10px; box-sizing: border-box;">
                <div id="info-frete" style="font-size:11px; color:#ffeb3b; margin-bottom:5px; font-weight:bold;"></div>
                <div class="total-row">
                    <span>TOTAL:</span><span id="txt-total">R$ 0,00</span>
                </div>
                <button class="btn-checkout" onclick="abrirModal()">Pagar Agora</button>
            </div>
        </div>

        <div id="modalCheckout">
            <div class="modal-content">
                <h3 style="margin-top:0; color:#004a99; text-align:center;">Finalizar Entrega</h3>
                <input type="text" id="f_nome" placeholder="Nome Completo">
                <input type="text" id="f_end" placeholder="Endereço Completo">
                <div style="display:flex; gap:10px;">
                    <input type="text" id="f_cidade" placeholder="Cidade">
                    <input type="text" id="f_uf" placeholder="UF" maxlength="2">
                </div>
                <input type="text" id="f_whats" placeholder="WhatsApp">
                <select id="f_pgto">
                    <option value="Pix (5% Desconto)">Pix (5% Desconto)</option>
                    <option value="Cartão de Crédito">Cartão de Crédito</option>
                </select>
                <button onclick="finalizarPedido()" style="background:#28a745; color:white; width:100%; padding:15px; border:none; border-radius:10px; font-weight:bold; cursor:pointer; font-size:16px; margin-top:10px;">PEDIR NO WHATSAPP</button>
                <center><a href="javascript:fecharModal()" style="color:#999; font-size:13px; text-decoration:none; display:block; margin-top:15px;">VOLTAR</a></center>
            </div>
        </div>

        <script>
            const ESTOQUE = {json_data};
            let carrinho = [];
            let valorFrete = 0;

            function renderizarProdutos() {{
                const lista = document.getElementById('product-list');
                lista.innerHTML = ESTOQUE.map((p, i) => `
                    <div class="tabela-row">
                        <div>
                            <b>${{p.nome}}</b><br>
                            <small>${{p.espec}}</small>
                        </div>
                        <div>
                            <span class="badge ${{p.estoque > 0 ? 'bg-green' : 'bg-red'}}">
                                ${{p.estoque > 0 ? 'SIM' : 'NÃO'}}
                            </span>
                        </div>
                        <div style="font-weight:bold; color:#004a99;">R$ ${{p.preco.toLocaleString('pt-BR', {{minimumFractionDigits: 2}})}}</div>
                        <div>
                            <button class="${{p.estoque > 0 ? 'btn-add' : 'btn-disabled'}}" onclick="${{p.estoque > 0 ? `adicionarCarrinho(${{i}})` : ''}}">
                                ${{p.estoque > 0 ? '+' : '✕'}}
                            </button>
                        </div>
                    </div>
                `).join('');
            }}

            async function buscarCEP() {{
                const cep = document.getElementById('cepInput').value.replace(/\D/g,'');
                if(cep.length !== 8) {{ alert("CEP Inválido"); return; }}
                try {{
                    const resp = await fetch(\`https://viacep.com.br/ws/${{cep}}/json/\`);
                    const d = await resp.json();
                    if(d.erro) throw new Error();
                    document.getElementById('f_cidade').value = d.localidade;
                    document.getElementById('f_uf').value = d.uf;
                    const sul_sudeste = ['SP','RJ','MG','ES','PR','SC','RS'];
                    valorFrete = sul_sudeste.includes(d.uf) ? 90.00 : 165.00;
                    document.getElementById('info-frete').innerText = \`🚚 FRETE: R$ ${{valorFrete.toFixed(2)}}\`;
                    atualizarTotais();
                }} catch(e) {{ alert("CEP não encontrado."); }}
            }}

            function adicionarCarrinho(index) {{
                carrinho.push(ESTOQUE[index]);
                atualizarTotais();
            }}

            function removerCarrinho(index) {{
                carrinho.splice(index, 1);
                atualizarTotais();
            }}

            function atualizarTotais() {{
                const listaC = document.getElementById('cart-items');
                document.getElementById('cart-count').innerText = carrinho.length;
                
                if(carrinho.length === 0) {{
                    listaC.innerHTML = '<p style="text-align:center; opacity:0.6; margin-top:30px;">Vazio</p>';
                    document.getElementById('txt-total').innerText = "R$ 0,00";
                    return;
                }}

                listaC.innerHTML = carrinho.map((p, i) => `
                    <div class="cart-item">
                        <span>${{p.nome}}</span>
                        <span>R$ ${{p.preco.toFixed(2)}} <i class="fas fa-trash-alt" onclick="removerCarrinho(${{i}})" style="color:#ff6b6b; cursor:pointer; margin-left:8px;"></i></span>
                    </div>
                `).join('');

                let subtotal = carrinho.reduce((acc, p) => acc + p.preco, 0);
                const cupom = document.getElementById('cupom').value.toUpperCase();
                let desconto = (cupom === "CABRAL5" || cupom === "BRUNA5" || cupom === "DAFNE10") ? 0.05 : 0;
                if(cupom === "DAFNE10") desconto = 0.10;

                let total = (subtotal * (1 - desconto)) + valorFrete;
                document.getElementById('txt-total').innerText = "R$ " + total.toLocaleString('pt-BR', {{minimumFractionDigits: 2}});
            }}

            function abrirModal() {{ if(carrinho.length > 0) document.getElementById('modalCheckout').style.display='block'; }}
            function fecharModal() {{ document.getElementById('modalCheckout').style.display='none'; }}

            function finalizarPedido() {{
                const nome = document.getElementById('f_nome').value;
                if(!nome) {{ alert("Preencha o nome!"); return; }}
                let mensagem = "*NOVO PEDIDO G-LAB*%0A%0A";
                mensagem += "*Cliente:* " + nome + "%0A";
                mensagem += "*Itens:*%0A" + carrinho.map(p => "- " + p.nome).join("%0A");
                mensagem += "%0A%0A*Total:* " + document.getElementById('txt-total').innerText;
                window.open("https://wa.me/17746222523?text=" + mensagem);
            }}

            renderizarProdutos();
        </script>
    </body>
    </html>
    """
    return html_code

# --- 4. LÓGICA DO APP ---
df_estoque = carregar_estoque()

with st.sidebar:
    st.image("https://github.com/glabpep/ordem/blob/main/1.png?raw=true", width=120)
    st.write("---")
    menu = st.radio("Menu", ["🛒 Site de Vendas", "🔐 Área Administrativa"])

if menu == "🛒 Site de Vendas":
    # Uso de height dinâmico e scrolling habilitado para melhor experiência mobile
    components.html(gerar_interface_vendas(df_estoque), height=800, scrolling=True)

else:
    if not st.session_state.autenticado:
        st.subheader("Login ADM")
        user = st.text_input("Usuário")
        pw = st.text_input("Senha", type="password")
        if st.button("Entrar"):
            if user == "admin" and pw == "glab2026":
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.error("Acesso Negado")
    else:
        st.title("📦 Estoque")
        # No mobile, colunas do Streamlit empilham automaticamente
        tab1, tab2 = st.tabs(["Visualizar", "Dar Baixa"])
        
        with tab1:
            st.dataframe(df_estoque, use_container_width=True)
            if st.button("Sair"):
                st.session_state.autenticado = False
                st.rerun()
        
        with tab2:
            p_sel = st.selectbox("Produto", df_estoque['PRODUTO'].tolist())
            q_venda = st.number_input("Qtd vendida", min_value=1, value=1)
            if st.button("Salvar Baixa"):
                idx = df_estoque[df_estoque['PRODUTO'] == p_sel].index[0]
                if df_estoque.at[idx, 'QTD'] >= q_venda:
                    df_estoque.at[idx, 'QTD'] -= q_venda
                    salvar_estoque(df_estoque)
                    st.success("Atualizado!")
                    st.rerun()
                else:
                    st.error("Sem estoque!")
