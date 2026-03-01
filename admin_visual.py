import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import os
import json

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="G-LAB PEPTIDES", layout="wide", page_icon="🧪")

# Remove elementos nativos do Streamlit para o site ser o protagonista
st.markdown("""
    <style>
        .block-container { padding: 0rem; }
        iframe { border: none; }
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .stButton>button { width: 100%; border-radius: 5px; }
    </style>
""", unsafe_allow_html=True)

# --- FUNÇÃO QUE GERA O SITE (HTML COMPLETO) ---
def gerar_site_vendas():
    diretorio = os.path.dirname(os.path.abspath(__file__))
    caminho_dados = os.path.join(diretorio, 'stock_0202 - NOVA.xlsx')
    
    # Lógica de integração com seu Excel
    produtos_json = "[]"
    if os.path.exists(caminho_dados):
        try:
            df = pd.read_excel(caminho_dados)
            df.columns = [str(col).strip().upper() for col in df.columns]
            lista = []
            for _, row in df.iterrows():
                lista.append({
                    "nome": str(row.get('PRODUTO', 'N/A')),
                    "espec": f"{row.get('VOLUME', '')} {row.get('MEDIDA', '')}",
                    "preco": float(row.get('PREÇO (R$)', 0)),
                    "status": "EM ESTOQUE"
                })
            produtos_json = json.dumps(lista)
        except:
            produtos_json = "[]"

    # TODO O SEU CÓDIGO HTML/CSS/JS CONSOLIDADO AQUI
    html_content = f"""
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            :root {{ --primary: #007bff; --secondary: #6c757d; --success: #28a745; --dark: #343a40; }}
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f7f6; margin: 0; padding: 10px; }}
            .container {{ max-width: 800px; margin: auto; background: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }}
            .logo {{ display: block; margin: 0 auto 20px; max-width: 250px; }}
            .card {{ border: 1px solid #eee; padding: 15px; border-radius: 10px; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center; }}
            .badge-espera {{ background: #ffebee; color: #c62828; padding: 5px 10px; border-radius: 5px; font-size: 12px; font-weight: bold; border: 1px solid #ef9a9a; }}
            .btn-add {{ background: #e0e0e0; border: none; padding: 8px 15px; border-radius: 5px; cursor: pointer; font-weight: bold; }}
            .checkout-btn {{ background: #25d366; color: white; width: 100%; border: none; padding: 15px; border-radius: 8px; font-size: 18px; font-weight: bold; cursor: pointer; margin-top: 20px; }}
            input[type="text"] {{ width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ddd; border-radius: 8px; box-sizing: border-box; }}
            .btn-calc {{ background: #28a745; color: white; border: none; padding: 12px 20px; border-radius: 8px; cursor: pointer; }}
            /* Modal e Outros Estilos do seu código */
            #modalCheckout {{ display:none; position:fixed; z-index:100; left:0; top:0; width:100%; height:100%; background:rgba(0,0,0,0.5); overflow-y:auto; }}
            .modal-content {{ background:white; margin:5% auto; padding:20px; width:90%; max-width:500px; border-radius:10px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <img src="https://github.com/glabpep/ordem/blob/main/1.png?raw=true" class="logo">
            <h3 style="text-align:center; color:#333;">Estoque Atualizado e Pedidos Online</h3>
            
            <div style="background:#e3f2fd; border-left:5px solid #2196f3; padding:15px; border-radius:5px; margin-bottom:20px;">
                📢 <b>Previsão de chegada: 09/03/2026</b>
            </div>

            <div style="border: 2px solid #007bff; padding: 15px; border-radius: 10px; margin-bottom:20px;">
                <label>🚚 <b>1. Informe seu CEP para Localizar Região:</b></label>
                <div style="display:flex; gap:10px;">
                    <input type="text" id="cep-destino" placeholder="00000-000">
                    <button class="btn-calc" id="btn-calc" onclick="calcularFrete()">Localizar</button>
                </div>
                <div id="resultado-frete" style="font-weight:bold; color:#007bff; margin-top:10px;"></div>
            </div>

            <div id="lista-produtos"></div>

            <button class="checkout-btn" onclick="abrirCheckout()">🛒 FINALIZAR PEDIDO VIA WHATSAPP</button>
        </div>

        <div id="modalCheckout">
            <div class="modal-content">
                <h3>Dados para Entrega</h3>
                <input type="text" id="f_nome" placeholder="NOME COMPLETO">
                <input type="text" id="f_tel" placeholder="WHATSAPP (COM DDD)">
                <input type="text" id="f_end" placeholder="ENDEREÇO / RUA">
                <input type="text" id="f_num" placeholder="NÚMERO">
                <input type="text" id="f_ba" placeholder="BAIRRO">
                <input type="text" id="f_ci" placeholder="CIDADE">
                <input type="text" id="f_es" placeholder="ESTADO (UF)">
                <select id="f_pgto" style="width:100%; padding:10px; margin-top:10px; border-radius:8px;">
                    <option value="PIX">PIX (5% de Desconto)</option>
                    <option value="CARTÃO">CARTÃO DE CRÉDITO</option>
                </select>
                <button class="checkout-btn" onclick="enviarPedido()">ENVIAR PARA O WHATSAPP</button>
                <button onclick="document.getElementById('modalCheckout').style.display='none'" style="width:100%; background:none; border:none; color:red; cursor:pointer; margin-top:10px;">CANCELAR</button>
            </div>
        </div>

        <script>
            const PRODUTOS_BD = {produtos_json};
            let freteV = 0;
            let freteD = "";

            function renderizar() {{
                const lista = document.getElementById('lista-produtos');
                lista.innerHTML = "";
                PRODUTOS_BD.forEach(p => {{
                    lista.innerHTML += `
                        <div class="card">
                            <div>
                                <b>${{p.nome}}</b><br><small>${{p.espec}}</small>
                            </div>
                            <div style="text-align:right">
                                <span class="badge-espera">EM ESPERA</span><br>
                                <b>R$ ${{p.preco.toFixed(2)}}</b>
                            </div>
                        </div>
                    `;
                }});
            }}

            async function calcularFrete() {{
                const cep = document.getElementById('cep-destino').value.replace(/\D/g,'');
                if(cep.length !== 8) return alert("CEP Inválido");
                
                document.getElementById('btn-calc').innerText = "...";
                try {{
                    const res = await fetch(`https://viacep.com.br/ws/${{cep}}/json/`);
                    const data = await res.json();
                    if(data.erro) throw new Error();
                    
                    // Lógica simplificada de frete
                    freteV = 90.00;
                    freteD = "SUL/SUDESTE R$ 90,00";
                    document.getElementById('resultado-frete').innerText = "✅ " + data.localidade + "/" + data.uf + ": " + freteD;
                    document.getElementById('f_ci').value = data.localidade;
                    document.getElementById('f_es').value = data.uf;
                }} catch(e) {{
                    alert("Erro ao buscar CEP");
                }}
                document.getElementById('btn-calc').innerText = "Localizar";
            }}

            function abrirCheckout() {{
                if(freteV === 0) return alert("Calcule o frete primeiro!");
                document.getElementById('modalCheckout').style.display = 'block';
            }}

            function enviarPedido() {{
                const nome = document.getElementById('f_nome').value;
                if(!nome) return alert("Preencha o nome!");
                
                let msg = "*NOVO PEDIDO G-LAB*%0A%0A";
                msg += "*CLIENTE:* " + nome + "%0A";
                msg += "*FRETE:* " + freteD;
                
                window.open("https://wa.me/+17746222523?text=" + msg, '_blank');
            }}

            renderizar();
        </script>
    </body>
    </html>
    """
    return html_content

# --- LÓGICA DE NAVEGAÇÃO STREAMLIT ---
if "view" not in st.session_state:
    st.session_state.view = "loja"

# Barra lateral discreta
with st.sidebar:
    st.image("1.png", width=100)
    if st.button("⚙️ Acesso Restrito"):
        st.session_state.view = "login"
    if st.session_state.view != "loja":
        if st.button("🛒 Voltar ao Site"):
            st.session_state.view = "loja"
            st.rerun()

# Renderização das Telas
if st.session_state.view == "loja":
    # EXIBE SEU SITE DE VENDAS COMO PRINCIPAL
    html_loja = gerar_site_vendas()
    components.html(html_loja, height=1800, scrolling=True)

elif st.session_state.view == "login":
    st.title("🔐 Login")
    u = st.text_input("Usuário")
    s = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        if u == "admin" and s == "glab2026":
            st.session_state.view = "admin"
            st.rerun()

elif st.session_state.view == "admin":
    st.title("📊 Gestão de Estoque")
    df = pd.read_excel('stock_0202 - NOVA.xlsx')
    st.dataframe(df, use_container_width=True)
    st.info("As alterações feitas no Excel acima refletem automaticamente no site principal.")
