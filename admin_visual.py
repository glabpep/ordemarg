import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import os
import json

# --- 1. CONFIGURAÇÃO E ESTADO (MANTIDO DO ORIGINAL) ---
st.set_page_config(page_title="G-LAB PEPTIDES", layout="wide", page_icon="🧪")

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

# CSS para esconder elementos do Streamlit e forçar o estilo da loja
st.markdown("""
    <style>
        .block-container { padding: 0rem; }
        footer {visibility: hidden;}
        header {visibility: hidden;}
        [data-testid="stSidebar"] { background-color: #f8f9fa; border-right: 1px solid #ddd; }
    </style>
""", unsafe_allow_html=True)

# --- 2. GESTÃO DE DADOS (LÓGICA DO SEU ARQUIVO ORIGINAL) ---
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
            # Carrega e padroniza colunas conforme seu script original
            df = pd.read_excel(arquivo_dados)
            df.columns = [str(col).strip().upper() for col in df.columns]
            
            # Garante que as colunas críticas existam e sejam numéricas
            if 'QTD' in df.columns:
                df['QTD'] = pd.to_numeric(df['QTD'], errors='coerce').fillna(0).astype(int)
            
            # Preço pode estar como 'PREÇO (R$)' ou 'PREÇO'
            col_preco = 'PREÇO (R$)' if 'PREÇO (R$)' in df.columns else 'PREÇO'
            if col_preco in df.columns:
                df[col_preco] = pd.to_numeric(df[col_preco], errors='coerce').fillna(0)
                
            return df
        except Exception as e:
            st.error(f"Erro ao ler Excel: {e}")
    return pd.DataFrame(columns=['PRODUTO', 'VOLUME', 'MEDIDA', 'PREÇO', 'QTD'])

def salvar_estoque(df):
    df.to_excel("stock_0202 - NOVA.xlsx", index=False)

# --- 3. DICIONÁRIO TÉCNICO INTEGRAL (COPIADO DO SEU ORIGINAL) ---
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
    "NAD+": "Coenzima Vital: Fundamental para a função mitocondrial e reparo de DNA através das sirtuínas. Associado à longevidade, clareza mental e recuperação de energia celular."
}

# --- 4. FRONT-END (INTEGRAÇÃO DE IMAGENS + LÓGICA ORIGINAL) ---
def gerar_interface_vendas(df):
    col_preco = 'PREÇO (R$)' if 'PREÇO (R$)' in df.columns else 'PREÇO'
    produtos_json = []
    
    for _, row in df.iterrows():
        nome_original = str(row.get('PRODUTO', 'SEM NOME'))
        nome_prod_up = nome_original.strip().upper()
        
        # Busca info técnica (Lógica original)
        desc_tec = "Peptídeo de alta pureza para fins de pesquisa e desenvolvimento."
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
            body {{ font-family: 'Segoe UI', Tahoma, sans-serif; margin: 0; background: #f0f2f5; color: #333; }}
            .main-content {{ padding: 15px; max-width: 1200px; margin: 0 auto; padding-bottom: 220px; }}
            
            /* Grid de Itens em Cards */
            .grid-produtos {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 20px; margin-top: 20px; }}
            
            .card {{ background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.1); display: flex; flex-direction: column; position: relative; }}
            .img-box {{ width: 100%; height: 200px; background: #fff; border-bottom: 1px solid #eee; }}
            .img-box img {{ width: 100%; height: 100%; object-fit: contain; padding: 10px; box-sizing: border-box; }}
            
            .badge {{ position: absolute; top: 10px; right: 10px; padding: 5px 10px; border-radius: 20px; font-size: 10px; font-weight: bold; text-transform: uppercase; }}
            .bg-green {{ background: #e6fcf5; color: #0ca678; border: 1px solid #0ca678; }}
            .bg-red {{ background: #fff5f5; color: #fa5252; border: 1px solid #fa5252; }}
            
            .card-info {{ padding: 15px; flex-grow: 1; display: flex; flex-direction: column; }}
            .card-title {{ font-size: 16px; font-weight: bold; margin: 0; color: #004a99; }}
            .card-espec {{ font-size: 13px; color: #666; margin: 5px 0; font-weight: 600; }}
            .card-desc {{ font-size: 11px; color: #888; line-height: 1.4; margin-bottom: 15px; flex-grow: 1; }}
            .card-price {{ font-size: 20px; font-weight: 800; color: #333; margin-bottom: 15px; }}
            
            .btn-add {{ background: #004a99; color: white; border: none; padding: 12px; border-radius: 8px; font-weight: bold; cursor: pointer; width: 100%; }}
            .btn-off {{ background: #e9ecef; color: #adb5bd; border: none; padding: 12px; border-radius: 8px; width: 100%; cursor: not-allowed; }}

            /* Sidebar Carrinho Responsivo (Lógica Original) */
            .cart-sidebar {{ 
                width: 350px; background: #004a99; color: white; height: 100vh; position: fixed; right: 0; top: 0; 
                padding: 25px; box-sizing: border-box; display: flex; flex-direction: column; z-index: 999; 
            }}
            
            @media (max-width: 900px) {{
                .cart-sidebar {{ width: 100%; height: auto; top: auto; bottom: 0; padding: 15px; border-radius: 20px 20px 0 0; }}
                .cart-items {{ display: none; }}
                .main-content {{ padding-bottom: 180px; }}
            }}

            .cart-items {{ flex-grow: 1; overflow-y: auto; margin-bottom: 15px; }}
            .cart-item {{ display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid rgba(255,255,255,0.1); font-size: 13px; }}
            .total-area {{ background: rgba(0,0,0,0.2); padding: 15px; border-radius: 10px; }}
            .btn-checkout {{ background: white; color: #004a99; border: none; width: 100%; padding: 15px; border-radius: 10px; font-weight: 800; cursor: pointer; font-size: 16px; margin-top: 10px; }}

            /* Modal Original */
            #modalCheckout {{ display:none; position:fixed; z-index:1000; left:0; top:0; width:100%; height:100%; background:rgba(0,0,0,0.8); }}
            .modal-content {{ background:white; max-width: 450px; margin: 20px auto; padding: 25px; border-radius: 15px; color: #333; }}
            .modal-content input, select {{ width:100%; padding:12px; margin: 8px 0; border: 1px solid #ddd; border-radius: 8px; box-sizing: border-box; }}
        </style>
    </head>
    <body>
        <div class="main-content">
            <center><img src="https://github.com/glabpep/ordem/blob/main/1.png?raw=true" width="200"></center>
            <div style="background:#fff9c4; color:#856404; padding:15px; border-radius:8px; font-size:12px; border:1px solid #ffeeba; margin-top:20px;">
                <b>Aviso:</b> Produtos liofilizados. Use <b>Bacteriostatic Water</b>. Próximo lote: 09/03/2026.
            </div>
            <div class="grid-produtos" id="grid-produtos"></div>
        </div>

        <div class="cart-sidebar">
            <div style="font-size: 20px; font-weight: bold; border-bottom: 1px solid rgba(255,255,255,0.2); padding-bottom: 10px; margin-bottom: 15px;">
                <i class="fas fa-shopping-cart"></i> SEU PEDIDO (<span id="count">0</span>)
            </div>
            <div id="cart-items" class="cart-items"></div>
            <div class="total-area">
                <input type="text" id="cupom" oninput="atualizarTotais()" placeholder="CUPOM DE DESCONTO" style="width:100%; padding:8px; border-radius:5px; border:none; margin-bottom:10px;">
                <div style="display:flex; justify-content:space-between; font-size:18px; font-weight:800;">
                    <span>TOTAL:</span><span id="txt-total">R$ 0,00</span>
                </div>
                <button class="btn-checkout" onclick="abrirCheckout()">FINALIZAR COMPRA</button>
            </div>
        </div>

        <div id="modalCheckout">
            <div class="modal-content">
                <h2 style="margin-top:0; color:#004a99;">Entrega</h2>
                <input type="text" id="f_nome" placeholder="Nome Completo">
                <input type="text" id="f_cep" placeholder="CEP" onblur="buscarCEP(this.value)">
                <input type="text" id="f_end" placeholder="Rua, Número e Bairro">
                <div style="display:flex; gap:10px;">
                    <input type="text" id="f_cidade" placeholder="Cidade">
                    <input type="text" id="f_uf" placeholder="UF" maxlength="2">
                </div>
                <input type="text" id="f_whats" placeholder="WhatsApp">
                <select id="f_pgto">
                    <option value="Pix (5% Desconto)">Pix (5% Desconto)</option>
                    <option value="Cartão de Crédito">Cartão de Crédito</option>
                </select>
                <button onclick="finalizarNoWhats()" style="background:#28a745; color:white; border:none; width:100%; padding:18px; border-radius:10px; font-weight:bold; cursor:pointer; font-size:16px; margin-top:10px;">ENVIAR PARA WHATSAPP</button>
                <center><button onclick="fecharCheckout()" style="background:none; border:none; color:#999; margin-top:15px; cursor:pointer;">Voltar</button></center>
            </div>
        </div>

        <script>
            const PRODUTOS = {json_data};
            let carrinho = [];
            let freteV = 0;

            function renderizar() {{
                const grid = document.getElementById('grid-produtos');
                grid.innerHTML = PRODUTOS.map((p, i) => `
                    <div class="card">
                        <div class="img-box">
                            <img src="${{p.img}}" onerror="this.src='https://via.placeholder.com/300x200?text=PEPTIDE'">
                            <span class="badge ${{p.estoque > 0 ? 'bg-green' : 'bg-red'}}">
                                ${{p.estoque > 0 ? 'DISPONÍVEL' : 'EM ESPERA'}}
                            </span>
                        </div>
                        <div class="card-info">
                            <h3 class="card-title">${{p.nome}}</h3>
                            <div class="card-espec">${{p.espec}}</div>
                            <div class="card-desc">${{p.desc}}</div>
                            <div class="card-price">R$ ${{p.preco.toLocaleString('pt-BR', {{minimumFractionDigits: 2}})}}</div>
                            ${{p.estoque > 0 
                                ? `<button class="btn-add" onclick="addCarrinho(${{i}})">ADICIONAR</button>` 
                                : `<button class="btn-off">ESGOTADO</button>`}}
                        </div>
                    </div>
                `).join('');
            }}

            function addCarrinho(idx) {{
                carrinho.push(PRODUTOS[idx]);
                atualizarTotais();
            }}

            function remover(idx) {{
                carrinho.splice(idx, 1);
                atualizarTotais();
            }}

            function atualizarTotais() {{
                const lista = document.getElementById('cart-items');
                const badge = document.getElementById('count');
                badge.innerText = carrinho.length;
                
                if(carrinho.length === 0) {{
                    lista.innerHTML = '<p style="text-align:center; opacity:0.5; font-size:12px;">Vazio</p>';
                    document.getElementById('txt-total').innerText = "R$ 0,00";
                    return;
                }}

                lista.innerHTML = carrinho.map((p, i) => `
                    <div class="cart-item">
                        <span>${{p.nome}}</span>
                        <span>R$ ${{p.preco.toFixed(2)}} <i class="fas fa-trash" onclick="remover(${{i}})" style="color:#ff6b6b; cursor:pointer; margin-left:8px;"></i></span>
                    </div>
                `).join('');

                // Lógica de Cupons Original
                let sub = carrinho.reduce((acc, p) => acc + p.preco, 0);
                let cupom = document.getElementById('cupom').value.toUpperCase();
                let desc = 0;
                if(cupom === "CABRAL5" || cupom === "BRUNA5") desc = 0.05;
                if(cupom === "DAFNE10") desc = 0.10;

                let total = (sub * (1 - desc)) + freteV;
                document.getElementById('txt-total').innerText = "R$ " + total.toLocaleString('pt-BR', {{minimumFractionDigits: 2}});
            }}

            async function buscarCEP(cep) {{
                cep = cep.replace(/\D/g, '');
                if(cep.length === 8) {{
                    const r = await fetch(\`https://viacep.com.br/ws/${{cep}}/json/\`);
                    const d = await r.json();
                    if(!d.erro) {{
                        document.getElementById('f_cidade').value = d.localidade;
                        document.getElementById('f_uf').value = d.uf;
                        document.getElementById('f_end').value = d.logradouro + " - " + d.bairro;
                        
                        // Lógica de Frete Original
                        const sul_sudeste = ['SP','RJ','MG','ES','PR','SC','RS'];
                        freteV = sul_sudeste.includes(d.uf) ? 90 : 165;
                        atualizarTotais();
                    }}
                }}
            }}

            function abrirCheckout() {{ if(carrinho.length > 0) document.getElementById('modalCheckout').style.display='block'; }}
            function fecharCheckout() {{ document.getElementById('modalCheckout').style.display='none'; }}

            function finalizarNoWhats() {{
                const nome = document.getElementById('f_nome').value;
                if(!nome) return alert("Preencha o nome");
                
                // Lógica de Brinde (Cupom Bruna) original
                let cupom = document.getElementById('cupom').value.toUpperCase();
                let temBrinde = (cupom === "BRUNA5");
                
                let msg = "*NOVO PEDIDO G-LAB*%0A%0A";
                msg += "*Cliente:* " + nome.toUpperCase() + "%0A";
                msg += "*Itens:*%0A" + carrinho.map(p => "- " + p.nome).join("%0A");
                if(temBrinde) msg += "*BRINDE:* Bacteriostatic Water 7ml%0A";
                msg += "%0A*TOTAL:* " + document.getElementById('txt-total').innerText;
                
                window.open("https://wa.me/17746222523?text=" + msg);
            }}

            renderizar();
        </script>
    </body>
    </html>
    """
    return html_code

# --- 5. LOGICA DO SISTEMA (MANTIDO 100% DO ORIGINAL) ---
df_estoque = carregar_estoque()

with st.sidebar:
    st.image("https://github.com/glabpep/ordem/blob/main/1.png?raw=true", width=150)
    st.write("---")
    menu = st.radio("NAVEGAÇÃO", ["🛒 SITE DE VENDAS", "🔐 ADMINISTRAÇÃO"])

if menu == "🛒 SITE DE VENDAS":
    # Passa o DataFrame completo para o componente
    components.html(gerar_interface_vendas(df_estoque), height=1500, scrolling=True)

else:
    # Lógica Administrativa Original
    if not st.session_state.autenticado:
        st.subheader("Login Admin")
        u = st.text_input("Usuário")
        p = st.text_input("Senha", type="password")
        if st.button("Acessar"):
            if u == "admin" and p == "glab2026":
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.error("Erro")
    else:
        st.title("📦 GESTÃO")
        st.dataframe(df_estoque, use_container_width=True)
        
        st.write("---")
        st.subheader("Baixa Manual")
        p_sel = st.selectbox("Produto", df_estoque['PRODUTO'].tolist())
        q_venda = st.number_input("Qtd", min_value=1, value=1)
        
        if st.button("DAR BAIXA"):
            idx = df_estoque[df_estoque['PRODUTO'] == p_sel].index[0]
            if df_estoque.at[idx, 'QTD'] >= q_venda:
                df_estoque.at[idx, 'QTD'] -= q_venda
                salvar_estoque(df_estoque)
                st.success("Atualizado!")
                st.rerun()
            else:
                st.error("Sem estoque!")
