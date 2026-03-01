import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import os
import json

# --- 1. CONFIGURAÇÃO DE PÁGINA (STREAMLIT) ---
st.set_page_config(page_title="G-LAB PEPTIDES", layout="wide", page_icon="🧪")

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

# Esconde elementos do Streamlit para o site ser o protagonista
st.markdown("""
    <style>
        .block-container { padding: 0rem; }
        footer {visibility: hidden;}
        header {visibility: hidden;}
        [data-testid="stSidebar"] { background-color: #f8f9fa; border-right: 1px solid #ddd; }
        @media (max-width: 640px) { .block-container { padding: 0rem; } }
    </style>
""", unsafe_allow_html=True)

# --- 2. LOGICA DE DADOS (EXCEL) ---
def carregar_dados():
    diretorio = os.path.dirname(os.path.abspath(__file__))
    # Tenta encontrar o arquivo enviado
    for nome in ['stock_0202 - NOVA.xlsx', 'stock_2901.xlsx']:
        caminho = os.path.join(diretorio, nome)
        if os.path.exists(caminho):
            try:
                df = pd.read_excel(caminho)
                df.columns = [str(col).strip().upper() for col in df.columns]
                # Previne erro de tipos
                if 'QTD' in df.columns:
                    df['QTD'] = pd.to_numeric(df['QTD'], errors='coerce').fillna(0).astype(int)
                col_p = 'PREÇO (R$)' if 'PREÇO (R$)' in df.columns else 'PREÇO'
                if col_p in df.columns:
                    df[col_p] = pd.to_numeric(df[col_p], errors='coerce').fillna(0)
                return df, col_p
            except:
                continue
    return pd.DataFrame(), ""

def salvar_dados(df):
    df.to_excel("stock_0202 - NOVA.xlsx", index=False)

# --- 3. DICIONÁRIO TÉCNICO INTEGRAL ---
INFOS_TECNICAS = {
    "5-AMINO": "Inibidor Seletivo de NNMT: Atua bloqueando a enzima nicotinamida N-metiltransferase, o que eleva os níveis de NAD+ e SAM intracelular. Indica eficácia na reversão da obesidade.",
    "AICAR": "Ativador de AMPK: Mimetiza o AMP intracelular para ativar a proteína quinase. Aumenta a oxidação de ácidos graxos e a resistência cardiovascular.",
    "AOD 9604": "Análogo Lipolítico do hGH: Focado na queima de gordura sem induzir efeitos hiperglicêmicos. Promove a lipólise e inibe a lipogênese.",
    "BPC-157": "Peptídeo Regenerativo: Composto derivado do suco gástrico. Demonstra alta eficácia na cicatrização de tendões, ligamentos e tecidos musculares.",
    "CJC-1295": "Análogo de GHRH: Estimula a glândula pituitária a liberar o hormônio do crescimento (GH).",
    "GHK-CU": "Peptídeo de Cobre: Atua na síntese de colágeno e elastina. Possui propriedades anti-inflamatórias potentes.",
    "IPAMORELIN": "Agonista Seletivo de Grelina: Estimula a liberação de GH sem elevar significativamente o cortisol ou prolactina.",
    "MELANOTAN 2": "Análogo de MSH: Estimula a produção de melanina (bronzeamento) e atua nos receptores associados à libido.",
    "TESAMORELIN": "Peptídeo GHRH: Eficaz na redução de gordura visceral abdominal. Melhora o perfil lipídico.",
    "TB-500": "Timosina Beta-4: Crucial para o reparo celular e angiogênese, acelerando a recuperação de lesões.",
    "MK-677": "Secretagogo de GH Oral: Aumenta os níveis de IGF-1 e GH de forma sustentada.",
    "NAD+": "Coenzima Vital: Fundamental para a função mitocondrial e reparo de DNA."
}

# --- 4. CONSTRUÇÃO DO SITE (HTML INTEGRAL) ---
df, col_preco = carregar_dados()
produtos_json = []

if not df.empty:
    for _, row in df.iterrows():
        nome_original = str(row.get('PRODUTO', ''))
        nome_up = nome_original.strip().upper()
        
        # Seleciona a info técnica
        caract = "Peptídeo de alta pureza para fins de pesquisa e desenvolvimento."
        for k, v in INFOS_TECNICAS.items():
            if k in nome_up:
                caract = v
                break
        
        produtos_json.append({
            "nome": nome_original,
            "espec": f"{row.get('VOLUME', '')} {row.get('MEDIDA', '')}",
            "preco": float(row.get(col_preco, 0)),
            "status": str(row.get('ESTOQUE', 'EM ESPERA')).upper(),
            "qtd": int(row.get('QTD', 0)),
            "caract": caract,
            "img": f"https://raw.githubusercontent.com/glabpep/ordem/main/{nome_up.replace(' ', '%20')}.webp"
        })

# SEU HTML ORIGINAL ADAPTADO APENAS PARA RECEBER OS DADOS
html_content = f"""
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>G-LAB PEPTIDES</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        :root {{ --primary: #004a99; --secondary: #28a745; --danger: #dc3545; --bg: #f4f7f9; }}
        body {{ font-family: 'Segoe UI', Roboto, sans-serif; background: var(--bg); margin: 0; padding: 0; color: #333; -webkit-font-smoothing: antialiased; }}
        .container {{ max-width: 900px; margin: auto; background: white; min-height: 100vh; padding: 15px; box-sizing: border-box; padding-bottom: 220px; position: relative; }}
        
        /* HEADER E RESPONSIVIDADE */
        .header-logo-container {{ text-align: center; padding: 20px 0; }}
        .header-logo {{ max-width: 250px; width: 100%; height: auto; }}
        
        .product-list {{ display: flex; flex-direction: column; gap: 15px; margin-top: 20px; }}
        
        /* CARD IDENTICO AO SEU DESIGN */
        .product-card {{ display: flex; align-items: center; background: white; border: 1px solid #eee; border-radius: 12px; padding: 15px; gap: 15px; transition: 0.2s; box-shadow: 0 2px 5px rgba(0,0,0,0.02); }}
        .prod-img-box {{ width: 90px; height: 90px; flex-shrink: 0; border: 1px solid #f5f5f5; border-radius: 10px; padding: 5px; box-sizing: border-box; }}
        .prod-img-box img {{ width: 100%; height: 100%; object-fit: contain; }}
        
        .prod-info {{ flex-grow: 1; }}
        .prod-name {{ font-weight: 800; font-size: 1.1rem; color: #111; margin: 0; text-transform: uppercase; }}
        .prod-espec {{ font-size: 0.9rem; color: var(--primary); font-weight: 700; margin-top: 2px; }}
        .prod-desc {{ font-size: 0.75rem; color: #777; line-height: 1.3; margin-top: 6px; font-style: italic; }}
        
        .prod-action {{ text-align: right; min-width: 100px; }}
        .prod-price {{ font-size: 1.2rem; font-weight: 900; color: #111; margin-bottom: 8px; }}
        
        .btn-add {{ background: var(--primary); color: white; border: none; padding: 10px 20px; border-radius: 8px; font-weight: bold; cursor: pointer; width: 100%; font-size: 0.85rem; }}
        .btn-off {{ background: #f0f0f0; color: #aaa; border: none; padding: 10px 20px; border-radius: 8px; font-weight: bold; cursor: not-allowed; width: 100%; font-size: 0.85rem; }}

        /* BARRA DO CARRINHO MOBILE-FIRST */
        .cart-bar {{ position: fixed; bottom: 0; left: 0; right: 0; background: var(--primary); color: white; padding: 20px; z-index: 1000; border-radius: 25px 25px 0 0; box-shadow: 0 -5px 25px rgba(0,0,0,0.2); }}
        .cart-inner {{ max-width: 900px; margin: auto; display: flex; justify-content: space-between; align-items: center; }}
        
        /* MODAL DE CHECKOUT */
        #modal-checkout {{ display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.85); z-index:9999; overflow-y:auto; }}
        .modal-content {{ background:white; width: 95%; max-width:500px; margin: 20px auto; padding: 25px; border-radius: 20px; box-sizing: border-box; }}
        input, select {{ width: 100%; padding: 14px; margin: 8px 0; border: 1px solid #ddd; border-radius: 10px; font-size: 16px; box-sizing: border-box; }}

        @media (max-width: 600px) {{
            .product-card {{ padding: 10px; gap: 10px; }}
            .prod-img-box {{ width: 70px; height: 70px; }}
            .prod-name {{ font-size: 0.95rem; }}
            .prod-price {{ font-size: 1rem; }}
            .btn-add {{ padding: 8px 12px; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header-logo-container">
            <img src="https://github.com/glabpep/ordem/blob/main/1.png?raw=true" class="header-logo">
        </div>

        <div id="main-list" class="product-list">
            </div>
    </div>

    <div class="cart-bar" id="cart-bar" style="display:none;">
        <div class="cart-inner">
            <div>
                <span id="c-count" style="background:white; color:var(--primary); padding:3px 12px; border-radius:15px; font-weight:bold; margin-right:10px;">0</span>
                <span style="font-weight:bold; font-size:1.2rem;">Total: R$ <span id="c-total">0,00</span></span>
            </div>
            <button onclick="document.getElementById('modal-checkout').style.display='block'" style="background:var(--secondary); color:white; border:none; padding:12px 25px; border-radius:12px; font-weight:bold; cursor:pointer;">FINALIZAR</button>
        </div>
    </div>

    <div id="modal-checkout">
        <div class="modal-content">
            <h2 style="margin:0 0 20px 0; color:var(--primary);">Finalizar Envio</h2>
            <input type="text" id="f_nome" placeholder="Nome Completo">
            <input type="text" id="f_cep" placeholder="CEP" onblur="cotarFrete(this.value)">
            <input type="text" id="f_end" placeholder="Rua, Número e Bairro">
            <input type="text" id="f_cupom" placeholder="CUPOM DE DESCONTO" oninput="atualizar()">
            <div id="resumo-financeiro" style="padding:15px; background:#f9f9f9; border-radius:12px; margin:15px 0; font-size:0.9rem;"></div>
            <button onclick="gerarWhatsApp()" style="width:100%; background:var(--secondary); color:white; border:none; padding:20px; border-radius:15px; font-weight:bold; font-size:1.1rem; cursor:pointer;">CONCLUIR NO WHATSAPP</button>
            <center><button onclick="document.getElementById('modal-checkout').style.display='none'" style="background:none; border:none; color:#999; margin-top:20px; cursor:pointer; font-size:1rem;">Voltar</button></center>
        </div>
    </div>

    <script>
        const PRODUTOS = {json.dumps(produtos_json)};
        let carrinho = [];
        let freteGlobal = 0;

        function render() {{
            const list = document.getElementById('main-list');
            list.innerHTML = PRODUTOS.map((p, i) => `
                <div class="product-card">
                    <div class="prod-img-box">
                        <img src="${{p.img}}" onerror="this.src='https://via.placeholder.com/100?text=LAB'">
                    </div>
                    <div class="prod-info">
                        <p class="prod-name">${{p.nome}}</p>
                        <p class="prod-espec">${{p.espec}}</p>
                        <p class="prod-desc">${{p.caract}}</p>
                    </div>
                    <div class="prod-action">
                        <div class="prod-price">R$ ${{p.preco.toLocaleString('pt-BR', {{minimumFractionDigits: 2}})}}</div>
                        ${{ (p.qtd > 0 || p.status === 'DISPONÍVEL') 
                            ? `<button class="btn-add" onclick="add(${{i}})">ADD</button>` 
                            : `<button class="btn-off">OFF</button>`}}
                    </div>
                </div>
            `).join('');
        }}

        function add(idx) {{
            carrinho.push(PRODUTOS[idx]);
            document.getElementById('cart-bar').style.display = 'block';
            atualizar();
        }}

        function atualizar() {{
            let sub = carrinho.reduce((acc, p) => acc + p.preco, 0);
            let cupom = document.getElementById('f_cupom').value.toUpperCase();
            let desc = (cupom === "CABRAL5" || cupom === "BRUNA5") ? 0.05 : (cupom === "DAFNE10" ? 0.10 : 0);
            
            let total = (sub * (1 - desc)) + freteGlobal;
            
            document.getElementById('c-count').innerText = carrinho.length;
            document.getElementById('c-total').innerText = total.toLocaleString('pt-BR', {{minimumFractionDigits: 2}});
            
            const resumo = document.getElementById('resumo-financeiro');
            if(resumo) {{
                resumo.innerHTML = `Subtotal: R$ ${{sub.toFixed(2)}}<br>Frete: R$ ${{freteGlobal.toFixed(2)}}<br>Desconto: ${{desc*100}}%`;
            }}
        }}

        async function cotarFrete(cep) {{
            const c = cep.replace(/\D/g, '');
            if(c.length === 8) {{
                const r = await fetch(\`https://viacep.com.br/ws/${{c}}/json/\`);
                const d = await r.json();
                if(!d.erro) {{
                    document.getElementById('f_end').value = d.logradouro + ", " + d.bairro;
                    const sulSudeste = ['SP','RJ','MG','ES','PR','SC','RS'];
                    freteGlobal = sulSudeste.includes(d.uf) ? 90 : 165;
                    atualizar();
                }}
            }}
        }}

        function gerarWhatsApp() {{
            const nome = document.getElementById('f_nome').value;
            let msg = "*PEDIDO G-LAB*%0A%0A*Cliente:* " + nome.toUpperCase() + "%0A*Itens:*%0A";
            carrinho.forEach(i => msg += "- " + i.nome + " (" + i.espec + ")%0A");
            msg += "%0A*Total c/ Frete:* R$ " + document.getElementById('c-total').innerText;
            window.open("https://wa.me/17746222523?text=" + msg);
        }}

        render();
    </script>
</body>
</html>
"""

# --- 5. INTERFACE DO USUÁRIO E ADMIN (NAVEGAÇÃO) ---
with st.sidebar:
    st.image("https://github.com/glabpep/ordem/blob/main/1.png?raw=true", width=150)
    st.write("---")
    # Menu simplificado para não poluir
    aba = st.radio("NAVEGAÇÃO", ["🛒 LOJA DE VENDAS", "🔐 ÁREA DO ADMINISTRADOR"])

if aba == "🛒 LOJA DE VENDAS":
    components.html(html_content, height=2000, scrolling=True)

else:
    # SISTEMA ADMINISTRATIVO PROTEGIDO
    if not st.session_state.autenticado:
        st.title("Acesso Restrito")
        u = st.text_input("Usuário")
        p = st.text_input("Senha", type="password")
        if st.button("ENTRAR"):
            if u == "admin" and p == "glab2026":
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.error("Credenciais inválidas.")
    else:
        st.title("🛠 Painel de Controle de Estoque")
        st.write("Edite as quantidades abaixo e clique em Salvar.")
        
        # Tabela editável (Funcionalidade Admin)
        if not df.empty:
            df_editado = st.data_editor(df, use_container_width=True, hide_index=True)
            
            if st.button("💾 SALVAR ALTERAÇÕES NO EXCEL"):
                salvar_dados(df_editado)
                st.success("Estoque atualizado com sucesso!")
                st.rerun()
        
        if st.sidebar.button("SAIR"):
            st.session_state.autenticado = False
            st.rerun()
