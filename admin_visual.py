import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import os
import json

# --- 1. CONFIGURAÇÃO E ESTADO (MANTIDO INTEGRALMENTE) ---
st.set_page_config(page_title="G-LAB PEPTIDES", layout="wide", page_icon="🧪")

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

st.markdown("""
    <style>
        .block-container { padding: 0rem; }
        footer {visibility: hidden;}
        header {visibility: hidden;}
        [data-testid="stSidebar"] { background-color: #f8f9fa; border-right: 1px solid #ddd; }
    </style>
""", unsafe_allow_html=True)

# --- 2. GESTÃO DE DADOS (SUA LÓGICA DE ARQUIVOS) ---
def carregar_estoque():
    diretorio_atual = os.path.dirname(os.path.abspath(__file__))
    arquivo_dados = None
    for nome in ['stock_0202 - NOVA.xlsx', 'stock_2901.xlsx']:
        caminho = os.path.join(diretorio_atual, nome)
        if os.path.exists(caminho):
            arquivo_dados = caminho
            break
            
    if arquivo_dados:
        try:
            df = pd.read_excel(arquivo_dados)
            df.columns = [str(col).strip().upper() for col in df.columns]
            if 'QTD' in df.columns:
                df['QTD'] = pd.to_numeric(df['QTD'], errors='coerce').fillna(0).astype(int)
            col_preco = 'PREÇO (R$)' if 'PREÇO (R$)' in df.columns else 'PREÇO'
            if col_preco in df.columns:
                df[col_preco] = pd.to_numeric(df[col_preco], errors='coerce').fillna(0)
            return df
        except Exception as e:
            st.error(f"Erro ao ler Excel: {e}")
    return pd.DataFrame()

def salvar_estoque(df):
    df.to_excel("stock_0202 - NOVA.xlsx", index=False)

# --- 3. DICIONÁRIO TÉCNICO INTEGRAL (REINTEGRADO) ---
INFOS_TECNICAS = {
    "5-AMINO": "Inibidor Seletivo de NNMT: Atua bloqueando a enzima nicotinamida N-metiltransferase, o que eleva os níveis de NAD+ e SAM intracelular. Indica eficácia na reversão da obesidade.",
    "AICAR": "Ativador de AMPK: Mimetiza o AMP intracelular para ativar a proteína quinase. Aumenta a oxidação de ácidos graxos e a resistência cardiovascular.",
    "AOD 9604": "Análogo Lipolítico do hGH: Focado na queima de gordura sem induzir efeitos hiperglicêmicos. Promove a lipólise e inibe a lipogênese.",
    "BPC-157": "Peptídeo Regenerativo: Composto derivado do suco gástrico. Demonstra alta eficácia na cicatrização de tendões, ligamentos e tecidos musculares.",
    "CJC-1295": "Análogo de GHRH: Estimula a glândula pituitária a liberar o hormônio do crescimento (GH). Variante com DAC possui meia-vida estendida.",
    "GHK-CU": "Peptídeo de Cobre: Atua na síntese de colágeno e elastina. Possui propriedades anti-inflamatórias potentes e sinaliza a remodelação tecidual.",
    "IPAMORELIN": "Agonista Seletivo de Grelina: Estimula a liberação de GH sem elevar significativamente o cortisol ou prolactina.",
    "MELANOTAN 2": "Análogo de MSH: Estimula a produção de melanina (bronzeamento) e atua nos receptores associados à libido.",
    "TESAMORELIN": "Peptídeo GHRH: Eficaz na redução de gordura visceral abdominal. Melhora o perfil lipídico e a composição corporal.",
    "TB-500": "Timosina Beta-4: Crucial para o reparo celular, migração celular e angiogênese, acelerando a recuperação de lesões.",
    "MK-677": "Secretagogo de GH Oral: Aumenta os níveis de IGF-1 e GH de forma sustentada, promovendo anabolismo e qualidade do sono.",
    "NAD+": "Coenzima Vital: Fundamental para a função mitocondrial e reparo de DNA. Associado à longevidade e energia celular."
}

# --- 4. SITE DE VENDAS (TODAS AS FUNCIONALIDADES ORIGINAIS) ---
def gerar_interface_vendas(df):
    col_preco = 'PREÇO (R$)' if 'PREÇO (R$)' in df.columns else 'PREÇO'
    produtos_json = []
    
    for _, row in df.iterrows():
        nome_original = str(row.get('PRODUTO', ''))
        nome_prod_up = nome_original.strip().upper()
        
        desc_tec = "Peptídeo de alta pureza para fins de pesquisa."
        for chave, info in INFOS_TECNICAS.items():
            if chave in nome_prod_up:
                desc_tec = info
                break
        
        produtos_json.append({
            "nome": nome_original,
            "espec": f"{row.get('VOLUME', '')} {row.get('MEDIDA', '')}",
            "preco": float(row.get(col_preco, 0)),
            "estoque": int(row.get('QTD', 0)),
            "desc": desc_tec,
            "img": f"https://raw.githubusercontent.com/glabpep/ordem/main/{nome_prod_up.replace(' ', '%20')}.webp"
        })
    
    json_data = json.dumps(produtos_json)

    html_code = f"""
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        <style>
            body {{ font-family: 'Segoe UI', sans-serif; margin: 0; background: #f4f7f9; color: #333; }}
            .main-content {{ padding: 15px; max-width: 1200px; margin: 0 auto; padding-bottom: 250px; }}
            
            /* Banner Topo */
            .banner {{ background: #004a99; color: white; padding: 20px; text-align: center; border-radius: 0 0 20px 20px; margin-bottom: 25px; }}
            
            /* Grid de CARDS (A Mudança solicitada) */
            .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 20px; }}
            .card {{ background: white; border-radius: 15px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.08); display: flex; flex-direction: column; position: relative; }}
            
            .img-container {{ width: 100%; height: 220px; background: #fff; position: relative; border-bottom: 1px solid #eee; }}
            .img-container img {{ width: 100%; height: 100%; object-fit: contain; padding: 10px; box-sizing: border-box; }}
            
            .badge {{ position: absolute; top: 12px; right: 12px; padding: 6px 12px; border-radius: 20px; font-size: 10px; font-weight: bold; text-transform: uppercase; }}
            .disponivel {{ background: #e6fcf5; color: #0ca678; border: 1px solid #0ca678; }}
            .esgotado {{ background: #fff5f5; color: #fa5252; border: 1px solid #fa5252; }}
            
            .card-content {{ padding: 20px; flex-grow: 1; display: flex; flex-direction: column; }}
            .card-title {{ font-size: 18px; font-weight: bold; margin: 0; color: #111; }}
            .card-espec {{ color: #004a99; font-weight: 600; font-size: 14px; margin: 5px 0; }}
            .card-desc {{ font-size: 12px; color: #777; line-height: 1.4; margin-bottom: 15px; height: 50px; overflow: hidden; }}
            .card-price {{ font-size: 22px; font-weight: 800; color: #111; margin-bottom: 15px; }}
            
            .btn-add {{ background: #004a99; color: white; border: none; padding: 14px; border-radius: 10px; font-weight: bold; cursor: pointer; transition: 0.2s; }}
            .btn-add:hover {{ background: #003366; }}
            .btn-off {{ background: #eee; color: #999; border: none; padding: 14px; border-radius: 10px; cursor: not-allowed; }}

            /* Carrinho (Lógica Original Mantida) */
            .sidebar-cart {{ 
                width: 380px; background: #004a99; color: white; height: 100vh; position: fixed; right: 0; top: 0; 
                padding: 30px; box-sizing: border-box; display: flex; flex-direction: column; z-index: 1000; box-shadow: -5px 0 20px rgba(0,0,0,0.2); 
            }}
            
            @media (max-width: 900px) {{
                .sidebar-cart {{ width: 100%; height: auto; top: auto; bottom: 0; padding: 20px; border-radius: 25px 25px 0 0; }}
                .cart-items {{ display: none; }}
                .main-content {{ padding-bottom: 230px; }}
            }}

            .cart-items {{ flex-grow: 1; overflow-y: auto; margin: 20px 0; }}
            .cart-item {{ display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid rgba(255,255,255,0.1); font-size: 14px; }}
            .total-box {{ background: rgba(0,0,0,0.2); padding: 20px; border-radius: 15px; }}
            .btn-checkout {{ background: white; color: #004a99; border: none; width: 100%; padding: 18px; border-radius: 12px; font-weight: bold; font-size: 16px; cursor: pointer; margin-top: 15px; }}

            /* Modal (Original) */
            .modal {{ display:none; position:fixed; z-index:2000; left:0; top:0; width:100%; height:100%; background:rgba(0,0,0,0.85); }}
            .modal-content {{ background:white; max-width: 480px; margin: 40px auto; padding: 30px; border-radius: 20px; position: relative; color: #333; }}
            .modal-content input, select {{ width: 100%; padding: 14px; margin: 10px 0; border: 1px solid #ddd; border-radius: 10px; box-sizing: border-box; font-size: 16px; }}
        </style>
    </head>
    <body>
        <div class="main-content">
            <div class="banner">
                <img src="https://github.com/glabpep/ordem/blob/main/1.png?raw=true" width="180"><br>
                <p style="margin-top:10px; font-size:14px; opacity:0.9;">Qualidade Analítica para Pesquisa Avançada</p>
            </div>
            
            <div class="grid" id="grid-produtos"></div>
        </div>

        <div class="sidebar-cart">
            <div style="font-size: 22px; font-weight: bold; display:flex; justify-content:space-between;">
                <span><i class="fas fa-shopping-bag"></i> MEU PEDIDO</span>
                <span id="cart-count">0</span>
            </div>
            
            <div id="cart-items" class="cart-items"></div>
            
            <div class="total-box">
                <input type="text" id="cupom" oninput="atualizar()" placeholder="CUPOM DE DESCONTO" style="width:100%; padding:10px; border-radius:8px; border:none; margin-bottom:15px; font-weight:bold; text-align:center;">
                <div style="display:flex; justify-content:space-between; font-size:22px; font-weight:bold;">
                    <span>TOTAL:</span><span id="txt-total">R$ 0,00</span>
                </div>
                <button class="btn-checkout" onclick="abrirCheckout()">FINALIZAR COMPRA</button>
            </div>
        </div>

        <div id="modal-checkout" class="modal">
            <div class="modal-content">
                <h2 style="margin-top:0; color:#004a99;">Finalizar Envio</h2>
                <input type="text" id="f_nome" placeholder="Nome Completo">
                <input type="text" id="f_cep" placeholder="CEP" onblur="cotarFrete(this.value)">
                <input type="text" id="f_end" placeholder="Endereço, Número e Bairro">
                <div style="display:flex; gap:10px;">
                    <input type="text" id="f_cidade" placeholder="Cidade">
                    <input type="text" id="f_uf" placeholder="UF" maxlength="2">
                </div>
                <input type="text" id="f_whats" placeholder="WhatsApp">
                <select id="f_pgto">
                    <option value="Pix (5% Desconto)">Pix (5% Desconto)</option>
                    <option value="Cartão de Crédito">Cartão de Crédito</option>
                </select>
                <button onclick="finalizar()" style="background:#28a745; color:white; border:none; width:100%; padding:20px; border-radius:12px; font-weight:bold; font-size:18px; cursor:pointer;">ENVIAR PEDIDO</button>
                <center><button onclick="fecharCheckout()" style="background:none; border:none; color:#999; margin-top:20px; cursor:pointer;">Voltar à Loja</button></center>
            </div>
        </div>

        <script>
            const PRODUTOS = {json_data};
            let carrinho = [];
            let valorFrete = 0;

            function renderizar() {{
                const grid = document.getElementById('grid-produtos');
                grid.innerHTML = PRODUTOS.map((p, i) => `
                    <div class="card">
                        <div class="img-container">
                            <img src="${{p.img}}" onerror="this.src='https://via.placeholder.com/300x300?text=PEPTIDE'">
                            <span class="badge ${{p.estoque > 0 ? 'disponivel' : 'esgotado'}}">
                                ${{p.estoque > 0 ? 'Disponível' : 'Em Falta'}}
                            </span>
                        </div>
                        <div class="card-content">
                            <h3 class="card-title">${{p.nome}}</h3>
                            <div class="card-espec">${{p.espec}}</div>
                            <div class="card-desc">${{p.desc}}</div>
                            <div class="card-price">R$ ${{p.preco.toLocaleString('pt-BR', {{minimumFractionDigits: 2}})}}</div>
                            ${{p.estoque > 0 
                                ? `<button class="btn-add" onclick="add(${{i}})">ADICIONAR</button>` 
                                : `<button class="btn-off">AVISE-ME</button>`}}
                        </div>
                    </div>
                `).join('');
            }}

            function add(idx) {{ carrinho.push(PRODUTOS[idx]); atualizar(); }}
            function remove(idx) {{ carrinho.splice(idx, 1); atualizar(); }}

            function atualizar() {{
                const lista = document.getElementById('cart-items');
                document.getElementById('cart-count').innerText = carrinho.length;
                
                if(carrinho.length === 0) {{
                    lista.innerHTML = '<p style="text-align:center; opacity:0.5;">Seu carrinho está vazio.</p>';
                    document.getElementById('txt-total').innerText = "R$ 0,00";
                    return;
                }}

                lista.innerHTML = carrinho.map((p, i) => `
                    <div class="cart-item">
                        <span>${{p.nome}}</span>
                        <span>R$ ${{p.preco.toFixed(2)}} <i class="fas fa-times-circle" onclick="remove(${{i}})" style="color:#ff6b6b; cursor:pointer; margin-left:8px;"></i></span>
                    </div>
                `).join('');

                // Lógica de Cupons Original
                let sub = carrinho.reduce((acc, p) => acc + p.preco, 0);
                let cupom = document.getElementById('cupom').value.toUpperCase();
                let desc = 0;
                if(cupom === "CABRAL5" || cupom === "BRUNA5") desc = 0.05;
                if(cupom === "DAFNE10") desc = 0.10;

                let total = (sub * (1 - desc)) + valorFrete;
                document.getElementById('txt-total').innerText = "R$ " + total.toLocaleString('pt-BR', {{minimumFractionDigits: 2}});
            }}

            async function cotarFrete(cep) {{
                cep = cep.replace(/\D/g, '');
                if(cep.length === 8) {{
                    const resp = await fetch(\`https://viacep.com.br/ws/${{cep}}/json/\`);
                    const d = await resp.json();
                    if(!d.erro) {{
                        document.getElementById('f_cidade').value = d.localidade;
                        document.getElementById('f_uf').value = d.uf;
                        document.getElementById('f_end').value = d.logradouro + " - " + d.bairro;
                        
                        // Lógica de Frete Original
                        const regiao = ['SP','RJ','MG','ES','PR','SC','RS'];
                        valorFrete = regiao.includes(d.uf) ? 90 : 165;
                        atualizar();
                    }}
                }}
            }}

            function abrirCheckout() {{ if(carrinho.length > 0) document.getElementById('modal-checkout').style.display='block'; }}
            function fecharCheckout() {{ document.getElementById('modal-checkout').style.display='none'; }}

            function finalizar() {{
                const nome = document.getElementById('f_nome').value;
                if(!nome) return alert("Por favor, informe seu nome.");
                
                let cupom = document.getElementById('cupom').value.toUpperCase();
                let temBrinde = (cupom === "BRUNA5");
                
                let msg = "*NOVO PEDIDO G-LAB*%0A%0A";
                msg += "*CLIENTE:* " + nome.toUpperCase() + "%0A";
                msg += "*PRODUTOS:*%0A" + carrinho.map(p => "- " + p.nome).join("%0A");
                if(temBrinde) msg += "%0A*🎁 BRINDE:* Bacteriostatic Water 7ml (Cupom Bruna)";
                msg += "%0A%0A*TOTAL:* " + document.getElementById('txt-total').innerText;
                
                window.open("https://wa.me/17746222523?text=" + msg);
            }}

            renderizar();
        </script>
    </body>
    </html>
    """
    return html_code

# --- 5. LÓGICA DE NAVEGAÇÃO E ADMIN (100% ORIGINAL) ---
df_estoque = carregar_estoque()

with st.sidebar:
    st.image("https://github.com/glabpep/ordem/blob/main/1.png?raw=true", width=150)
    st.write("---")
    menu = st.radio("Menu de Acesso", ["🛒 Loja de Peptídeos", "🔐 Administrativo"])

if menu == "🛒 Loja de Peptídeos":
    components.html(gerar_interface_vendas(df_estoque), height=1800, scrolling=True)

else:
    if not st.session_state.autenticado:
        st.subheader("Login Administrativo")
        u = st.text_input("Usuário")
        p = st.text_input("Senha", type="password")
        if st.button("Entrar"):
            if u == "admin" and p == "glab2026":
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.error("Credenciais incorretas.")
    else:
        st.title("📦 Controle de Estoque")
        st.dataframe(df_estoque, use_container_width=True)
        
        st.write("---")
        st.subheader("Registrar Venda/Saída")
        p_sel = st.selectbox("Selecione o Item", df_estoque['PRODUTO'].tolist())
        q_venda = st.number_input("Quantidade", min_value=1, value=1)
        
        if st.button("ATUALIZAR ESTOQUE"):
            idx = df_estoque[df_estoque['PRODUTO'] == p_sel].index[0]
            if df_estoque.at[idx, 'QTD'] >= q_venda:
                df_estoque.at[idx, 'QTD'] -= q_venda
                salvar_estoque(df_estoque)
                st.success(f"Saída de {q_venda} unidades de {p_sel} registrada!")
                st.rerun()
            else:
                st.error("Quantidade solicitada maior que o estoque disponível!")
