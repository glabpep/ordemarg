import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import os
import json

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="G-LAB PEPTIDES", layout="wide", page_icon="🧪")

# CSS para esconder o Streamlit e manter o layout limpo
st.markdown("""
    <style>
        .block-container { padding: 0rem; }
        iframe { border: none; }
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- FUNÇÕES DE DADOS (EXCEL) ---
def carregar_estoque():
    caminho = "stock_0202 - NOVA.xlsx"
    if os.path.exists(caminho):
        try:
            df = pd.read_excel(caminho)
            df.columns = [str(col).strip().upper() for col in df.columns]
            # Converte QTD para número para evitar o ValueError das suas imagens
            if 'QTD' in df.columns:
                df['QTD'] = pd.to_numeric(df['QTD'], errors='coerce').fillna(0).astype(int)
            return df
        except: return pd.DataFrame()
    return pd.DataFrame()

def salvar_estoque(df):
    df.to_excel("stock_0202 - NOVA.xlsx", index=False)

# --- GERADOR DO SITE (HTML/JS/CSS INTEGRADO) ---
def gerar_site_vendas(df):
    # Transforma os dados do Excel em JSON para o JavaScript
    lista_prods = []
    for _, row in df.iterrows():
        lista_prods.append({
            "nome": str(row.get('PRODUTO', 'N/A')),
            "espec": f"{row.get('VOLUME', '')} {row.get('MEDIDA', '')}",
            "preco": float(row.get('PREÇO (R$)', 0)),
            "disponivel": int(row.get('QTD', 0)) > 0
        })
    produtos_json = json.dumps(lista_prods)

    # HTML COMPLETO COM TODAS AS FUNCIONALIDADES
    html_final = f"""
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; background: white; margin: 0; display: flex; }}
            .main-content {{ flex: 1; padding: 20px; max-width: 900px; margin: 0 auto; margin-right: 380px; }}
            
            /* Banners conforme suas imagens */
            .logo-center {{ text-align: center; margin-bottom: 20px; }}
            .logo-center img {{ width: 250px; }}
            .banner-azul {{ background: #e3f2fd; color: #0d47a1; padding: 12px; border-radius: 8px; border-left: 5px solid #2196f3; font-size: 14px; margin-bottom: 15px; font-weight: bold; }}
            .banner-amarelo {{ background: #fff9c4; color: #827717; padding: 12px; border-radius: 8px; font-size: 13px; margin-bottom: 20px; border: 1px solid #fbc02d; }}
            
            /* CEP e Tabela */
            .cep-box {{ border: 2px solid #0d47a1; border-radius: 10px; padding: 15px; display: flex; gap: 10px; align-items: center; margin-bottom: 25px; }}
            .product-table {{ width: 100%; border-collapse: collapse; }}
            .product-table th {{ background: #0d47a1; color: white; padding: 12px; text-align: left; }}
            .product-row {{ border-bottom: 1px solid #eee; transition: 0.2s; }}
            .product-row:hover {{ background: #f9f9f9; }}
            
            .badge {{ padding: 5px 10px; border-radius: 4px; font-size: 11px; font-weight: bold; text-transform: uppercase; }}
            .status-ok {{ border: 1px solid #28a745; color: #28a745; }}
            .status-wait {{ border: 1px solid #dc3545; color: #dc3545; }}
            .btn-add {{ background: #28a745; color: white; border: none; padding: 8px 15px; border-radius: 5px; cursor: pointer; font-weight: bold; }}
            .btn-off {{ background: #e0e0e0; color: #999; cursor: not-allowed; padding: 8px 15px; border-radius: 5px; }}

            /* Carrinho Lateral Azul (Igual às imagens) */
            .cart-sidebar {{ width: 350px; background: #004a99; color: white; height: 100vh; position: fixed; right: 0; top: 0; padding: 25px; box-sizing: border-box; display: flex; flex-direction: column; }}
            .cart-title {{ font-size: 18px; font-weight: bold; border-bottom: 1px solid rgba(255,255,255,0.2); padding-bottom: 15px; margin-bottom: 15px; }}
            #cart-list {{ flex: 1; overflow-y: auto; font-size: 14px; }}
            .cart-item {{ display: flex; justify-content: space-between; margin-bottom: 10px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 5px; }}
            
            .cart-footer {{ margin-top: 15px; background: rgba(0,0,0,0.2); padding: 15px; border-radius: 10px; }}
            .btn-checkout {{ background: white; color: #004a99; width: 100%; border: none; padding: 15px; border-radius: 8px; font-weight: bold; cursor: pointer; font-size: 16px; margin-top: 10px; }}
            
            /* Modal de Endereço */
            #modalPayment {{ display:none; position:fixed; z-index:999; left:0; top:0; width:100%; height:100%; background:rgba(0,0,0,0.8); }}
            .modal-content {{ background:white; margin: 5% auto; padding: 25px; width: 90%; max-width: 450px; border-radius: 15px; color: #333; }}
            input, select {{ width: 100%; padding: 12px; margin: 8px 0; border: 1px solid #ddd; border-radius: 6px; box-sizing: border-box; }}
        </style>
    </head>
    <body>
        <div class="main-content">
            <div class="logo-center"><img src="https://github.com/glabpep/ordem/blob/main/1.png?raw=true"></div>
            
            <div class="banner-azul"><i class="fas fa-truck"></i> Previsão de chegada de novos itens 09/03/2026, o estoque do site será atualizado!</div>
            
            <div class="banner-amarelo">
                <b>Aviso importante:</b> Os produtos são envasados em forma sólida... <b>NOME DA SOLUÇÃO:</b> BACTERIOSTATIC WATER.
            </div>

            <div class="cep-box">
                <i class="fas fa-map-marker-alt" style="color:#0d47a1; font-size:20px;"></i>
                <input type="text" id="cep-input" placeholder="00000-000" style="margin:0; flex:1;">
                <button onclick="buscarCEP()" style="background:#28a745; color:white; border:none; padding:10px 20px; border-radius:5px; cursor:pointer; font-weight:bold;">Localizar</button>
            </div>

            <table class="product-table">
                <thead><tr><th>Produto</th><th>Status</th><th>Preço</th><th>Ação</th></tr></thead>
                <tbody id="lista-corpo"></tbody>
            </table>
        </div>

        <div class="cart-sidebar">
            <div class="cart-title"><i class="fas fa-shopping-cart"></i> Seu Pedido <span id="count-top" style="float:right;">0</span></div>
            <div id="cart-list"></div>
            <div class="cart-footer">
                <input type="text" id="cupom" placeholder="CUPOM" oninput="atualizarTotal()" style="padding:8px;">
                <div id="frete-text" style="font-size:12px; color:#ffeb3b; margin:10px 0;"></div>
                <div style="display:flex; justify-content:space-between; font-size:18px; font-weight:bold;">
                    <span>TOTAL:</span><span id="total-val">R$ 0,00</span>
                </div>
                <button class="btn-checkout" onclick="abrirCheckout()">Ir para Pagamento</button>
            </div>
        </div>

        <div id="modalPayment">
            <div class="modal-content">
                <h3 style="margin-top:0;">Dados para Entrega</h3>
                <input type="text" id="f_nome" placeholder="Nome Completo">
                <input type="text" id="f_rua" placeholder="Rua / Avenida / Nº">
                <input type="text" id="f_bairro" placeholder="Bairro">
                <div style="display:flex; gap:10px;">
                    <input type="text" id="f_cidade" placeholder="Cidade">
                    <input type="text" id="f_uf" placeholder="UF" maxlength="2">
                </div>
                <input type="text" id="f_whats" placeholder="WhatsApp com DDD">
                <select id="f_pgto">
                    <option value="Pix (Aprovação Imediata)">Pix (Aprovação Imediata)</option>
                    <option value="Cartão de Crédito">Cartão de Crédito</option>
                </select>
                <button onclick="enviarWhatsApp()" style="background:#28a745; color:white; width:100%; border:none; padding:15px; border-radius:10px; font-weight:bold; cursor:pointer; font-size:16px; margin-top:10px;">ENVIAR PARA O WHATSAPP</button>
                <center><a href="javascript:fecharCheckout()" style="color:red; font-size:12px; display:block; margin-top:15px;">CANCELAR</a></center>
            </div>
        </div>

        <script>
            const PRODUTOS = {produtos_json};
            let carrinho = [];
            let frete = 0;
            let cupomAtivo = 0;

            function renderCatalog() {{
                const tbody = document.getElementById('lista-corpo');
                tbody.innerHTML = PRODUTOS.map((p, i) => `
                    <tr class="product-row">
                        <td><b>${{p.nome}}</b><br><small style="color:#666;">${{p.espec}}</small></td>
                        <td><span class="badge ${{p.disponivel ? 'status-ok' : 'status-wait'}}">${{p.disponivel ? 'DISPONÍVEL' : 'EM ESPERA'}}</span></td>
                        <td>R$ ${{p.preco.toFixed(2)}}</td>
                        <td>
                            <button class="${{p.disponivel ? 'btn-add' : 'btn-off'}}" onclick="${{p.disponivel ? `addCart(${{i}})` : ''}}">
                                ${{p.disponivel ? '+' : '✕'}}
                            </button>
                        </td>
                    </tr>
                `).join('');
            }}

            function addCart(i) {{
                carrinho.push(PRODUTOS[i]);
                atualizarTotal();
            }}

            async function buscarCEP() {{
                const cep = document.getElementById('cep-input').value.replace(/\D/g,'');
                if(cep.length !== 8) return alert("CEP inválido");
                
                try {{
                    const r = await fetch(\`https://viacep.com.br/ws/\${{cep}}/json/\`);
                    const d = await r.json();
                    if(d.erro) throw new Error();
                    
                    document.getElementById('f_cidade').value = d.localidade;
                    document.getElementById('f_uf').value = d.uf;
                    
                    const sul_sudeste = ['SP','RJ','MG','ES','PR','SC','RS'];
                    frete = sul_sudeste.includes(d.uf) ? 90.00 : 165.00;
                    document.getElementById('frete-text').innerText = "🚚 Frete Localizado: R$ " + frete.toFixed(2);
                    atualizarTotal();
                }} catch {{ alert("Erro ao buscar CEP"); }}
            }}

            function atualizarTotal() {{
                const list = document.getElementById('cart-list');
                list.innerHTML = carrinho.map((item, idx) => `
                    <div class="cart-item">
                        <span>\${{item.nome}}</span>
                        <span>R$ \${{item.preco.toFixed(2)}} <i class="fas fa-trash" onclick="remover(\${{idx}})" style="cursor:pointer; color:#ff6b6b;"></i></span>
                    </div>
                `).join('');

                const cupom = document.getElementById('cupom').value.toUpperCase();
                cupomAtivo = (cupom === 'CABRAL5' || cupom === 'BRUNA5' || cupom === 'DAFNE10') ? 0.05 : 0;
                if(cupom === 'DAFNE10') cupomAtivo = 0.10;

                let sub = carrinho.reduce((a, b) => a + b.preco, 0);
                let total = (sub * (1 - cupomAtivo)) + (carrinho.length > 0 ? frete : 0);
                
                document.getElementById('total-val').innerText = "R$ " + total.toFixed(2);
                document.getElementById('count-top').innerText = carrinho.length;
            }}

            function remover(i) {{ carrinho.splice(i, 1); atualizarTotal(); }}
            function abrirCheckout() {{ if(carrinho.length > 0) document.getElementById('modalPayment').style.display='block'; }}
            function fecharCheckout() {{ document.getElementById('modalPayment').style.display='none'; }}

            function enviarWhatsApp() {{
                const nome = document.getElementById('f_nome').value;
                if(!nome) return alert("Preencha seu nome");
                
                let msg = "*NOVO PEDIDO G-LAB*%0A%0A";
                msg += "*Cliente:* " + nome + "%0A";
                msg += "*Endereço:* " + document.getElementById('f_rua').value + ", " + document.getElementById('f_bairro').value + "%0A";
                msg += "*Cidade:* " + document.getElementById('f_cidade').value + "-" + document.getElementById('f_uf').value + "%0A%0A";
                msg += "*ITENS:*%0A" + carrinho.map(i => "- " + i.nome).join("%0A");
                msg += "%0A%0A*TOTAL:* " + document.getElementById('total-val').innerText;
                
                window.open("https://wa.me/17746222523?text=" + msg);
            }}

            renderCatalog();
        </script>
    </body>
    </html>
    """
    return html_final

# --- LOGICA DE NAVEGAÇÃO (STREAMLIT) ---
df_estoque = carregar_estoque()

# Inicializa estados de sessão
if "logado" not in st.session_state: st.session_state.logado = False

with st.sidebar:
    st.image("https://github.com/glabpep/ordem/blob/main/1.png?raw=true", width=120)
    opcao = st.radio("Navegação", ["🛒 Site de Vendas", "🔐 Área Restrita"])

if opcao == "🛒 Site de Vendas":
    components.html(gerar_site_vendas(df_estoque), height=2000, scrolling=True)

else:
    if not st.session_state.logado:
        st.subheader("Login G-LAB")
        u = st.text_input("Usuário")
        s = st.text_input("Senha", type="password")
        if st.button("Acessar"):
            if u == "admin" and s == "glab2026":
                st.session_state.logado = True
                st.rerun()
            else: st.error("Acesso negado")
    else:
        st.title("🛠️ Gestão de Estoque")
        tab1, tab2 = st.tabs(["📊 Ver Inventário", "📦 Baixa Manual"])
        
        with tab1:
            st.dataframe(df_estoque, use_container_width=True)
            if st.button("Sair"):
                st.session_state.logado = False
                st.rerun()
        
        with tab2:
            st.write("Selecione o produto para dar baixa (venda realizada):")
            prod_nome = st.selectbox("Produto", df_estoque['PRODUTO'].unique())
            qtd_venda = st.number_input("Quantidade vendida", min_value=1, value=1)
            
            if st.button("Confirmar Baixa e Atualizar Excel"):
                idx = df_estoque[df_estoque['PRODUTO'] == prod_nome].index[0]
                estoque_atual = df_estoque.at[idx, 'QTD']
                
                if estoque_atual >= qtd_venda:
                    df_estoque.at[idx, 'QTD'] = estoque_atual - qtd_venda
                    salvar_estoque(df_estoque) # SALVA NO EXCEL REAL
                    st.success(f"Estoque atualizado! Novo saldo de {prod_nome}: {df_estoque.at[idx, 'QTD']}")
                    st.rerun()
                else:
                    st.error("Quantidade em estoque insuficiente!")
