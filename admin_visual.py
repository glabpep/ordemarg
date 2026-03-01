import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import os
import json

# 1. CONFIGURAÇÃO INICIAL (DEVE SER A PRIMEIRA LINHA)
st.set_page_config(page_title="G-LAB PEPTIDES", layout="wide", page_icon="🧪")

# 2. ESTADO DE SESSÃO (EVITA ATTRIBUTE ERROR)
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

# CSS para esconder o excesso do Streamlit
st.markdown("""
    <style>
        .block-container { padding: 0rem; }
        footer {visibility: hidden;}
        header {visibility: hidden;}
        [data-testid="stSidebar"] { background-color: #f8f9fa; }
    </style>
""", unsafe_allow_html=True)

# 3. FUNÇÕES DE BANCO DE DADOS (EXCEL)
def carregar_estoque():
    caminho = "stock_0202 - NOVA.xlsx"
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

def salvar_estoque(df):
    df.to_excel("stock_0202 - NOVA.xlsx", index=False)

# 4. GERADOR DO SITE (RESTORE TOTAL DO VISUAL)
def gerar_site_vendas(df):
    # Converte DataFrame para Lista de Dicionários para o JS
    lista_prods = []
    for _, r in df.iterrows():
        lista_prods.append({
            "n": str(r.get('PRODUTO', 'N/A')),
            "e": f"{r.get('VOLUME', '')} {r.get('MEDIDA', '')}",
            "p": float(r.get('PREÇO (R$)', 0)),
            "s": int(r.get('QTD', 0)) > 0
        })
    json_payload = json.dumps(lista_prods)

    html_final = f"""
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; background: white; margin: 0; display: flex; }}
            .conteudo {{ flex: 1; padding: 20px; max-width: 850px; margin: 0 auto; margin-right: 370px; }}
            
            /* Banners das Imagens */
            .banner-azul {{ background: #e3f2fd; color: #0d47a1; padding: 12px; border-radius: 8px; border-left: 5px solid #2196f3; font-size: 14px; margin-bottom: 10px; font-weight: bold; }}
            .banner-amarelo {{ background: #fff9c4; color: #827717; padding: 12px; border-radius: 8px; font-size: 13px; margin-bottom: 20px; border: 1px solid #fbc02d; }}
            
            /* Tabela e Busca */
            .cep-box {{ border: 2px solid #0d47a1; border-radius: 10px; padding: 10px; display: flex; gap: 10px; align-items: center; margin-bottom: 20px; }}
            .tabela {{ width: 100%; border-collapse: collapse; }}
            .tabela th {{ background: #0d47a1; color: white; padding: 12px; text-align: left; }}
            .linha-prod {{ border-bottom: 1px solid #eee; transition: 0.2s; }}
            
            .badge {{ padding: 5px 8px; border-radius: 4px; font-size: 10px; font-weight: bold; }}
            .disponivel {{ border: 1px solid #28a745; color: #28a745; }}
            .espera {{ border: 1px solid #dc3545; color: #dc3545; }}
            
            /* Carrinho Azul Lateral */
            .carrinho-lateral {{ width: 350px; background: #004a99; color: white; height: 100vh; position: fixed; right: 0; top: 0; padding: 20px; display: flex; flex-direction: column; }}
            .itens-carrinho {{ flex: 1; overflow-y: auto; margin: 15px 0; font-size: 13px; }}
            .item-c {{ display: flex; justify-content: space-between; margin-bottom: 8px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 5px; }}
            
            .botao-pagar {{ background: white; color: #004a99; width: 100%; border: none; padding: 15px; border-radius: 8px; font-weight: bold; cursor: pointer; font-size: 16px; }}

            /* Modal de Checkout */
            #modal {{ display:none; position:fixed; z-index:9999; left:0; top:0; width:100%; height:100%; background:rgba(0,0,0,0.8); }}
            .modal-content {{ background:white; margin: 5% auto; padding: 25px; width: 400px; border-radius: 15px; color: #333; }}
            input, select {{ width: 100%; padding: 10px; margin: 5px 0; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box; }}
        </style>
    </head>
    <body>
        <div class="conteudo">
            <center><img src="https://github.com/glabpep/ordem/blob/main/1.png?raw=true" width="220"></center><br>
            
            <div class="banner-azul"><i class="fas fa-truck"></i> Previsão de chegada de novos itens 09/03/2026!</div>
            <div class="banner-amarelo"><b>Aviso importante:</b> Produtos envasados em forma sólida... Solução: Bacteriostatic Water.</div>

            <div class="cep-box">
                <i class="fas fa-map-marker-alt" style="color:#0d47a1"></i>
                <input type="text" id="cep" placeholder="00000-000" style="border:none; outline:none; flex:1;">
                <button onclick="calcFrete()" style="background:#28a745; color:white; border:none; padding:8px 15px; border-radius:5px; cursor:pointer;">Localizar</button>
            </div>

            <table class="tabela">
                <thead><tr><th>Produto</th><th>Status</th><th>Preço</th><th>Ação</th></tr></thead>
                <tbody id="lista"></tbody>
            </table>
        </div>

        <div class="carrinho-lateral">
            <h3 style="margin:0;"><i class="fas fa-shopping-cart"></i> SEU PEDIDO</h3>
            <div id="cart-list" class="itens-carrinho"></div>
            <div style="background:rgba(0,0,0,0.2); padding:15px; border-radius:10px;">
                <div id="frete-txt" style="font-size:11px; color:#ffeb3b;"></div>
                <div style="display:flex; justify-content:space-between; font-size:18px; font-weight:bold; margin:10px 0;">
                    <span>TOTAL:</span><span id="total">R$ 0,00</span>
                </div>
                <button class="botao-pagar" onclick="abrir()">Ir para Pagamento</button>
            </div>
        </div>

        <div id="modal">
            <div class="modal-content">
                <h3>Dados de Entrega</h3>
                <input type="text" id="f_nome" placeholder="Nome Completo">
                <input type="text" id="f_rua" placeholder="Rua e Número">
                <input type="text" id="f_bairro" placeholder="Bairro">
                <input type="text" id="f_cid" placeholder="Cidade">
                <input type="text" id="f_uf" placeholder="UF">
                <input type="text" id="f_zap" placeholder="WhatsApp">
                <select id="f_pgto">
                    <option>Pix (Aprovação Imediata)</option>
                    <option>Cartão de Crédito</option>
                </select>
                <button onclick="enviar()" style="background:#28a745; color:white; width:100%; border:none; padding:12px; border-radius:8px; font-weight:bold; cursor:pointer; margin-top:10px;">ENVIAR WHATSAPP</button>
                <center><a href="javascript:fechar()" style="color:red; font-size:12px; display:block; margin-top:10px;">CANCELAR</a></center>
            </div>
        </div>

        <script>
            const PRODS = {json_payload};
            let cart = [];
            let freteVal = 0;

            function render() {{
                const b = document.getElementById('lista');
                b.innerHTML = PRODS.map((p, i) => `
                    <tr class="linha-prod">
                        <td><b>${{p.n}}</b><br><small>${{p.e}}</small></td>
                        <td><span class="badge ${{p.s ? 'disponivel' : 'espera'}}">${{p.s ? 'DISPONÍVEL' : 'EM ESPERA'}}</span></td>
                        <td>R$ ${{p.p.toFixed(2)}}</td>
                        <td><button onclick="${{p.s ? `add(${{i}})` : ''}}" style="background:${{p.s ? '#0d47a1' : '#ccc'}}; color:white; border:none; padding:5px 10px; border-radius:4px; cursor:pointer;">${{p.s ? '+' : '✕'}}</button></td>
                    </tr>
                `).join('');
            }}

            function add(i) {{ cart.push(PRODS[i]); att(); }}
            function remove(i) {{ cart.splice(i, 1); att(); }}

            async function calcFrete() {{
                const c = document.getElementById('cep').value.replace(/\D/g,'');
                if(c.length!==8) return;
                const r = await fetch(\`https://viacep.com.br/ws/\${{c}}/json/\`);
                const d = await r.json();
                if(d.uf) {{
                    document.getElementById('f_cid').value = d.localidade;
                    document.getElementById('f_uf').value = d.uf;
                    freteVal = ['SP','RJ','MG','ES','PR','SC','RS'].includes(d.uf) ? 90 : 165;
                    document.getElementById('frete-txt').innerText = "🚚 Frete Localizado: R$ " + freteVal.toFixed(2);
                    att();
                }}
            }}

            function att() {{
                const l = document.getElementById('cart-list');
                l.innerHTML = cart.map((item, idx) => `
                    <div class="item-c">
                        <span>\${{item.n}}</span>
                        <span>R$ \${{item.p.toFixed(2)}} <i class="fas fa-trash" onclick="remove(\${{idx}})" style="color:#ff6b6b; cursor:pointer;"></i></span>
                    </div>
                `).join('');
                let total = cart.reduce((a, b) => a + b.p, 0) + (cart.length > 0 ? freteVal : 0);
                document.getElementById('total').innerText = "R$ " + total.toFixed(2);
            }}

            function abrir() {{ if(cart.length>0) document.getElementById('modal').style.display='block'; }}
            function fechar() {{ document.getElementById('modal').style.display='none'; }}

            function enviar() {{
                const msg = "*NOVO PEDIDO G-LAB*%0A*Cliente:* "+document.getElementById('f_nome').value+"%0A*Itens:*%0A"+cart.map(i=>"- "+i.n).join("%0A")+"%0A*Total:* "+document.getElementById('total').innerText;
                window.open("https://wa.me/17746222523?text=" + msg);
            }}
            render();
        </script>
    </body>
    </html>
    """
    return html_final

# 5. FLUXO PRINCIPAL
df_dados = carregar_estoque()

with st.sidebar:
    st.image("https://github.com/glabpep/ordem/blob/main/1.png?raw=true", width=120)
    escolha = st.radio("Navegação", ["🛒 Site de Vendas", "🔐 Área do Funcionário"])

if escolha == "🛒 Site de Vendas":
    components.html(gerar_site_vendas(df_dados), height=1200, scrolling=True)

else:
    if not st.session_state.autenticado:
        st.title("Acesso Restrito")
        u = st.text_input("Usuário")
        s = st.text_input("Senha", type="password")
        if st.button("Login"):
            if u == "admin" and s == "glab2026":
                st.session_state.autenticado = True
                st.rerun()
            else: st.error("Incorreto")
    else:
        st.title("🛠️ Gestão de Estoque")
        tab1, tab2 = st.tabs(["Estoque Atual", "Dar Baixa"])
        
        with tab1:
            st.dataframe(df_dados)
            if st.button("Sair"):
                st.session_state.autenticado = False
                st.rerun()
        
        with tab2:
            prod = st.selectbox("Produto", df_dados['PRODUTO'].unique())
            qtd = st.number_input("Qtd vendida", min_value=1, value=1)
            if st.button("Confirmar Baixa"):
                idx = df_dados[df_dados['PRODUTO'] == prod].index[0]
                if df_dados.at[idx, 'QTD'] >= qtd:
                    df_dados.at[idx, 'QTD'] -= qtd
                    salvar_estoque(df_dados)
                    st.success("Estoque Atualizado!")
                    st.rerun()
                else: st.error("Sem estoque!")
