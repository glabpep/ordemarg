import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import os
import json

# --- 1. CONFIGURAÇÃO DE PÁGINA E ESTILO STREAMLIT ---
st.set_page_config(page_title="G-LAB PEPTIDES", layout="wide", page_icon="🧪")

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

# CSS para esconder elementos padrão do Streamlit e garantir tela cheia
st.markdown("""
    <style>
        .block-container { padding: 0rem; }
        footer {visibility: hidden;}
        header {visibility: hidden;}
        #MainMenu {visibility: hidden;}
        [data-testid="stSidebar"] { background-color: #f8f9fa; border-right: 1px solid #ddd; }
        @media (max-width: 768px) {
            .stMain { padding: 0px; }
        }
    </style>
""", unsafe_allow_html=True)

# --- 2. GESTÃO DE DADOS (EXCEL) ---
def carregar_estoque():
    # Mantendo a lógica de busca em múltiplos arquivos conforme o original
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
            # Limpeza e conversão rigorosa para evitar erros no JS
            if 'QTD' in df.columns:
                df['QTD'] = pd.to_numeric(df['QTD'], errors='coerce').fillna(0).astype(int)
            if 'PREÇO (R$)' in df.columns:
                df['PREÇO (R$)'] = pd.to_numeric(df['PREÇO (R$)'], errors='coerce').fillna(0)
            elif 'PREÇO' in df.columns:
                df['PREÇO'] = pd.to_numeric(df['PREÇO'], errors='coerce').fillna(0)
            return df
        except Exception as e:
            st.error(f"Erro ao ler Excel: {e}")
    return pd.DataFrame(columns=['PRODUTO', 'VOLUME', 'MEDIDA', 'PREÇO', 'QTD'])

def salvar_estoque(df):
    caminho = "stock_0202 - NOVA.xlsx"
    df.to_excel(caminho, index=False)

# --- 3. DICIONÁRIO TÉCNICO INTEGRAL (REINTEGRADO 100%) ---
INFOS_TECNICAS = {
    "5-AMINO": "Inibidor Seletivo de NNMT: Atua bloqueando a enzima nicotinamida N-metiltransferase, o que eleva os níveis de NAD+ e SAM intracelular. Indica eficácia na reversão da obesidade e otimização do gasto energético basal.",
    "AICAR": "Ativador de AMPK: Mimetiza o AMP intracelular para ativar a proteína quinase. Investigado por aumentar a captação de glicose muscular, a oxidação de ácidos graxos e a resistência cardiovascular.",
    "AOD 9604": "Análogo Lipolítico do hGH: Focado no isolamento das propriedades de queima de gordura do GH sem induzir efeitos hiperglicêmicos. Promove a lipólise e inibe a lipogênese.",
    "BPC-157": "Peptídeo Regenerativo: Composto de 15 aminoácidos derivado do suco gástrico humano. Demonstra alta eficácia na cicatrização de tendões, ligamentos, músculos e saúde do trato gastrointestinal.",
    "CJC-1295": "Análogo de GHRH: Estimula a glândula pituitária a liberar o hormônio do crescimento (GH). A variante com DAC possui uma meia-vida estendida, proporcionando liberação contínua.",
    "GHK-CU": "Peptídeo de Cobre: Atua na síntese de colágeno, elastina e glicosaminoglicanos. Possui propriedades anti-inflamatórias potentes e sinaliza a remodelação tecidual.",
    "IPAMORELIN": "Agonista Seletivo de Grelina: O mais limpo dos secretagogos de GH. Estimula a liberação de GH sem elevar significativamente o cortisol, prolactina ou estimular o apetite excessivo.",
    "MELANOTAN 2": "Análogo de MSH: Estimula a produção de melanina (bronzeamento) de forma sistêmica e atua nos receptores de melanocortina associados à função erétil e libido.",
    "TESAMORELIN": "Peptídeo GHRH: Especificamente aprovado em estudos para a redução de gordura visceral abdominal (lipodistrofia). Melhora o perfil lipídico e a composição corporal.",
    "TB-500": "Timosina Beta-4: Crucial para o reparo e regeneração celular. Atua na migração celular e angiogênese (criação de novos vasos), acelerando a recuperação de lesões agudas e crônicas.",
    "MK-677": "Secretagogo de GH Oral: Mimetiza a ação da grelina. Aumenta os níveis de IGF-1 e GH de forma sustentada por 24 horas, promovendo anabolismo e qualidade do sono.",
    "NAD+": "Coenzima Vital: Fundamental para a função mitocondrial e reparo de DNA através das sirtuínas. Associado à longevidade, clareza mental e recuperação de energia celular.",
    "GLUTA": "Glutationa: O principal antioxidante endógeno. Essencial para desintoxicação hepática e proteção contra estresse oxidativo celular.",
    "SOMA": "Somatropina: Hormônio do crescimento bioidêntico. Atua no crescimento celular global, queima de gordura e regeneração de tecidos profundos."
}

# --- 4. INTERFACE DE VENDAS (HTML/JS/CSS COMPLETO E RESPONSIVO) ---
def gerar_interface_vendas(df):
    produtos_json = []
    for _, row in df.iterrows():
        nome_original = str(row.get('PRODUTO', 'SEM NOME'))
        nome_prod = nome_original.strip().upper()
        
        # Lógica de busca de descrição técnica
        desc = "Peptídeo de alta pureza para fins de pesquisa e desenvolvimento laboratorial."
        for chave, info in INFOS_TECNICAS.items():
            if chave in nome_prod:
                desc = info
                break
        
        produtos_json.append({
            "nome": nome_original,
            "espec": f"{row.get('VOLUME', '')} {row.get('MEDIDA', '')}",
            "preco": float(row.get('PREÇO (R$)', row.get('PREÇO', 0))),
            "estoque": int(row.get('QTD', 0)),
            "desc": desc,
            "img": f"https://raw.githubusercontent.com/glabpep/ordem/main/{nome_prod.replace(' ', '%20')}.webp"
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
            :root {{ --primary: #004a99; --secondary: #28a745; --bg: #f4f7f9; --text: #333; }}
            body {{ font-family: 'Segoe UI', Roboto, sans-serif; margin: 0; background-color: var(--bg); display: flex; flex-direction: column; color: var(--text); }}
            
            .main-content {{ flex: 1; padding: 15px; max-width: 1200px; margin: 0 auto; box-sizing: border-box; width: 100%; padding-bottom: 200px; }}
            
            /* Header/Banners */
            .header-loja {{ text-align: center; padding: 20px 0; }}
            .banner-info {{ background: #e3f2fd; color: #0d47a1; padding: 15px; border-radius: 10px; border-left: 5px solid #2196f3; font-size: 14px; margin-bottom: 20px; text-align: left; }}
            
            /* Grid de Cards */
            .grid-produtos {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; }}
            
            .card {{ background: white; border-radius: 15px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.08); display: flex; flex-direction: column; position: relative; transition: 0.3s; }}
            .card:hover {{ transform: translateY(-5px); }}
            
            .img-box {{ width: 100%; height: 220px; background: #fff; position: relative; border-bottom: 1px solid #eee; }}
            .img-box img {{ width: 100%; height: 100%; object-fit: contain; padding: 10px; box-sizing: border-box; }}
            
            .badge-estoque {{ position: absolute; top: 12px; right: 12px; padding: 6px 12px; border-radius: 20px; font-size: 11px; font-weight: bold; text-transform: uppercase; }}
            .disponivel {{ background: #e6fcf5; color: #0ca678; border: 1px solid #0ca678; }}
            .esgotado {{ background: #fff5f5; color: #fa5252; border: 1px solid #fa5252; }}
            
            .card-body {{ padding: 20px; flex: 1; display: flex; flex-direction: column; }}
            .card-title {{ font-size: 18px; font-weight: bold; margin: 0; color: #111; }}
            .card-espec {{ color: #004a99; font-weight: 600; font-size: 14px; margin: 5px 0 15px 0; }}
            .card-desc {{ font-size: 12.5px; color: #666; line-height: 1.5; margin-bottom: 15px; flex-grow: 1; }}
            .card-price {{ font-size: 24px; font-weight: 800; color: #111; margin-bottom: 20px; }}
            
            .btn-comprar {{ background: var(--primary); color: white; border: none; padding: 14px; border-radius: 10px; font-weight: bold; cursor: pointer; font-size: 14px; transition: 0.2s; }}
            .btn-comprar:hover {{ opacity: 0.9; }}
            .btn-disabled {{ background: #e9ecef; color: #adb5bd; cursor: not-allowed; border: none; padding: 14px; border-radius: 10px; font-weight: bold; width: 100%; }}

            /* Carrinho Lateral/Mobile */
            .sidebar-cart {{ 
                width: 380px; background: var(--primary); color: white; height: 100vh; position: fixed; right: 0; top: 0; 
                padding: 30px; box-sizing: border-box; display: flex; flex-direction: column; z-index: 2000; box-shadow: -5px 0 25px rgba(0,0,0,0.2); 
            }}
            
            @media (max-width: 900px) {{
                .sidebar-cart {{ width: 100%; height: auto; top: auto; bottom: 0; padding: 20px; border-radius: 25px 25px 0 0; }}
                .cart-items {{ max-height: 150px; overflow-y: auto; display: none; }}
                .main-content {{ padding-bottom: 220px; }}
                .grid-produtos {{ grid-template-columns: 1fr; }}
            }}

            .cart-item {{ display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid rgba(255,255,255,0.1); font-size: 14px; }}
            .total-box {{ background: rgba(0,0,0,0.2); padding: 20px; border-radius: 15px; margin-top: 15px; }}
            .total-row {{ display: flex; justify-content: space-between; font-size: 22px; font-weight: bold; margin-bottom: 15px; }}
            
            .btn-finalizar {{ background: white; color: var(--primary); border: none; width: 100%; padding: 18px; border-radius: 12px; font-weight: bold; cursor: pointer; font-size: 16px; }}

            /* Modal Checkout */
            .modal {{ display:none; position:fixed; z-index:3000; left:0; top:0; width:100%; height:100%; background:rgba(0,0,0,0.85); overflow-y: auto; padding: 10px; box-sizing: border-box; }}
            .modal-content {{ background:white; max-width: 500px; margin: 30px auto; padding: 30px; border-radius: 20px; position: relative; }}
            .modal-content input, .modal-content select {{ width: 100%; padding: 14px; margin: 10px 0; border: 1px solid #ddd; border-radius: 10px; box-sizing: border-box; }}
        </style>
    </head>
    <body>
        <div class="main-content">
            <div class="header-loja">
                <img src="https://github.com/glabpep/ordem/blob/main/1.png?raw=true" width="220">
            </div>
            
            <div class="banner-info">
                <i class="fas fa-info-circle"></i> <b>AVISO IMPORTANTE:</b> Os produtos são envasados em forma sólida (liofilizada). Para reconstituição, utilize <b>Bacteriostatic Water</b>. Próximo lote: 09/03/2026.
            </div>

            <div class="grid-produtos" id="lista-produtos"></div>
        </div>

        <div class="sidebar-cart">
            <div style="font-size: 22px; font-weight: bold; margin-bottom: 20px; display: flex; justify-content: space-between;">
                <span><i class="fas fa-shopping-bag"></i> SEU PEDIDO</span>
                <span id="cart-count-badge">0</span>
            </div>
            
            <div id="cart-items-list" class="cart-items"></div>
            
            <div class="total-box">
                <input type="text" id="cupom_input" oninput="atualizarCarrinho()" placeholder="CUPOM DE DESCONTO" style="width:100%; padding:10px; border-radius:8px; border:none; margin-bottom:15px; font-weight:bold;">
                <div class="total-row">
                    <span>TOTAL</span>
                    <span id="label-total">R$ 0,00</span>
                </div>
                <button class="btn-finalizar" onclick="abrirCheckout()">FINALIZAR COMPRA</button>
            </div>
        </div>

        <div id="modal-checkout" class="modal">
            <div class="modal-content">
                <h2 style="margin-top:0; color:var(--primary);">Dados de Entrega</h2>
                <input type="text" id="f_nome" placeholder="Nome Completo">
                <input type="text" id="f_cep" placeholder="CEP" onblur="validarCEP(this.value)">
                <input type="text" id="f_end" placeholder="Rua, Número e Bairro">
                <div style="display:flex; gap:10px;">
                    <input type="text" id="f_cidade" placeholder="Cidade">
                    <input type="text" id="f_uf" placeholder="UF" maxlength="2">
                </div>
                <input type="text" id="f_whats" placeholder="WhatsApp com DDD">
                <select id="f_pagamento">
                    <option value="Pix (5% Desconto)">Pix (5% Desconto)</option>
                    <option value="Cartão de Crédito">Cartão de Crédito</option>
                </select>
                <button onclick="enviarPedido()" style="background:#28a745; color:white; border:none; width:100%; padding:20px; border-radius:12px; font-weight:bold; cursor:pointer; font-size:18px; margin-top:10px;">CONCLUIR NO WHATSAPP</button>
                <center><button onclick="fecharCheckout()" style="background:none; border:none; color:#999; margin-top:15px; cursor:pointer;">Cancelar e Voltar</button></center>
            </div>
        </div>

        <script>
            const DATA_ESTOQUE = {json_data};
            let carrinho = [];
            let freteValor = 0;

            function renderizarProdutos() {{
                const grid = document.getElementById('lista-produtos');
                grid.innerHTML = DATA_ESTOQUE.map((p, i) => `
                    <div class="card">
                        <div class="img-box">
                            <img src="${{p.img}}" onerror="this.src='https://via.placeholder.com/400x300?text=LAB+RESEARCH'">
                            <span class="badge-estoque ${{p.estoque > 0 ? 'disponivel' : 'esgotado'}}">
                                ${{p.estoque > 0 ? 'Disponível' : 'Esgotado'}}
                            </span>
                        </div>
                        <div class="card-body">
                            <h3 class="card-title">${{p.nome}}</h3>
                            <div class="card-espec">${{p.espec}}</div>
                            <div class="card-desc">${{p.desc}}</div>
                            <div class="card-price">R$ ${{p.preco.toLocaleString('pt-BR', {{minimumFractionDigits: 2}})}}</div>
                            ${{p.estoque > 0 
                                ? `<button class="btn-comprar" onclick="adicionar(${{i}})">ADICIONAR AO PEDIDO</button>` 
                                : `<button class="btn-disabled">EM FALTA</button>`}}
                        </div>
                    </div>
                `).join('');
            }}

            function adicionar(idx) {{
                carrinho.push(DATA_ESTOQUE[idx]);
                atualizarCarrinho();
            }}

            function remover(idx) {{
                carrinho.splice(idx, 1);
                atualizarCarrinho();
            }}

            function atualizarCarrinho() {{
                const lista = document.getElementById('cart-items-list');
                const badge = document.getElementById('cart-count-badge');
                badge.innerText = carrinho.length;
                
                if(carrinho.length === 0) {{
                    lista.innerHTML = '<p style="text-align:center; opacity:0.6;">Carrinho vazio</p>';
                    document.getElementById('label-total').innerText = "R$ 0,00";
                    return;
                }}

                lista.innerHTML = carrinho.map((item, i) => `
                    <div class="cart-item">
                        <span>${{item.nome}}</span>
                        <span>R$ ${{item.preco.toFixed(2)}} <i class="fas fa-trash" onclick="remover(${{i}})" style="cursor:pointer; color:#ff6b6b; margin-left:10px;"></i></span>
                    </div>
                `).join('');

                // Lógica de Cupom do Original
                let subtotal = carrinho.reduce((acc, p) => acc + p.preco, 0);
                let cupom = document.getElementById('cupom_input').value.toUpperCase();
                let desc = 0;
                if(cupom === "CABRAL5" || cupom === "BRUNA5") desc = 0.05;
                if(cupom === "DAFNE10") desc = 0.10;

                let total = (subtotal * (1 - desc)) + freteValor;
                document.getElementById('label-total').innerText = "R$ " + total.toLocaleString('pt-BR', {{minimumFractionDigits: 2}});
            }}

            async function validarCEP(cep) {{
                cep = cep.replace(/\D/g, '');
                if(cep.length === 8) {{
                    try {{
                        const r = await fetch(\`https://viacep.com.br/ws/${{cep}}/json/\`);
                        const d = await r.json();
                        if(!d.erro) {{
                            document.getElementById('f_cidade').value = d.localidade;
                            document.getElementById('f_uf').value = d.uf;
                            document.getElementById('f_end').value = d.logradouro + ", " + d.bairro;
                            
                            // Lógica de Frete do Original
                            const sul_sudeste = ['SP','RJ','MG','ES','PR','SC','RS'];
                            freteValor = sul_sudeste.includes(d.uf) ? 90 : 165;
                            atualizarCarrinho();
                        }}
                    }} catch(e) {{}}
                }}
            }}

            function abrirCheckout() {{ if(carrinho.length > 0) document.getElementById('modal-checkout').style.display='block'; }}
            function fecharCheckout() {{ document.getElementById('modal-checkout').style.display='none'; }}

            function enviarPedido() {{
                const nome = document.getElementById('f_nome').value;
                if(!nome) return alert("Preencha seu nome");
                
                let msg = "*NOVO PEDIDO G-LAB PEPTIDES*%0A%0A";
                msg += "*CLIENTE:* " + nome.toUpperCase() + "%0A";
                msg += "*LOCAL:* " + document.getElementById('f_cidade').value + " / " + document.getElementById('f_uf').value + "%0A%0A";
                msg += "*PRODUTOS:*%0A" + carrinho.map(p => "- " + p.nome + " (" + p.espec + ")").join("%0A");
                msg += "%0A%0A*TOTAL FINAL:* " + document.getElementById('label-total').innerText;
                msg += "%0A*PAGAMENTO:* " + document.getElementById('f_pagamento').value;
                
                window.open("https://wa.me/17746222523?text=" + msg);
            }}

            renderizarProdutos();
        </script>
    </body>
    </html>
    """
    return html_code

# --- 5. LÓGICA DE NAVEGAÇÃO E ADMIN (ESTRUTURA ORIGINAL) ---
df_estoque = carregar_estoque()

with st.sidebar:
    st.image("https://github.com/glabpep/ordem/blob/main/1.png?raw=true", width=150)
    st.write("---")
    menu = st.radio("NAVEGAÇÃO", ["🛒 SITE DE VENDAS", "🔐 ÁREA ADMINISTRATIVA"])

if menu == "🛒 SITE DE VENDAS":
    components.html(gerar_interface_vendas(df_estoque), height=1500, scrolling=True)

else:
    # Área Administrativa Original Mantida Integralmente
    if not st.session_state.autenticado:
        st.subheader("ACESSO RESTRITO")
        u = st.text_input("Usuário")
        p = st.text_input("Senha", type="password")
        if st.button("LOGIN"):
            if u == "admin" and p == "glab2026":
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.error("Credenciais Inválidas")
    else:
        st.title("📦 GESTÃO DE ESTOQUE")
        
        tab_view, tab_edit = st.tabs(["📊 ESTOQUE ATUAL", "✏️ DAR BAIXA"])
        
        with tab_view:
            st.dataframe(df_estoque, use_container_width=True, height=500)
            if st.button("LOGOUT"):
                st.session_state.autenticado = False
                st.rerun()
                
        with tab_edit:
            st.write("Dar baixa em produto:")
            p_lista = df_estoque['PRODUTO'].tolist()
            p_sel = st.selectbox("Selecione o Produto", p_lista)
            q_venda = st.number_input("Quantidade Vendida", min_value=1, value=1)
            
            if st.button("CONFIRMAR ATUALIZAÇÃO"):
                idx = df_estoque[df_estoque['PRODUTO'] == p_sel].index[0]
                if df_estoque.at[idx, 'QTD'] >= q_venda:
                    df_estoque.at[idx, 'QTD'] -= q_venda
                    salvar_estoque(df_estoque)
                    st.success(f"Baixa de {q_venda} un. em {p_sel} realizada!")
                    st.rerun()
                else:
                    st.error("Quantidade em estoque insuficiente!")
