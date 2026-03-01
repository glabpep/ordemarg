import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import os
import json

# --- 1. CONFIGURAÇÃO E ESTADO ---
st.set_page_config(page_title="G-LAB PEPTIDES", layout="wide", page_icon="🧪")

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

# CSS para limpar a interface do Streamlit
st.markdown("""
    <style>
        .block-container { padding: 0rem; }
        footer {visibility: hidden;}
        header {visibility: hidden;}
        [data-testid="stSidebar"] { background-color: #f8f9fa; border-right: 1px solid #ddd; }
    </style>
""", unsafe_allow_html=True)

# --- 2. BASE DE DADOS (EXCEL) ---
def carregar_estoque():
    caminho = "stock_0202 - NOVA.xlsx"
    if os.path.exists(caminho):
        try:
            df = pd.read_excel(caminho)
            df.columns = [str(col).strip().upper() for col in df.columns]
            # Limpeza rigorosa para evitar quebra no JS
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

# --- 3. FRONT-END (HTML/JS/CSS) ---
def gerar_interface_vendas(df):
    # Preparação dos dados para o JavaScript (Crucial para não virar tela branca)
    produtos_json = []
    for _, row in df.iterrows():
        produtos_json.append({
            "nome": str(row.get('PRODUTO', 'Sem Nome')),
            "espec": f"{row.get('VOLUME', '')} {row.get('MEDIDA', '')}",
            "preco": float(row.get('PREÇO (R$)', 0)),
            "estoque": int(row.get('QTD', 0))
        })
    
    # Transforma em string JSON segura
    json_data = json.dumps(produtos_json)

    html_code = f"""
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; background-color: #fff; display: flex; overflow-x: hidden; }}
            .main-content {{ flex: 1; padding: 20px; max-width: 900px; margin: 0 auto; margin-right: 360px; }}
            
            /* Banners */
            .banner-blue {{ background: #e3f2fd; color: #0d47a1; padding: 15px; border-radius: 8px; border-left: 6px solid #2196f3; font-size: 14px; margin-bottom: 10px; font-weight: 500; }}
            .banner-yellow {{ background: #fff9c4; color: #856404; padding: 15px; border-radius: 8px; font-size: 13px; border: 1px solid #ffeeba; margin-bottom: 20px; }}
            
            /* Busca/CEP */
            .cep-container {{ border: 2px solid #004a99; border-radius: 10px; padding: 10px; display: flex; align-items: center; gap: 10px; margin-bottom: 25px; }}
            .cep-container input {{ border: none; outline: none; flex: 1; font-size: 16px; }}
            .btn-cep {{ background: #28a745; color: white; border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer; font-weight: bold; }}

            /* Tabela de Itens */
            .tabela-header {{ background: #004a99; color: white; display: grid; grid-template-columns: 2fr 1fr 1fr 1fr; padding: 15px; border-radius: 8px 8px 0 0; font-weight: bold; font-size: 14px; }}
            .tabela-row {{ display: grid; grid-template-columns: 2fr 1fr 1fr 1fr; padding: 15px; border-bottom: 1px solid #eee; align-items: center; transition: 0.2s; }}
            .tabela-row:hover {{ background: #fcfcfc; }}
            
            .badge {{ padding: 5px 10px; border-radius: 5px; font-size: 11px; font-weight: bold; text-align: center; display: inline-block; }}
            .bg-green {{ background: #e6fcf5; color: #0ca678; border: 1px solid #0ca678; }}
            .bg-red {{ background: #fff5f5; color: #fa5252; border: 1px solid #fa5252; }}
            
            .btn-add {{ background: #004a99; color: white; border: none; padding: 8px; border-radius: 5px; cursor: pointer; width: 100%; font-weight: bold; }}
            .btn-disabled {{ background: #e9ecef; color: #adb5bd; border: none; padding: 8px; border-radius: 5px; width: 100%; cursor: not-allowed; }}

            /* Carrinho Lateral */
            .sidebar-cart {{ width: 350px; background: #004a99; color: white; height: 100vh; position: fixed; right: 0; top: 0; padding: 25px; box-sizing: border-box; display: flex; flex-direction: column; box-shadow: -5px 0 15px rgba(0,0,0,0.1); }}
            .cart-title {{ font-size: 20px; font-weight: bold; border-bottom: 1px solid rgba(255,255,255,0.2); padding-bottom: 15px; margin-bottom: 15px; }}
            .cart-items {{ flex: 1; overflow-y: auto; font-size: 14px; }}
            .cart-item {{ display: flex; justify-content: space-between; margin-bottom: 12px; padding-bottom: 8px; border-bottom: 1px solid rgba(255,255,255,0.1); }}
            
            .cart-footer {{ background: rgba(0,0,0,0.2); padding: 20px; border-radius: 12px; margin-top: 10px; }}
            .total-row {{ display: flex; justify-content: space-between; font-size: 22px; font-weight: bold; margin: 15px 0; }}
            .btn-checkout {{ background: white; color: #004a99; width: 100%; padding: 18px; border: none; border-radius: 10px; font-weight: bold; cursor: pointer; font-size: 18px; }}

            /* Modal Checkout */
            #modalCheckout {{ display:none; position:fixed; z-index:9999; left:0; top:0; width:100%; height:100%; background:rgba(0,0,0,0.8); }}
            .modal-content {{ background:white; width: 90%; max-width: 450px; margin: 30px auto; padding: 30px; border-radius: 15px; color: #333; }}
            .modal-content input, .modal-content select {{ width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ddd; border-radius: 8px; box-sizing: border-box; font-size: 14px; }}
        </style>
    </head>
    <body>
        <div class="main-content">
            <center><img src="https://github.com/glabpep/ordem/blob/main/1.png?raw=true" width="250" style="margin-bottom:20px;"></center>
            
            <div class="banner-blue"><i class="fas fa-truck"></i> Previsão de chegada de novos itens 09/03/2026, o estoque do site será atualizado!</div>
            <div class="banner-yellow"><b>Aviso importante:</b> Os produtos são envasados em forma sólida... NOME DA SOLUÇÃO: BACTERIOSTATIC WATER.</div>

            <div class="cep-container">
                <i class="fas fa-map-marker-alt" style="color:#004a99"></i>
                <input type="text" id="cepInput" placeholder="Informe seu CEP para Localizar Região">
                <button class="btn-cep" onclick="buscarCEP()">Localizar</button>
            </div>

            <div class="tabela-header">
                <div>PRODUTO</div><div>STATUS</div><div>VALOR</div><div>AÇÃO</div>
            </div>
            <div id="product-list">
                </div>
        </div>

        <div class="sidebar-cart">
            <div class="cart-title"><i class="fas fa-shopping-bag"></i> SEU PEDIDO <span id="cart-count" style="float:right">0</span></div>
            <div id="cart-items" class="cart-items">
                <p style="text-align:center; opacity:0.6; margin-top:50px;">Carrinho vazio</p>
            </div>
            
            <div class="cart-footer">
                <input type="text" id="cupom" placeholder="CUPOM DE DESCONTO" oninput="atualizarTotais()" style="width:100%; padding:10px; border-radius:6px; border:none; margin-bottom:15px;">
                <div id="info-frete" style="font-size:12px; color:#ffeb3b; margin-bottom:10px; font-weight:bold;"></div>
                <div class="total-row">
                    <span>TOTAL:</span><span id="txt-total">R$ 0,00</span>
                </div>
                <button class="btn-checkout" onclick="abrirModal()">Ir para Pagamento</button>
            </div>
        </div>

        <div id="modalCheckout">
            <div class="modal-content">
                <h2 style="margin-top:0; color:#004a99; text-align:center;">Dados de Entrega</h2>
                <input type="text" id="f_nome" placeholder="Nome Completo">
                <input type="text" id="f_end" placeholder="Endereço (Rua, Número, Bairro)">
                <div style="display:flex; gap:10px;">
                    <input type="text" id="f_cidade" placeholder="Cidade">
                    <input type="text" id="f_uf" placeholder="UF" maxlength="2">
                </div>
                <input type="text" id="f_whats" placeholder="WhatsApp (com DDD)">
                <select id="f_pgto">
                    <option value="Pix (5% Desconto)">Pix (5% Desconto)</option>
                    <option value="Cartão de Crédito">Cartão de Crédito</option>
                </select>
                <button onclick="finalizarPedido()" style="background:#28a745; color:white; width:100%; padding:16px; border:none; border-radius:10px; font-weight:bold; cursor:pointer; font-size:18px; margin-top:10px;">FINALIZAR NO WHATSAPP</button>
                <center><a href="javascript:fecharModal()" style="color:#999; font-size:13px; text-decoration:none; display:block; margin-top:15px;">CANCELAR E VOLTAR</a></center>
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
                            <b style="color:#333;">${{p.nome}}</b><br>
                            <small style="color:#666;">${{p.espec}}</small>
                        </div>
                        <div>
                            <span class="badge ${{p.estoque > 0 ? 'bg-green' : 'bg-red'}}">
                                ${{p.estoque > 0 ? 'DISPONÍVEL' : 'EM ESPERA'}}
                            </span>
                        </div>
                        <div style="font-weight:bold; color:#004a99;">R$ ${{p.preco.toLocaleString('pt-BR', {{minimumFractionDigits: 2}})}}</div>
                        <div>
                            <button class="${{p.estoque > 0 ? 'btn-add' : 'btn-disabled'}}" onclick="${{p.estoque > 0 ? `adicionarCarrinho(${{i}})` : ''}}">
                                ${{p.estoque > 0 ? 'ADICIONAR' : '✕'}}
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
                    
                    document.getElementById('info-frete').innerText = \`🚚 FRETE PARA ${{d.uf}}: R$ ${{valorFrete.toFixed(2)}}\`;
                    atualizarTotais();
                }} catch(e) {{ alert("Erro ao consultar CEP."); }}
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
                if(carrinho.length === 0) {{
                    listaC.innerHTML = '<p style="text-align:center; opacity:0.6; margin-top:50px;">Carrinho vazio</p>';
                    document.getElementById('txt-total').innerText = "R$ 0,00";
                    document.getElementById('cart-count').innerText = "0";
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
                document.getElementById('cart-count').innerText = carrinho.length;
            }}

            function abrirModal() {{ if(carrinho.length > 0) document.getElementById('modalCheckout').style.display='block'; }}
            function fecharModal() {{ document.getElementById('modalCheckout').style.display='none'; }}

            function finalizarPedido() {{
                const nome = document.getElementById('f_nome').value;
                if(!nome) {{ alert("Por favor, preencha seu nome."); return; }}
                
                let mensagem = "*NOVO PEDIDO G-LAB*%0A%0A";
                mensagem += "*Cliente:* " + nome + "%0A";
                mensagem += "*Endereço:* " + document.getElementById('f_end').value + "%0A";
                mensagem += "*Cidade:* " + document.getElementById('f_cidade').value + "/" + document.getElementById('f_uf').value + "%0A%0A";
                mensagem += "*ITENS:*%0A" + carrinho.map(p => "- " + p.nome).join("%0A");
                mensagem += "%0A%0A*TOTAL FINAL:* " + document.getElementById('txt-total').innerText;
                mensagem += "%0A*PAGAMENTO:* " + document.getElementById('f_pgto').value;
                
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
    st.image("https://github.com/glabpep/ordem/blob/main/1.png?raw=true", width=150)
    st.write("---")
    menu = st.radio("Navegação", ["🛒 Site de Vendas", "🔐 Área Administrativa"])

if menu == "🛒 Site de Vendas":
    # Aqui os dados do DF são passados para o HTML
    components.html(gerar_interface_vendas(df_estoque), height=1000, scrolling=True)

else:
    if not st.session_state.autenticado:
        st.subheader("Login Administrativo")
        user = st.text_input("Usuário")
        pw = st.text_input("Senha", type="password")
        if st.button("Entrar"):
            if user == "admin" and pw == "glab2026":
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.error("Acesso Negado")
    else:
        st.title("📦 Gestão de Estoque")
        col1, col2 = st.columns([2,1])
        
        with col1:
            st.write("Estoque Atual (Excel):")
            st.dataframe(df_estoque, use_container_width=True)
            if st.button("Sair"):
                st.session_state.autenticado = False
                st.rerun()
        
        with col2:
            st.write("Dar Baixa Manual:")
            p_sel = st.selectbox("Produto", df_estoque['PRODUTO'].tolist())
            q_venda = st.number_input("Qtd vendida", min_value=1, value=1)
            
            if st.button("Atualizar Excel"):
                idx = df_estoque[df_estoque['PRODUTO'] == p_sel].index[0]
                if df_estoque.at[idx, 'QTD'] >= q_venda:
                    df_estoque.at[idx, 'QTD'] -= q_venda
                    salvar_estoque(df_estoque)
                    st.success(f"Baixa de {q_venda} un. em {p_sel} salva com sucesso!")
                    st.rerun()
                else:
                    st.error("Estoque insuficiente!")
