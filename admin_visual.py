import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import os
import json

# --- 1. CONFIGURAÇÃO DE PÁGINA ---
st.set_page_config(page_title="G-LAB PEPTIDES", layout="wide", page_icon="🧪")

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

# CSS para garantir que o Streamlit não interfira no layout do seu index.html
st.markdown("""
    <style>
        .block-container { padding: 0rem; }
        footer {visibility: hidden;}
        header {visibility: hidden;}
        #MainMenu {visibility: hidden;}
        [data-testid="stSidebar"] { background-color: #f8f9fa; border-right: 1px solid #ddd; }
    </style>
""", unsafe_allow_html=True)

# --- 2. GESTÃO DE DADOS (EXCEL) ---
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
        except:
            return pd.DataFrame()
    return pd.DataFrame()

def salvar_estoque(df):
    df.to_excel("stock_0202 - NOVA.xlsx", index=False)

# --- 3. DICIONÁRIO TÉCNICO INTEGRAL ---
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

# --- 4. PREPARAÇÃO DO JSON PARA O FRONT-END ---
df_estoque = carregar_estoque()
col_preco = 'PREÇO (R$)' if 'PREÇO (R$)' in df_estoque.columns else 'PREÇO'
produtos_para_site = []

for _, row in df_estoque.iterrows():
    nome_original = str(row.get('PRODUTO', ''))
    nome_up = nome_original.strip().upper()
    
    desc_tec = "Peptídeo de alta pureza para fins de pesquisa e desenvolvimento."
    for chave, info in INFOS_TECNICAS.items():
        if chave in nome_up:
            desc_tec = info
            break
            
    produtos_para_site.append({
        "nome": nome_original,
        "espec": f"{row.get('VOLUME', '')} {row.get('MEDIDA', '')}",
        "preco": float(row.get(col_preco, 0)),
        "estoque": int(row.get('QTD', 0)),
        "status": str(row.get('ESTOQUE', 'EM ESPERA')).upper(),
        "caracteristica": desc_tec,
        "img": f"https://raw.githubusercontent.com/glabpep/ordem/main/{nome_up.replace(' ', '%20')}.webp"
    })

json_produtos = json.dumps(produtos_para_site)

# --- 5. O FRONT-END INTEGRAL (INDEX.HTML) ---
# Aqui injetamos o seu HTML original com a lógica de renderização dinâmica
html_completo = f"""
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>G-LAB PEPTIDES</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        :root {{ --primary: #004a99; --secondary: #28a745; --danger: #dc3545; --bg: #f4f7f9; }}
        body {{ font-family: 'Segoe UI', Roboto, sans-serif; background: var(--bg); margin: 0; padding: 0; color: #333; }}
        .container {{ max-width: 900px; margin: auto; background: white; min-height: 100vh; padding: 15px; box-sizing: border-box; padding-bottom: 220px; }}
        
        .header-logo-container {{ text-align: center; padding: 10px 0; }}
        .header-logo {{ max-width: 250px; height: auto; }}
        
        .info-alert-card {{ background: #fff3cd; border: 1px solid #ffeeba; color: #856404; padding: 12px; border-radius: 8px; margin-bottom: 20px; font-size: 0.85rem; line-height: 1.4; }}
        
        /* LISTA DE PRODUTOS */
        .product-list {{ display: flex; flex-direction: column; gap: 12px; }}
        .product-item {{ display: flex; align-items: center; background: white; border: 1px solid #eee; border-radius: 12px; padding: 12px; gap: 15px; transition: 0.2s; position: relative; }}
        
        .prod-img-box {{ width: 80px; height: 80px; flex-shrink: 0; background: #fff; border-radius: 8px; overflow: hidden; border: 1px solid #f0f0f0; }}
        .prod-img-box img {{ width: 100%; height: 100%; object-fit: contain; }}
        
        .prod-info {{ flex-grow: 1; }}
        .prod-name {{ font-weight: 700; font-size: 1rem; color: #111; margin: 0; }}
        .prod-espec {{ font-size: 0.85rem; color: var(--primary); font-weight: 600; }}
        .prod-caract {{ font-size: 0.75rem; color: #777; line-height: 1.2; margin-top: 4px; font-style: italic; }}
        
        .prod-price-action {{ text-align: right; display: flex; flex-direction: column; gap: 8px; }}
        .prod-price {{ font-size: 1.1rem; font-weight: 800; color: #222; }}
        
        .btn-add {{ background: var(--primary); color: white; border: none; padding: 8px 15px; border-radius: 6px; font-weight: bold; cursor: pointer; font-size: 0.8rem; }}
        .btn-esgotado {{ background: #eee; color: #999; border: none; padding: 8px 15px; border-radius: 6px; font-weight: bold; cursor: not-allowed; font-size: 0.8rem; }}

        /* BARRA DO CARRINHO (ESTILO INDEX.HTML) */
        .cart-bar {{ position: fixed; bottom: 0; left: 0; right: 0; background: var(--primary); color: white; padding: 15px 20px; z-index: 1000; border-radius: 20px 20px 0 0; box-shadow: 0 -5px 20px rgba(0,0,0,0.15); }}
        .cart-content {{ max-width: 900px; margin: auto; display: flex; justify-content: space-between; align-items: center; }}
        
        /* MODAIS, CUPONS E LÓGICA IGUAL AO SEU INDEX... */
        .modal {{ display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.8); z-index:2000; overflow-y:auto; padding: 15px; box-sizing: border-box; }}
        .modal-content {{ background:white; max-width:500px; margin: 20px auto; padding: 25px; border-radius: 15px; color: #333; }}
        input, select {{ width:100%; padding:12px; margin: 8px 0; border: 1px solid #ddd; border-radius: 8px; box-sizing: border-box; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header-logo-container">
            <img src="https://github.com/glabpep/ordem/blob/main/1.png?raw=true" class="header-logo">
            <div class="subtitle">Research & Development Laboratorial</div>
        </div>

        <div class="info-alert-card">
            <i class="fas fa-microscope"></i> <b>AVISO:</b> Todos os produtos são enviados de forma <b>liofilizada (pó)</b>. Para reconstituição, utilize <b>Bacteriostatic Water</b>. Lote atual com validade estendida.
        </div>

        <div class="product-list" id="product-list"></div>
    </div>

    <div class="cart-bar" id="cart-bar" style="display:none;">
        <div class="cart-content">
            <div>
                <span id="cart-count" style="background:white; color:var(--primary); padding:3px 10px; border-radius:12px; font-weight:bold; margin-right:10px;">0</span>
                <span style="font-weight:bold; font-size:1.1rem;">R$ <span id="cart-total">0,00</span></span>
            </div>
            <button onclick="abrirCheckout()" style="background:var(--secondary); color:white; border:none; padding:12px 25px; border-radius:10px; font-weight:800; cursor:pointer; font-size:0.9rem;">CONCLUIR PEDIDO</button>
        </div>
    </div>

    <div id="modal-checkout" class="modal">
        <div class="modal-content">
            <h2 style="margin-top:0; color:var(--primary);">Finalizar Pedido</h2>
            <input type="text" id="f_nome" placeholder="Nome Completo">
            <input type="text" id="f_cep" placeholder="CEP (Apenas números)" onblur="validarCEP(this.value)">
            <input type="text" id="f_end" placeholder="Rua, Número e Bairro">
            <div style="display:flex; gap:10px;">
                <input type="text" id="f_cidade" placeholder="Cidade">
                <input type="text" id="f_uf" placeholder="UF" maxlength="2">
            </div>
            <input type="text" id="f_whats" placeholder="Seu WhatsApp">
            <input type="text" id="f_cupom" placeholder="CUPOM DE DESCONTO" oninput="calcularTotal()">
            <select id="f_pgto">
                <option value="Pix (5% Desconto)">Pix (5% Desconto)</option>
                <option value="Cartão de Crédito">Cartão de Crédito</option>
            </select>
            <div id="resumo-financeiro" style="background:#f9f9f9; padding:15px; border-radius:10px; margin:15px 0; font-size:0.9rem; line-height:1.6;"></div>
            <button onclick="enviarPedido()" style="width:100%; background:var(--secondary); color:white; border:none; padding:18px; border-radius:12px; font-weight:bold; cursor:pointer; font-size:1.1rem;">ENVIAR PARA WHATSAPP</button>
            <center><button onclick="fecharCheckout()" style="background:none; border:none; color:#999; margin-top:15px; cursor:pointer;">Continuar Comprando</button></center>
        </div>
    </div>

    <script>
        const DATA = {json_produtos};
        let carrinho = [];
        let freteValor = 0;

        function renderizarProdutos() {{
            const lista = document.getElementById('product-list');
            lista.innerHTML = DATA.map((p, i) => `
                <div class="product-item">
                    <div class="prod-img-box">
                        <img src="${{p.img}}" onerror="this.src='https://via.placeholder.com/100?text=LAB'">
                    </div>
                    <div class="prod-info">
                        <p class="prod-name">${{p.nome}}</p>
                        <p class="prod-espec">${{p.espec}}</p>
                        <p class="prod-caract">${{p.caracteristica}}</p>
                    </div>
                    <div class="prod-price-action">
                        <div class="prod-price">R$ ${{p.preco.toLocaleString('pt-BR', {{minimumFractionDigits: 2}})}}</div>
                        ${{ (p.estoque > 0 || p.status === 'DISPONÍVEL') 
                            ? `<button class="btn-add" onclick="adicionar(${{i}})">ADD</button>` 
                            : `<button class="btn-esgotado">OFF</button>`}}
                    </div>
                </div>
            `).join('');
        }}

        function adicionar(idx) {{
            carrinho.push(DATA[idx]);
            document.getElementById('cart-bar').style.display = 'block';
            calcularTotal();
        }}

        function calcularTotal() {{
            let subtotal = carrinho.reduce((acc, p) => acc + p.preco, 0);
            let cupom = document.getElementById('f_cupom').value.toUpperCase();
            let desc = 0;
            
            // Lógica de Cupons Original
            if(cupom === "CABRAL5" || cupom === "BRUNA5") desc = 0.05;
            if(cupom === "DAFNE10") desc = 0.10;
            
            let v_desc = subtotal * desc;
            let total = subtotal - v_desc + freteValor;

            document.getElementById('cart-count').innerText = carrinho.length;
            document.getElementById('cart-total').innerText = total.toLocaleString('pt-BR', {{minimumFractionDigits: 2}});
            
            const resumo = document.getElementById('resumo-financeiro');
            if(resumo) {{
                resumo.innerHTML = `
                    Subtotal: R$ ${{subtotal.toFixed(2)}}<br>
                    Desconto: R$ ${{v_desc.toFixed(2)}} (${{(desc*100)}}%)<br>
                    Frete: R$ ${{freteValor.toFixed(2)}}<br>
                    <b>Total Final: R$ ${{total.toFixed(2)}}</b>
                `;
            }}
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
                        
                        // Lógica de Frete Original
                        const sulSudeste = ['SP','RJ','MG','ES','PR','SC','RS'];
                        freteValor = sulSudeste.includes(d.uf) ? 90 : 165;
                        calcularTotal();
                    }}
                }} catch(e) {{}}
            }}
        }}

        function abrirCheckout() {{ document.getElementById('modal-checkout').style.display='block'; }}
        function fecharCheckout() {{ document.getElementById('modal-checkout').style.display='none'; }}

        function enviarPedido() {{
            const nome = document.getElementById('f_nome').value;
            if(!nome) return alert("Preencha o nome");
            
            let msg = "*NOVO PEDIDO G-LAB*%0A%0A";
            msg += "*Cliente:* " + nome.toUpperCase() + "%0A";
            msg += "*Itens:*%0A" + carrinho.map(p => "- " + p.nome).join("%0A");
            msg += "%0A%0A*Total:* R$ " + document.getElementById('cart-total').innerText;
            
            window.open("https://wa.me/17746222523?text=" + msg);
        }}

        renderizarProdutos();
    </script>
</body>
</html>
"""

# --- 6. NAVEGAÇÃO E ADMIN (STREAMLIT) ---
with st.sidebar:
    st.image("https://github.com/glabpep/ordem/blob/main/1.png?raw=true", width=150)
    st.write("---")
    menu = st.radio("NAVEGAÇÃO", ["🛒 SITE DE VENDAS", "🔐 ÁREA ADMINISTRATIVA"])

if menu == "🛒 SITE DE VENDAS":
    components.html(html_completo, height=2000, scrolling=True)
else:
    # A ÁREA ADMINISTRATIVA QUE VOCÊ PRECISA
    if not st.session_state.autenticado:
        st.subheader("Login Restrito")
        u = st.text_input("Usuário")
        p = st.text_input("Senha", type="password")
        if st.button("Acessar"):
            if u == "admin" and p == "glab2026":
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.error("Credenciais incorretas.")
    else:
        st.title("📦 Gestão de Estoque")
        st.dataframe(df_estoque, use_container_width=True, height=400)
        
        st.write("---")
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Dar Baixa/Atualizar")
            p_sel = st.selectbox("Produto", df_estoque['PRODUTO'].tolist())
            nova_qtd = st.number_input("Nova Quantidade em Estoque", min_value=0, value=10)
            if st.button("SALVAR ALTERAÇÃO"):
                idx = df_estoque[df_estoque['PRODUTO'] == p_sel].index[0]
                df_estoque.at[idx, 'QTD'] = nova_qtd
                salvar_estoque(df_estoque)
                st.success("Estoque atualizado!")
                st.rerun()
        
        with col2:
            st.subheader("Logout")
            if st.button("SAIR DO SISTEMA"):
                st.session_state.autenticado = False
                st.rerun()
