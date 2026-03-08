import pandas as pd
import os
import json

def gerar_site_vendas_completo():
    diretorio_atual = os.path.dirname(os.path.abspath(__file__))
    
    # URL BASE DO SEU REPOSITÓRIO (Ajustada para o seu repo 'glabpep')
    # O '%20' é necessário porque sua pasta tem espaço: 'imagens produtos'
    URL_RAW_GITHUB = "https://raw.githubusercontent.com/glabpep/ordemarg/main/imagens%20produtos/"

    # Busca o arquivo de dados
    arquivo_dados = None
    for nome in ['stock_0202 - NOVA.xlsx', 'stock_2901.xlsx - Plan1.csv']:
        caminho = os.path.join(diretorio_atual, nome)
        if os.path.exists(caminho):
            arquivo_dados = caminho
            break

    if not arquivo_dados:
        print(f"Erro: Arquivo não encontrado em: {diretorio_atual}")
        return

    # Dicionário de informações técnicas integral
    infos_tecnicas = {
        "5-AMINO": "Inhibidor selectivo de NNMT: Actúa bloqueando la enzima nicotinamida N-metiltransferasa, lo que eleva los niveles intracelulares de NAD+ y SAM. Estudios indican eficacia en la reversión de la obesidad y optimización del gasto energético basal.",
        "AICAR": "Activador de AMPK: Imita el AMP intracelular para activar la proteína quinasa. Investigado por aumentar la captación de glucosa muscular, la oxidación de ácidos grasos y la resistencia cardiovascular.",
        "AOD 9604": "Análogo lipolítico de hGH: Diseñado para aislar las propiedades de quema de grasa de la hormona del crecimiento sin inducir efectos hiperglucémicos. Aplicado en estudios de obesidad y regeneración de cartílago.",
        "HGH FRAGMENT": "Modulador lipídico: Fragmento terminal de la hormona del crecimiento responsable de la lipólisis. Puede inhibir la formación de nueva grasa y acelerar la lipólisis visceral sin alterar la insulina.",
        "L-CARNITINE": "Cofactor de transporte mitocondrial: Esencial para transportar ácidos grasos hacia la matriz mitocondrial (β-oxidación). Reduce la fatiga muscular y favorece el rendimiento atlético.",
        "MOTS-C": "Péptido derivado de la mitocondria: Regulador hormonal del metabolismo sistémico. Mejora la homeostasis de la glucosa y combate la resistencia a la insulina mediante la activación de la vía AMPK.",
        "SLU PP": "Agonista Pan-ERR (la 'píldora del ejercicio'): Activa los receptores ERRα, β y γ. Aumenta significativamente la biogénesis mitocondrial y la resistencia física.",
        "LIPO C": "Mezcla lipotrópica inyectable: Compuesta por metionina, inositol y colina. Favorece la exportación de grasas del hígado y optimiza la movilización lipídica.",
        "CJC-1295": "Secretagogo de GH de larga duración: Análogo de GHRH que aumenta la secreción de GH e IGF-1. Investigado en antienvejecimiento y mejora de la composición corporal.",
        "IPAMORELIN": "Agonista selectivo de grelina: Estimula la liberación pulsátil de GH sin elevar cortisol ni prolactina.",
        "CJC-1295 + IPAMORELIN": "Sinergia hormonal dual: Combinación de GHRH con GHRP que imita la liberación fisiológica natural de la hormona del crecimiento.",
        "GHRP-6": "Péptido liberador de GH: Estimula la hipófisis y aumenta la señalización del apetito mediante la grelina.",
        "HEXARELIN": "Secretagogo potente de GH perteneciente a la familia GHRP. Puede aumentar la fuerza contráctil cardíaca y muscular.",
        "IGF-1 LR3": "Análogo de IGF-1 de larga vida media que permanece activo hasta 20 horas. Mediador importante de la hiperplasia muscular.",
        "IGF DES": "Variante de IGF-1 de acción local con afinidad elevada por los receptores.",
        "SERMORELIN": "Estimula el eje natural de hormona de crecimiento imitando el GHRH.",
        "MK-677": "Secretagogo oral (Ibutamoren) que actúa como agonista del receptor de grelina aumentando GH e IGF-1.",
        "BPC-157": "Pentadecapéptido gástrico investigado por acelerar la angiogénesis y cicatrización.",
        "BPC-157 ORAL": "Versión oral estable en jugo gástrico enfocada en la protección gastrointestinal.",
        "TB-500": "Timosina Beta-4 sintética involucrada en migración celular y reparación de tejidos.",
        "TB-500 + BPC": "Protocolo combinado de regeneración que une TB-500 con BPC-157.",
        "GHK-CU": "Complejo péptido-cobre que estimula síntesis de colágeno y regeneración tisular.",
        "GLOW": "Bioestimulación dérmica (GHK-Cu + BPC + TB) orientada a regeneración cutánea.",
        "ARA 290": "Derivado de eritropoyetina investigado para regeneración nerviosa y dolor neuropático.",
        "KPV": "Tripéptido antiinflamatorio que inhibe vías inflamatorias como NF-κB.",
        "LL-37": "Péptido antimicrobiano del sistema inmune innato.",
        "KLOW": "Combinación de GHK + BPC + TB + KPV diseñada para señalización regenerativa profunda.",
        "TIRZEPATIDE": "Agonista dual GIP/GLP-1 que promueve saciedad y mejora sensibilidad a la insulina.",
        "RETATRUTIDE": "Agonista triple GIP/GLP-1/GCGR que aumenta el gasto energético.",
        "SEMAGLUTIDE": "Agonista de GLP-1 que retrasa el vaciamiento gástrico y aumenta la saciedad.",
        "SELANK": "Péptido ansiolítico que modula serotonina y norepinefrina.",
        "SEMAX": "Nootrópico neuroprotector que aumenta niveles de BDNF y NGF.",
        "PINEALON": "Bioregulador de cadena corta que actúa sobre la expresión génica neuronal.",
        "NAD+": "Coenzima esencial para metabolismo energético y reparación del ADN.",
        "METHYLENE BLUE": "Optimización mitocondrial mediante transporte alternativo de electrones.",
        "DSIP": "Péptido modulador del sueño profundo.",
        "OXYTOCIN": "Neuromodulador asociado a vínculos sociales y reducción del estrés.",
        "EPITHALON": "Péptido asociado a activación de telomerasa y longevidad celular.",
        "KISSPEPTIN": "Regulador del eje hipotálamo-hipófisis-gonadal.",
        "MELANOTAN 1": "Agonista de melanocortina que estimula la producción de melanina.",
        "MELANOTAN 2": "Estimula pigmentación cutánea y puede aumentar libido.",
        "PT-141": "Péptido utilizado para tratar disfunción sexual actuando en el sistema nervioso central.",
        "VITAMIN B-12": "Metilcobalamina esencial para formación de glóbulos rojos y función neurológica.",
        "BACTERIOSTATIC WATER": "Agua bacteriostática con 0,9% de alcohol bencílico que previene proliferación bacteriana.",
        "SS-31": "Péptido protector mitocondrial que preserva la cardiolipina.",
        "HYALURONIC ACID 2% + GHK": "Combinación de ácido hialurónico con péptido GHK para hidratación y regeneración tisular.",
        "HCG": "Hormona que imita la acción de LH estimulando producción de testosterona.",
        "HEMP OIL": "Aceite derivado del cáñamo con propiedades antiinflamatorias.",
        "TESAMORELIN": "Análogo de GHRH aprobado para reducción de grasa visceral."
    }
    try:
        if arquivo_dados.endswith('.xlsx'):
            df = pd.read_excel(arquivo_dados)
        else:
            df = pd.read_csv(arquivo_dados)
        df.columns = [str(col).strip() for col in df.columns]
        
        produtos_base = []
        for idx, row in df.iterrows():
            nome_prod = str(row.get('PRODUTO', 'N/A')).strip()
            info_prod = "Informação técnica detalhada não disponível para este item."
            for chave, texto in infos_tecnicas.items():
                if chave in nome_prod.upper():
                    info_prod = texto
                    break

            produtos_base.append({
                "id": idx,
                "nome": nome_prod,
                "espec": f"{row.get('VOLUME', '')} {row.get('MEDIDA', '')}".strip(),
                "preco": float(row.get('Preço (U$)', 0)),
                "info": info_prod
            })
        js_produtos = json.dumps(produtos_base)
        
    except Exception as e:
        print(f"Erro ao ler os dados: {e}")
        return

    html_template = f"""
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <title>G-LAB PEPTIDES - Pedidos</title>
        <style>
            :root {{ --primary: #004a99; --secondary: #28a745; --danger: #dc3545; --bg: #f4f7f9; }}
            body {{ font-family: 'Segoe UI', Roboto, sans-serif; background: var(--bg); margin: 0; padding: 0; color: #333; }}
            .container {{ max-width: 900px; margin: auto; background: white; min-height: 100vh; padding: 15px; box-sizing: border-box; padding-bottom: 220px; }}
            .header-logo-container {{ text-align: center; padding: 10px 0; }}
            .header-logo {{ max-width: 250px; height: auto; }}
            .subtitle {{ text-align: center; color: #666; font-size: 0.9rem; margin-bottom: 20px; font-weight: 500; }}
            .info-alert-card {{ background: #fff3cd; border: 1px solid #ffeeba; color: #856404; padding: 15px; border-radius: 12px; margin-bottom: 10px; position: relative; font-size: 0.9rem; line-height: 1.4; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }}
            .lote-alert-card {{ background: #e3f2fd; border: 1px solid #bbdefb; color: #0d47a1; padding: 15px; border-radius: 12px; margin-bottom: 20px; font-size: 0.9rem; line-height: 1.4; font-weight: bold; border-left: 5px solid #2196f3; }}
            .close-alert {{ position: absolute; top: 10px; right: 10px; cursor: pointer; font-weight: bold; font-size: 1.2rem; }}
            .frete-card {{ background: #fff; border: 2px solid var(--primary); padding: 15px; border-radius: 12px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
            .table-container {{ overflow-x: auto; border-radius: 8px; border: 1px solid #eee; }}
            table {{ width: 100%; border-collapse: collapse; background: white; min-width: 400px; }}
            th {{ background: var(--primary); color: white; padding: 12px 8px; text-align: left; font-size: 0.85rem; }}
            td {{ padding: 12px 8px; border-bottom: 1px solid #f0f0f0; font-size: 0.9rem; }}
            .status-disponivel {{ color: var(--secondary); font-weight: bold; }}
            .status-espera {{ color: var(--danger); font-weight: bold; background: #fff5f5; padding: 4px 8px; border-radius: 4px; border: 1px solid var(--danger); display: inline-block; }}
            .input-style {{ padding: 12px; border: 1px solid #ccc; border-radius: 8px; width: 100%; box-sizing: border-box; font-size: 16px; }}
            .btn-add {{ background: var(--secondary); color: white; border: none; padding: 10px; border-radius: 8px; cursor: pointer; font-weight: bold; width: 100%; }}
            .btn-add:disabled {{ background: #eee; color: #999; cursor: not-allowed; }}
            .btn-info {{ background: none; border: none; color: var(--primary); font-size: 0.75rem; text-decoration: underline; cursor: pointer; padding: 0; margin-top: 5px; font-weight: bold; }}
            
            /* CARRINHO FIXO E SEMPRE VISÍVEL */
            .cart-panel {{ 
                position: fixed; 
                bottom: 20px; 
                right: 20px; 
                background: var(--primary); 
                color: white; 
                padding: 15px; 
                border-radius: 15px; 
                z-index: 1000; 
                display: none; 
                box-shadow: 0 5px 20px rgba(0,0,0,0.3); 
                width: 350px; 
                max-height: 80vh; 
                overflow-y: auto; 
            }}
            /* MODAL FIXO NO CENTRO DA TELA */
            .modal {{ 
                display: none; 
                position: fixed; 
                z-index: 2000; 
                left: 0; 
                top: 0; 
                width: 100%; 
                height: 100%; 
                background: rgba(0,0,0,0.8); 
                backdrop-filter: blur(3px); /* Efeito de desfoque no fundo */
            }}
            .modal-content {{ 
                background: white; 
                position: fixed; /* Fixa em relação à tela, não à página */
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%); /* Centraliza exatamente no meio */
                padding: 20px; 
                width: 90%; 
                max-width: 500px; 
                max-height: 90vh; /* Garante que o card caiba em telas pequenas */
                border-radius: 15px; 
                box-sizing: border-box; 
                overflow-y: auto; /* Permite rolar apenas dentro do card se ele for grande */
                box-shadow: 0 10px 40px rgba(0,0,0,0.5);
            }}
            /* Ajuste para Celulares */
            @media (max-width: 600px) {{
                .cart-panel {{
                    width: 90% !important;
                    left: 5% !important;
                    right: 5% !important;
                    bottom: 10px !important;
                }}
                .modal-content {{
                    width: 95% !important;
                    padding: 15px !important;
                }}
            }}
            .cart-list {{ margin: 10px 0; max-height: 150px; overflow-y: auto; background: rgba(255,255,255,0.1); border-radius: 8px; padding: 5px; }}
            .cart-item {{ display: flex; justify-content: space-between; padding: 8px; border-bottom: 1px solid rgba(255,255,255,0.1); font-size: 0.85rem; align-items: center; }}
            .btn-remove {{ background: #ff4444; border: none; color: white; cursor: pointer; font-weight: bold; border-radius: 4px; padding: 2px 8px; margin-left: 10px; }}
            .coupon-section {{ display: flex; gap: 5px; margin: 10px 0; }}
            .coupon-input {{ flex: 1; padding: 8px; border-radius: 5px; border: none; font-size: 0.8rem; color: #333; }}
            .btn-coupon {{ background: #ffeb3b; color: #333; border: none; padding: 8px 12px; border-radius: 5px; font-weight: bold; cursor: pointer; font-size: 0.8rem; }}
            .ship-row {{ display: flex; justify-content: space-between; align-items: center; font-size: 0.85rem; color: #ffeb3b; margin-top: 5px; font-weight: bold; }}
            .total-row {{ display: flex; justify-content: space-between; font-size: 1.1rem; font-weight: bold; margin: 5px 0; border-top: 1px solid rgba(255,255,255,0.2); padding-top: 10px; }}
            .discount-line {{ display: none; justify-content: space-between; color: #ffeb3b; font-size: 0.9rem; margin-bottom: 5px; }}
            .btn-checkout-final {{ background: white; color: var(--primary); border: none; width: 100%; padding: 14px; border-radius: 12px; font-weight: bold; font-size: 1rem; cursor: pointer; margin-top: 5px; }}
            
            .modal {{ display: none; position: fixed; z-index: 2000; left: 0; top: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.7); overflow-y: auto; }}
            .modal-content {{ background: white; margin: 5% auto; padding: 20px; width: 95%; max-width: 500px; border-radius: 15px; box-sizing: border-box; text-align: center; }}
            .modal-info-body {{ background: #f8f9fa; padding: 15px; border-radius: 10px; border-left: 5px solid var(--primary); margin: 15px 0; font-size: 0.95rem; line-height: 1.5; text-align: left; }}
            .prod-img-modal {{ max-width: 250px; height: auto; border-radius: 10px; margin: 0 auto 15px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); display: none; }}
            .form-group {{ margin-bottom: 12px; }}
        </style>
    </head>
    <body>
    <div class="container">
        <div class="header-logo-container">
            <img src="https://raw.githubusercontent.com/glabpep/ordemarg/main/1.png" alt="G-LAB PEPTIDES" style="max-width: 200px;">
        </div>
        <p class="subtitle">Stock Actualizado y Pedidos Online</p>

        <div class="lote-alert-card">
            📢 Llegada prevista de nuevos productos el 09/03/2026. El stock del sitio será actualizado.
        </div>

        <div id="main-info-alert" class="info-alert-card">
            <span class="close-alert" onclick="this.parentElement.style.display='none'">&times;</span>
            <strong>Aviso importante:</strong> Los productos se envasan en forma sólida, por lo que no requieren refrigeración para conservar sus propiedades. El producto debe diluirse en solución bacteriostática (se vende por separado). Después de la dilución debe mantenerse refrigerado.
  <br><strong>NOMBRE DE LA SOLUCIÓN:</strong> BACTERIOSTATIC WATER.
        </div>
        


        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th style="width: 45%;">Produto</th>
                        <th>Status</th>
                        <th>Preço</th>
                        <th>Ação</th>
                    </tr>
                </thead>
                <tbody>
    """
    for idx, row in df.iterrows():
        produto = str(row.get('PRODUTO', 'N/A')).strip()
        espec = f"{row.get('VOLUME', '')} {row.get('MEDIDA', '')}".strip()
        preco = row.get('Preço (U$)', 0)
        estoque_status = str(row.get('ESTOQUE', row.get('STATUS', ''))).strip().upper()
        
        is_available = "DISPONÍVEL" in estoque_status
        status_class = "status-disponivel" if is_available else "status-espera"
        btn_disabled = "" if is_available else "disabled"
        simbolo = "+" if is_available else "✖"
        
        html_template += f"""
                    <tr>
                        <td>
                            <strong>{produto}</strong><br>
                            <small style="color:#666">{espec}</small><br>
                            <button class="btn-info" onclick="abrirInfo({idx})">+ informações</button>
                        </td>
                        <td><span class="{status_class}">{estoque_status}</span></td>
                        <td style="white-space: nowrap;">U$ {preco:,.2f}</td>
                        <td>
                            <button onclick="adicionar({idx})" {btn_disabled} class="btn-add">
                                {simbolo}
                            </button>
                        </td>
                    </tr>
        """

    html_template += f"""
                </tbody>
            </table>
        </div>
    </div>

    <div id="modalInfo" class="modal">
        <div class="modal-content">
            <h2 id="info-titulo" style="color: var(--primary); margin-top: 0; font-size: 1.2rem;"></h2>
            <img id="info-imagem" src="" alt="Produto" class="prod-img-modal">
            <div class="modal-info-body" id="info-texto"></div>
            <button onclick="fecharInfo()" class="btn-add" style="background:#6c757d">Fechar</button>
        </div>
    </div>
    <div id="cart-panel" class="cart-panel">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <h3 style="margin:0">🛒 Seu Pedido (<span id="cart-count">0</span>)</h3>
            <button onclick="document.getElementById('cart-panel').style.display='none'" style="background:none; border:none; color:white; font-size:1.5rem;">▾</button>
        </div>
        
        <div id="cart-list" class="cart-list"></div>

        <div class="coupon-section">
            <input type="text" id="coupon-code" class="coupon-input" placeholder="Cupom de Desconto">
            <button onclick="aplicarCupom()" class="btn-coupon">Aplicar</button>
        </div>

        <div id="ship-info-container" class="ship-row" style="display:none;">
            <span id="ship-info-text"></span>
            <button onclick="removerFrete()" class="btn-remove" style="background:rgba(255,255,255,0.2); margin:0;">✖</button>
        </div>
        
        <div id="discount-row" class="discount-line">
            <span>Desconto (<span id="discount-name"></span>):</span>
            <span>- U$ <span id="discount-val">0.00</span></span>
        </div>

        <div class="total-row">
            <span>TOTAL GERAL:</span>
            <span>U$ <span id="total-val">0.00</span></span>
        </div>
        <button class="btn-checkout-final" onclick="abrirCheckout()">Ir para Pagamento</button>
    </div>
    <div id="modalCheckout" class="modal">
        <div class="modal-content" style="text-align: left;">
            <h2 style="color: var(--primary); margin-top: 0;">📦 Datos de Entrega</h2>
            <div class="form-group"><input type="text" id="f_nome" class="input-style" placeholder="Nombre Completo"></div>
            <div class="form-group"><input type="text" id="f_end" class="input-style" placeholder="Dirección (Calle/Av)"></div>
            <div style="display:flex; gap:10px; margin-bottom:12px;">
                <input type="text" id="f_num" class="input-style" style="width:30%" placeholder="Nº">
                <input type="text" id="f_bairro" class="input-style" style="width:70%" placeholder="Barrio">
            </div>
            <div class="form-group"><input type="text" id="f_comp" class="input-style" placeholder="Complemento (Opcional)"></div>
            <div style="display:flex; gap:10px; margin-bottom:12px;">
                <input type="text" id="f_cidade" class="input-style" placeholder="Ciudad">
                <input type="text" id="f_estado" class="input-style" style="width:30%" placeholder="Provincia">
            </div>
            <div class="form-group"><input type="tel" id="f_tel" class="input-style" placeholder="WhatsApp"></div>
            <div class="form-group">
                <label style="font-size:12px; font-weight:bold;">Forma de Pago:</label>
                <select id="f_pgto" class="input-style">
                    <option value="Pix">Pix (Aprobación Inmediata)</option>
                    <option value="Cartão de crédito">Tarjeta de Crédito (HASTA 12 CUOTAS CON INTERÉS DE LA PLATAFORMA)</option>
                </select>
            </div>
            <button onclick="enviarPedido()" class="btn-add" style="padding:15px; font-size:1.1rem; background:var(--primary);">ENVIAR A WHATSAPP</button>
            <button onclick="fecharCheckout()" style="background:none; border:none; width:100%; color:#666; margin-top:15px;">Cancelar / Volver</button>
        </div>
    </div>
    <script>
        const PRODUTOS = {js_produtos};
        const URL_BASE_IMG = "{URL_RAW_GITHUB}";
        let carrinho = [];
        let freteV = 0;
        let freteD = "";
        let cupomAtivo = null;

        const REGIOES = {{
            'SUL': ['PR', 'SC', 'RS'],
            'SUDESTE': ['SP', 'RJ', 'MG', 'ES'],
            'CENTRO-OESTE': ['DF', 'GO', 'MT', 'MS'],
            'NORTE': ['AM', 'RR', 'AP', 'PA', 'TO', 'RO', 'AC'],
            'NORDESTE': ['BA', 'SE', 'AL', 'PE', 'PB', 'RN', 'CE', 'PI', 'MA']
        }};

        
        function abrirInfo(id) {{
            const p = PRODUTOS.find(x => x.id === id);
            if(p) {{
                document.getElementById('info-titulo').innerText = p.nome;
                document.getElementById('info-texto').innerText = p.info;
                
                const imgElement = document.getElementById('info-imagem');
                const nomeLimpo = p.nome.trim();
                const extensoes = ['.webp', '.png', '.jpg', '.jpeg'];

                function tentarExtensao(index) {{
                    if (index >= extensoes.length) {{ 
                        imgElement.style.display = 'none'; 
                        return; 
                    }}
                    const caminhoImg = URL_BASE_IMG + encodeURIComponent(nomeLimpo) + extensoes[index];
                    imgElement.src = caminhoImg;
                    imgElement.onload = () => imgElement.style.display = 'block';
                    imgElement.onerror = () => tentarExtensao(index + 1);
                }}
                tentarExtensao(0);

                document.getElementById('modalInfo').style.display = 'block';
                document.body.style.overflow = 'hidden'; // TRAVA O SCROLL DA PÁGINA
            }}
        }}
        function fecharInfo() {{ 
            document.getElementById('modalInfo').style.display = 'none'; 
            document.body.style.overflow = 'auto'; // LIBERA O SCROLL
        }}

        function abrirCheckout() {{
            if (carrinho.length === 0) return alert("Seu carrinho está vazio!");
            document.getElementById('modalCheckout').style.display = 'block';
            document.body.style.overflow = 'hidden'; // TRAVA O SCROLL
        }}

        function fecharCheckout() {{
            document.getElementById('modalCheckout').style.display = 'none';
            document.body.style.overflow = 'auto'; // LIBERA O SCROLL
        }}

        
        function adicionar(id) {{
            const p = PRODUTOS.find(x => x.id === id);
            if(p) {{
                carrinho.push({{...p, uid: Date.now() + Math.random()}});
                atualizarInterface();
            }}
        }}

        function remover(uid) {{
            carrinho = carrinho.filter(x => x.uid !== uid);
            if (carrinho.length === 0) removerFrete();
            atualizarInterface();
        }}

        function removerFrete() {{
            freteV = 0; freteD = "";
            document.getElementById('resultado-frete').innerText = "";
            document.getElementById('cep-destino').value = "";
            atualizarInterface();
        }}

        function aplicarCupom() {{
            const code = document.getElementById('coupon-code').value.trim().toUpperCase();
            const cupons = {{
                'BRUNA5': 0.05, 'DANI5': 0.05, 'GILMARA5': 0.05,
                'DAFNE10': 0.10, 'NOS5': 0.05, 'ROGERIO5': 0.05,
                'ANDERSON5': 0.05, 'JAQUE5': 0.05, 'CABRAL5': 0.05, 'KARLINHA5': 0.05,
                'LUD5': 0.05, 'CASSIA5': 0.05, 'THAIS5': 0.05, 'NATAN': 0.00000001, 'LIRICY5': 0.05,
                'ANDREAFLEURY': 0.05, 'BRUNA10': 0.10, 'ANA5': 0.05, 
            }};
            if(cupons[code]) {{
                cupomAtivo = {{ nome: code, desc: cupons[code] }};
                alert("Cupom aplicado!");
            }} else {{
                cupomAtivo = null; alert("Cupom inválido.");
            }}
            atualizarInterface();
        }}
        function atualizarInterface() {{
            const list = document.getElementById('cart-list');
            const panel = document.getElementById('cart-panel');
            panel.style.display = carrinho.length > 0 ? 'block' : 'none';
            document.getElementById('cart-count').innerText = carrinho.length;
            list.innerHTML = '';
            let subtotal = 0;
            
            carrinho.forEach(item => {{
                subtotal += item.preco;
                list.innerHTML += `<div class="cart-item"><span>${{item.nome}}</span><span>U$ ${{item.preco.toFixed(2)}} <button class="btn-remove" onclick="remover(${{item.uid}})">×</button></span></div>`;
            }});

            // Lógica do Brinde Bruna5
            if (cupomAtivo && cupomAtivo.nome === 'BRUNA5') {{
                list.innerHTML += `<div class="cart-item" style="background: rgba(0,255,0,0.1); border: 1px dashed #fff;">
                    <span>🎁 BRINDE CUPOM BRUNA<br><small>Bacteriostatic Water 7ml</small></span>
                    <span style="color:#00ff00; font-weight:bold;">GRÁTIS</span>
                </div>`;
            }}

            let valorDesconto = cupomAtivo ? subtotal * cupomAtivo.desc : 0;
            document.getElementById('discount-row').style.display = cupomAtivo ? 'flex' : 'none';
            if(cupomAtivo) {{
                document.getElementById('discount-name').innerText = cupomAtivo.nome;
                document.getElementById('discount-val').innerText = valorDesconto.toFixed(2);
            }}

            const shipContainer = document.getElementById('ship-info-container');
            shipContainer.style.display = freteV > 0 ? 'flex' : 'none';
            if(freteV > 0) document.getElementById('ship-info-text').innerText = "🚚 " + freteD;

            const totalFinal = (subtotal - valorDesconto) + freteV;
            document.getElementById('total-val').innerText = totalFinal.toLocaleString('pt-BR', {{minimumFractionDigits: 2}});
        }}

        function abrirCheckout() {{
            if (carrinho.length === 0) {{
                alert("Seu carrinho está vazio!");
                return;
            }}

            document.getElementById('modalCheckout').style.display = 'block';
        }}

        function fecharCheckout() {{ document.getElementById('modalCheckout').style.display = 'none'; }}

        function enviarPedido() {{
            const dados = {{
                n: document.getElementById('f_nome').value.trim().toUpperCase(),
                e: document.getElementById('f_end').value.trim().toUpperCase(),
                nu: document.getElementById('f_num').value.trim().toUpperCase(),
                ba: document.getElementById('f_bairro').value.trim().toUpperCase(),
                co: document.getElementById('f_comp').value.trim().toUpperCase(),
                ci: document.getElementById('f_cidade').value.trim().toUpperCase(),
                es: document.getElementById('f_estado').value.trim().toUpperCase(),
                ce: "",
                t: document.getElementById('f_tel').value.trim().toUpperCase(),
                p: document.getElementById('f_pgto').value.toUpperCase()
            }};
            if(!dados.n || !dados.e || !dados.nu || !dados.ba || !dados.ci || !dados.es || !dados.t) {{
                alert("Por favor, preencha todos os campos obrigatórios!");
                return;
            }}
            const temSolucao = carrinho.some(item => item.nome.toUpperCase().includes("BACTERIOSTATIC WATER"));
            const temBrinde = cupomAtivo && cupomAtivo.nome === 'BRUNA5';

            if(!temSolucao && !temBrinde) {{
                const confirmar = confirm("¿Está seguro de que desea realizar el pedido sin la solución para diluir el producto?");
                if(!confirmar) {{
                    fecharCheckout();
                    document.getElementById('cart-panel').style.display = 'none';
                    alert("Por favor, adicione a BACTERIOSTATIC WATER (3ml, 10ml ou 30ml) à sua lista de produtos.");
                    window.scrollTo({{ top: 0, behavior: 'smooth' }});
                    return; 
                }}
            }}
            let subtotalItens = 0;
            carrinho.forEach(i => subtotalItens += i.preco);
            let descTotal = cupomAtivo ? subtotalItens * cupomAtivo.desc : 0;
            
            let msg = "*NOVO PEDIDO G-LAB*%0A%0A";
            msg += "*DADOS DO CLIENTE:*%0A";
            msg += "• *NOME:* " + dados.n + "%0A";
            msg += "• *WHATSAPP:* " + dados.t + "%0A";
            msg += "• *END:* " + dados.e + ", " + dados.nu + "%0A";
            msg += "• *BAIRRO:* " + dados.ba + "%0A";
            if(dados.co) msg += "• *COMPL:* " + dados.co + "%0A";
            msg += "• *CIDADE:* " + dados.ci + "-" + dados.es + "%0A";
            msg += "• *CEP:* " + (dados.ce || "NÃO INFORMADO") + "%0A";
            msg += "• *PAGAMENTO:* " + dados.p + "%0A%0A";
            
            msg += "*ITENS DO PEDIDO:*%0A";
            carrinho.forEach(i => {{ 
                let linhaItem = "• " + i.nome.toUpperCase() + " (" + i.espec.toUpperCase() + ") - U$ " + i.preco.toFixed(2);
                if(cupomAtivo) {{
                    let descI = i.preco * cupomAtivo.desc;
                    linhaItem += " - COM DESCONTO (" + (cupomAtivo.desc * 100).toFixed(0) + "%) U$ " + (i.preco - descI).toFixed(2);
                }}
                msg += linhaItem + "%0A"; 
            }});

            if (temBrinde) {{
                msg += "• BRINDE CUPOM BRUNA (BACTERIOSTATIC WATER 7 ML) - U$ 0,00%0A";
            }}

            if(cupomAtivo) msg += "%0A🏷️ *CUPOM:* " + cupomAtivo.nome + " (-U$ " + descTotal.toFixed(2) + ")";
            msg += "%0A🚚 *FRETE:* " + freteD.toUpperCase();
            msg += "%0A%0A*TOTAL GERAL: U$ " + (subtotalItens - descTotal + freteV).toFixed(2) + "*";
            
            window.open("https://wa.me/+17746222523?text=" + msg, '_blank');
        }}
    </script>
    </body>
    </html>
    """
    # Salva o arquivo final
    caminho_saida = os.path.join(diretorio_atual, 'index.html')
    try:
        with open(caminho_saida, 'w', encoding='utf-8') as f:
            f.write(html_template)
        print(f"✅ Sucesso! Site gerado em: {caminho_saida}")
        print(f"🚀 Sistema de redundância de CEP (ViaCEP + BrasilAPI) integrado.")
    except Exception as e:
        print(f"❌ Erro ao salvar o arquivo: {e}")

if __name__ == "__main__":
    gerar_site_vendas_completo()


