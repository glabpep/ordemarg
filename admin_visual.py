import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import os
import json

# --- 1. CONFIGURAÇÃO DE AMBIENTE ---
st.set_page_config(page_title="G-LAB PEPTIDES", layout="wide", page_icon="🧪")

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

# CSS para limpar a interface do Streamlit e focar no seu Site
st.markdown("""
    <style>
        .block-container { padding: 0rem; max-width: 100%; }
        footer {visibility: hidden;}
        header {visibility: hidden;}
        [data-testid="stSidebar"] { background-color: #f8f9fa; border-right: 1px solid #ddd; }
        /* Garantir que o iframe ocupe a tela toda no mobile */
        iframe { width: 100%; border: none; }
    </style>
""", unsafe_allow_html=True)

# --- 2. GESTÃO DE DADOS (EXCEL) ---
def carregar_estoque():
    diretorio = os.path.dirname(os.path.abspath(__file__))
    arquivo = os.path.join(diretorio, 'stock_0202 - NOVA.xlsx')
    
    if os.path.exists(arquivo):
        df = pd.read_excel(arquivo)
        # Limpeza de colunas
        df.columns = [str(col).strip() for col in df.columns]
        return df
    return pd.DataFrame()

df_atual = carregar_estoque()

# --- 3. PREPARAÇÃO DO JSON PARA O SEU HTML ---
# Aqui mapeamos os produtos do Excel para o formato que o seu index.html reconhece
produtos_json = []
if not df_atual.empty:
    for _, row in df_atual.iterrows():
        nome_prod = str(row.get('PRODUTO', '')).strip()
        # O link da imagem segue o seu padrão do GitHub
        img_url = f"https://raw.githubusercontent.com/glabpep/ordem/main/{nome_prod.replace(' ', '%20')}.webp"
        
        produtos_json.append({
            "nome": nome_prod,
            "espec": f"{row.get('VOLUME', '')} {row.get('MEDIDA', '')}",
            "preco": float(row.get('Preço (R$)', 0)),
            "estoque": str(row.get('ESTOQUE', 'EM ESPERA')).upper(),
            "qtd": int(row.get('QTD', 0)) if pd.notna(row.get('QTD')) else 0,
            "img": img_url
        })

# --- 4. O SEU HTML INTEGRAL (VERSÃO ROBUSTA) ---
# Injetamos o JSON dentro da variável 'produtosBase' do seu script original
html_vendas = f"""
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>G-LAB PEPTIDES</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        /* ESTILOS ORIGINAIS DO SEU INDEX.HTML */
        :root {{ --primary: #004a99; --secondary: #28a745; --bg: #f4f7f9; }}
        body {{ font-family: 'Segoe UI', Roboto, sans-serif; background: var(--bg); margin: 0; padding: 0; color: #333; }}
        .container {{ max-width: 900px; margin: auto; background: white; min-height: 100vh; padding: 15px; box-sizing: border-box; padding-bottom: 220px; }}
        .header-logo-container {{ text-align: center; padding: 15px 0; }}
        .header-logo {{ max-width: 220px; width: 100%; height: auto; }}
        
        /* LISTA DE PRODUTOS RESPONSIVA (MOBILE) */
        .product-item {{ display: flex; align-items: center; border: 1px solid #eee; border-radius: 15px; padding: 12px; margin-bottom: 12px; gap: 12px; background: #fff; }}
        .prod-img {{ width: 80px; height: 80px; object-fit: contain; border-radius: 10px; }}
        .prod-info {{ flex-grow: 1; }}
        .prod-name {{ font-weight: 800; font-size: 1rem; margin: 0; text-transform: uppercase; }}
        .prod-espec {{ color: var(--primary); font-weight: 700; font-size: 0.85rem; }}
        .prod-price {{ font-weight: 900; font-size: 1.1rem; margin-top: 4px; }}
        
        .btn-add {{ background: var(--primary); color: white; border: none; padding: 10px; border-radius: 8px; font-weight: bold; cursor: pointer; width: 80px; }}
        .btn-off {{ background: #eee; color: #aaa; border: none; padding: 10px; border-radius: 8px; width: 80px; cursor: not-allowed; }}

        /* CARRINHO FIXO EMBAIXO */
        .cart-bar {{ position: fixed; bottom: 0; left: 0; right: 0; background: var(--primary); color: white; padding: 18px; z-index: 999; border-radius: 20px 20px 0 0; box-shadow: 0 -5px 15px rgba(0,0,0,0.1); }}
        .cart-flex {{ max-width: 900px; margin: auto; display: flex; justify-content: space-between; align-items: center; }}
        
        /* MODAL IDENTICO AO SEU */
        .modal {{ display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.8); z-index:10000; }}
        .modal-content {{ background:white; width: 92%; max-width:450px; margin: 10% auto; padding: 25px; border-radius: 20px; }}
        input, select {{ width: 100%; padding: 12px; margin: 8px 0; border: 1px solid #ddd; border-radius: 10px; box-sizing: border-box; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header-logo-container">
            <img src="https://github.com/glabpep/ordem/blob/main/1.png?raw=true" class="header-logo">
        </div>

        <div id="lista-produtos"></div>
    </div>

    <div class="cart-bar" id="cart-bar" style="display:none;">
        <div class="cart-flex">
            <div>
                <span id="c-qtd" style="background:white; color:var(--primary); padding:3px 10px; border-radius:15px; font-weight:bold;">0</span>
                <span style="font-weight:bold; margin-left:10px;">R$ <span id="c-total">0,00</span></span>
            </div>
            <button onclick="abrirModal()" style="background:var(--secondary); color:white; border:none; padding:12px 20px; border-radius:10px; font-weight:bold;">CONCLUIR</button>
        </div>
    </div>

    <div id="modal-checkout" class="modal">
        <div class="modal-content">
            <h3 style="margin-top:0; color:var(--primary);">Finalizar Pedido</h3>
            <input type="text" id="f_nome" placeholder="Nome Completo">
            <input type="text" id="f_cep" placeholder="CEP" onblur="checarFrete(this.value)">
            <input type="text" id="f_end" placeholder="Endereço">
            <input type="text" id="f_cupom" placeholder="CUPOM" oninput="recalcular()">
            <div id="resumo" style="font-size:0.85rem; background:#f9f9f9; padding:10px; border-radius:8px; margin:10px 0;"></div>
            <button onclick="enviarPedido()" style="width:100%; background:var(--secondary); color:white; border:none; padding:15px; border-radius:10px; font-weight:bold; font-size:1.1rem;">ENVIAR WHATSAPP</button>
            <center><button onclick="fecharModal()" style="background:none; border:none; color:#999; margin-top:15px;">Voltar</button></center>
        </div>
    </div>

    <script>
        const PRODUTOS = {json.dumps(produtos_json)};
        let carrinho = [];
        let vFrete = 0;

        function render() {{
            const div = document.getElementById('lista-produtos');
            div.innerHTML = PRODUTOS.map((p, i) => `
                <div class="product-item">
                    <img src="${{p.img}}" class="prod-img" onerror="this.src='https://via.placeholder.com/100?text=G-LAB'">
                    <div class="prod-info">
                        <p class="prod-name">${{p.nome}}</p>
                        <p class="prod-espec">${{p.espec}}</p>
                        <p class="prod-price">R$ ${{p.preco.toLocaleString('pt-BR', {{minimumFractionDigits:2}})}}</p>
                    </div>
                    ${{ (p.qtd > 0 || p.estoque === 'DISPONÍVEL') 
                        ? `<button class="btn-add" onclick="add(${{i}})">ADD</button>` 
                        : `<button class="btn-off">OFF</button>`}}
                </div>
            `).join('');
        }}

        function add(idx) {{
            carrinho.push(PRODUTOS[idx]);
            document.getElementById('cart-bar').style.display = 'block';
            recalcular();
        }}

        function recalcular() {{
            let sub = carrinho.reduce((a, b) => a + b.preco, 0);
            let cupom = document.getElementById('f_cupom').value.toUpperCase();
            let desc = (cupom === "CABRAL5" || cupom === "BRUNA5") ? 0.05 : (cupom === "DAFNE10" ? 0.10 : 0);
            let total = (sub * (1 - desc)) + vFrete;
            
            document.getElementById('c-qtd').innerText = carrinho.length;
            document.getElementById('c-total').innerText = total.toLocaleString('pt-BR', {{minimumFractionDigits:2}});
            document.getElementById('resumo').innerHTML = `Subtotal: R$ ${{sub.toFixed(2)}}<br>Frete: R$ ${{vFrete.toFixed(2)}}<br>Desconto: ${{desc*100}}%`;
        }}

        async function checarFrete(cep) {{
            let c = cep.replace(/\D/g, '');
            if(c.length === 8) {{
                const r = await fetch(\`https://viacep.com.br/ws/${{c}}/json/\`);
                const d = await r.json();
                if(!d.erro) {{
                    document.getElementById('f_end').value = d.logradouro + ", " + d.bairro;
                    vFrete = ['SP','RJ','MG','ES','PR','SC','RS'].includes(d.uf) ? 90 : 165;
                    recalcular();
                }}
            }}
        }}

        function abrirModal() {{ document.getElementById('modal-checkout').style.display='block'; }}
        function fecharModal() {{ document.getElementById('modal-checkout').style.display='none'; }}

        function enviarPedido() {{
            const nome = document.getElementById('f_nome').value;
            if(!nome) return alert("Digite seu nome");
            let msg = "*PEDIDO G-LAB*%0A%0A*Cliente:* " + nome + "%0A*Itens:*%0A";
            carrinho.forEach(item => msg += "- " + item.nome + " (" + item.espec + ")%0A");
            msg += "%0A*Total:* R$ " + document.getElementById('c-total').innerText;
            window.open("https://wa.me/17746222523?text=" + msg);
        }}

        render();
    </script>
</body>
</html>
"""

# --- 5. INTERFACE DO USUÁRIO (MENU LATERAL) ---
with st.sidebar:
    st.image("https://github.com/glabpep/ordem/blob/main/1.png?raw=true", use_container_width=True)
    aba = st.radio("NAVEGAÇÃO", ["🛒 LOJA", "🔐 ADMINISTRADOR"])

if aba == "🛒 LOJA":
    # Exibe o seu HTML Identico
    components.html(html_vendas, height=1200, scrolling=True)

else:
    # AREA DO ADMIN PROTEGIDA
    if not st.session_state.autenticado:
        st.subheader("Login Administrativo")
        user = st.text_input("Usuário")
        pw = st.text_input("Senha", type="password")
        if st.button("ACESSAR"):
            if user == "admin" and pw == "glab2026":
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.error("Dados incorretos")
    else:
        st.title("⚙️ Gestão de Estoque")
        st.info("Altere os dados na tabela e clique no botão de salvar abaixo.")
        
        # Tabela editável (conecta direto no Excel)
        df_editavel = st.data_editor(df_atual, use_container_width=True, hide_index=True)
        
        if st.button("💾 SALVAR ALTERAÇÕES"):
            try:
                df_editavel.to_excel("stock_0202 - NOVA.xlsx", index=False)
                st.success("Estoque atualizado com sucesso!")
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao salvar: {e}")
        
        if st.button("Sair"):
            st.session_state.autenticado = False
            st.rerun()
