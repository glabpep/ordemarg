import pandas as pd
import os
import json

def gerar_site_vendas_completo():
    diretorio_atual = os.path.dirname(os.path.abspath(__file__))
    
    # -------------------------------------------------------------------------
    # BUSCA DE ARQUIVOS DE DADOS (LOGICA ORIGINAL)
    # -------------------------------------------------------------------------
    arquivo_dados = None
    for nome in ['stock_0202 - NOVA.xlsx', 'stock_2901.xlsx - Plan1.csv', 'stock_0202.xlsx']:
        caminho = os.path.join(diretorio_atual, nome)
        if os.path.exists(caminho):
            arquivo_dados = caminho
            break

    if not arquivo_dados:
        print(f"❌ Error: Archivo de stock no encontrado en: {diretorio_atual}")
        return

    # -------------------------------------------------------------------------
    # DICIONÁRIO TÉCNICO INTEGRAL (SEM ENCURTAMENTOS)
    # -------------------------------------------------------------------------
    infos_tecnicas = {
        "5-AMINO": "Inhibidor selectivo de NNMT: Actúa bloqueando la enzima nicotinamida N-metiltransferasa, lo que eleva los niveles intracelulares de NAD+ y SAM. Estudios indican eficacia en la reversión de la obesidad y optimización del gasto energético basal.",
        "AICAR": "Activador de AMPK: Imita el AMP intracelular para activar la proteína quinasa. Investigado por aumentar la captación de glucosa muscular, la oxidación de ácidos grasos y la resistencia cardiovascular.",
        "AOD 9604": "Análogo lipolítico de hGH: Diseñado para aislar las propiedades de quema de grasa de la hormona del crecimiento sin inducir efectos hiperglucémicos. Aplicado en estudios de obesidad y regeneración de cartílago.",
        "ARA 290": "Derivado de eritropoyetina investigado para regeneración nerviosa y dolor neuropático.",
        "BACTERIOSTATIC WATER": "Agua bacteriostática con 0,9% de alcohol bencílico que previene la proliferación bacteriana en viales de dosis múltiples.",
        "BPC-157": "Pentadecapéptido gástrico investigado por acelerar la angiogénesis, la cicatrización de tendones, ligamentos y la salud del tracto gastrointestinal.",
        "CJC-1295": "Secretagogo de GH de larga duración: Análogo de GHRH que aumenta los niveles plasmáticos de la hormona del crecimiento y el IGF-1 de manera sostenida.",
        "IPAMORELIN": "Agonista selectivo del receptor de grelina: Estimula la liberación pulsátil de GH sin aumentar significativamente el cortisol, la prolactina o la ACTH.",
        "NAD+": "Coenzima esencial para el metabolismo energético, la función mitocondrial y la reparación del ADN. Investigado por sus efectos antienvejecimiento.",
        "SEMAGLUTIDE": "Agonista del receptor de GLP-1: Retrasa el vaciamiento gástrico, aumenta la saciedad y mejora el control glucémico.",
        "TIRZEPATIDE": "Agonista dual de los receptores GIP y GLP-1: Promueve una pérdida de peso significativa y mejora la sensibilidad a la insulina.",
        "TB-500": "Versión sintética de la Timosina Beta-4: Involucrada en la migración celular, la reparación de tejidos y la reducción de la inflamación.",
        "MK-677": "Secretagogo de GH administrado por vía oral (Ibutamoren): Imita la acción de la grelina para aumentar los niveles de GH e IGF-1 sin afectar el cortisol.",
        "MOTS-C": "Péptido derivado de la mitocondria: Regula el metabolismo de la glucosa y promueve la homeostasis metabólica y la resistencia física.",
        "FRAGMENT 176-191": "Fracción terminal de la hGH: Específicamente diseñada para la lipólisis (quema de grasa) sin afectar la sensibilidad a la insulina.",
        "TESAMORELIN": "Análogo del factor liberador de hormona de crecimiento: Utilizado en estudios para reducir la grasa adiposa visceral.",
        "FOLLISTATIN 315": "Proteína que inhibe la miostatina: Investigada por su potencial para aumentar la masa muscular mediante la regulación del crecimiento celular.",
        "EPITALON": "Péptido sintético regulador de la telomerasa: Investigado por sus propiedades antienvejecimiento y regulación del ciclo circadiano."
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
            
            # Busca informação técnica expandida
            info_prod = "Información técnica detallada no disponible para este producto en este momento."
            for chave, texto in infos_tecnicas.items():
                if chave in nome_prod.upper():
                    info_prod = texto
                    break

            # Lógica de estoque rigorosa
            estoque_raw = str(row.get('ESTOQUE', row.get('STATUS', ''))).strip().upper()
            
            produtos_base.append({
                "id": idx,
                "nome": nome_prod,
                "espec": f"{row.get('VOLUME', '')} {row.get('MEDIDA', '')}".strip(),
                "preco": float(row.get('Preço (U$)', row.get('Preço (U$)', 0))),
                "status": estoque_raw,
                "info": info_prod
            })
        js_produtos = json.dumps(produtos_base)
        
    except Exception as e:
        print(f"❌ Error al procesar el archivo: {e}")
        return

    # -------------------------------------------------------------------------
    # TEMPLATE HTML INTEGRAL (TODAS AS LINHAS E CSS ORIGINAL)
    # -------------------------------------------------------------------------
    html_template = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <title>G-LAB PEPTIDES - Pedidos Online</title>
        <style>
            :root {{
                --primary: #004a99;
                --secondary: #28a745;
                --danger: #dc3545;
                --warning: #ffc107;
                --light: #f4f7f9;
                --dark: #333;
                --white: #ffffff;
            }}
            body {{
                font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
                background-color: var(--light);
                margin: 0;
                padding: 0;
                color: var(--dark);
                line-height: 1.6;
            }}
            .container {{
                max-width: 900px;
                margin: 0 auto;
                background-color: var(--white);
                min-height: 100vh;
                padding: 20px;
                box-sizing: border-box;
                box-shadow: 0 0 20px rgba(0,0,0,0.1);
                padding-bottom: 250px;
            }}
            .header-logo-container {{
                text-align: center;
                padding: 20px 0;
                border-bottom: 2px solid #eee;
                margin-bottom: 20px;
            }}
            .header-logo {{
                max-width: 280px;
                height: auto;
            }}
            .subtitle {{
                text-align: center;
                color: #666;
                font-size: 1rem;
                margin-top: 10px;
                font-weight: 500;
                text-transform: uppercase;
                letter-spacing: 1px;
            }}
            .lote-alert-card {{
                background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
                border: 1px solid #90caf9;
                color: #0d47a1;
                padding: 20px;
                border-radius: 12px;
                margin-bottom: 25px;
                font-size: 0.95rem;
                font-weight: bold;
                border-left: 6px solid #2196f3;
                display: flex;
                align-items: center;
                gap: 15px;
            }}
            .table-container {{
                width: 100%;
                overflow-x: auto;
                margin-top: 20px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                min-width: 500px;
            }}
            th {{
                background-color: var(--primary);
                color: var(--white);
                padding: 15px;
                text-align: left;
                font-size: 0.9rem;
                text-transform: uppercase;
            }}
            td {{
                padding: 15px;
                border-bottom: 1px solid #f0f0f0;
                vertical-align: middle;
            }}
            .status-disponivel {{
                color: var(--secondary);
                font-weight: bold;
                display: flex;
                align-items: center;
                gap: 5px;
            }}
            .status-espera {{
                color: var(--danger);
                font-weight: bold;
                background-color: #fff5f5;
                padding: 6px 10px;
                border-radius: 6px;
                border: 1px solid var(--danger);
                display: inline-block;
                font-size: 0.8rem;
            }}
            .btn-add {{
                background-color: var(--secondary);
                color: white;
                border: none;
                padding: 12px;
                border-radius: 8px;
                cursor: pointer;
                font-weight: bold;
                width: 100%;
                transition: transform 0.2s, background 0.2s;
                font-size: 1.1rem;
            }}
            .btn-add:active {{ transform: scale(0.95); }}
            .btn-add:disabled {{
                background-color: #e0e0e0;
                color: #9e9e9e;
                cursor: not-allowed;
            }}
            .btn-info-link {{
                background: none;
                border: none;
                color: var(--primary);
                font-size: 0.8rem;
                text-decoration: underline;
                cursor: pointer;
                padding: 0;
                margin-top: 5px;
            }}
            .cart-panel {{
                position: fixed;
                bottom: 0;
                left: 0;
                right: 0;
                background-color: var(--primary);
                color: white;
                padding: 20px;
                border-radius: 25px 25px 0 0;
                box-shadow: 0 -5px 25px rgba(0,0,0,0.2);
                z-index: 1000;
                display: none;
            }}
            @media (min-width: 768px) {{
                .cart-panel {{
                    width: 450px;
                    left: auto;
                    right: 30px;
                    bottom: 30px;
                    border-radius: 20px;
                }}
            }}
            .modal {{
                display: none;
                position: fixed;
                z-index: 9999;
                left: 0;
                top: 0;
                width: 100%;
                height: 100%;
                background-color: rgba(0,0,0,0.8);
                backdrop-filter: blur(5px);
            }}
            .modal-content {{
                background-color: var(--white);
                margin: 5% auto;
                padding: 25px;
                width: 90%;
                max-width: 550px;
                border-radius: 20px;
                position: relative;
                animation: slideIn 0.3s ease-out;
            }}
            @keyframes slideIn {{
                from {{ transform: translateY(50px); opacity: 0; }}
                to {{ transform: translateY(0); opacity: 1; }}
            }}
            .input-style {{
                width: 100%;
                padding: 14px;
                margin-bottom: 12px;
                border: 1px solid #ddd;
                border-radius: 10px;
                box-sizing: border-box;
                font-size: 16px;
                outline: none;
            }}
            .input-style:focus {{ border-color: var(--primary); box-shadow: 0 0 0 2px rgba(0,74,153,0.1); }}
        </style>
    </head>
    <body>

    <div class="container">
        <div class="header-logo-container">
            <img src="1.png" alt="G-LAB PEPTIDES" class="header-logo">
            <div class="subtitle">Excelencia en Peptidos - Argentina</div>
        </div>

        <div class="lote-alert-card">
            <div>📢 <strong>AVISO IMPORTANTE:</strong> Nueva reposición de stock prevista para el 09/03/2026. Los pedidos realizados ahora aseguran disponibilidad inmediata de los ítems en stock.</div>
        </div>

        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>Producto / Especificación</th>
                        <th>Estado</th>
                        <th>Precio</th>
                        <th>Seleccionar</th>
                    </tr>
                </thead>
                <tbody>
    """

    for p in produtos_base:
        is_avail = "DISPONÍVEL" in p['status'] or "STOCK" in p['status']
        st_class = "status-disponivel" if is_avail else "status-espera"
        st_text = "✅ EN STOCK" if is_avail else p['status']
        btn_attr = "" if is_avail else "disabled"
        icon = "🛒 AÑADIR" if is_avail else "AGOTADO"
        
        html_template += f"""
                    <tr>
                        <td>
                            <div style="font-weight: bold; font-size: 1.05rem;">{p['nome']}</div>
                            <div style="color: #666; font-size: 0.85rem;">{p['espec']}</div>
                            <button class="btn-info-link" onclick="abrirInfo({p['id']})">+ Ver información técnica</button>
                        </td>
                        <td><span class="{st_class}">{st_text}</span></td>
                        <td style="font-weight: bold; color: var(--primary);">U$ {p['preco']:.2f}</td>
                        <td>
                            <button onclick="adicionarAoCarrinho({p['id']})" {btn_attr} class="btn-add">{icon}</button>
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
            <h2 id="info-titulo" style="color: var(--primary); margin-top: 0;"></h2>
            <hr>
            <div id="info-texto" style="margin: 20px 0; font-size: 1.05rem; color: #444; line-height: 1.5;"></div>
            <button onclick="fecharInfo()" class="btn-add" style="background-color: #666;">CERRAR DETALLES</button>
        </div>
    </div>

    <div id="cart-panel" class="cart-panel">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
            <strong style="font-size: 1.2rem;">🛒 MI PEDIDO (<span id="cart-count">0</span>)</strong>
            <button onclick="toggleCart()" style="background: none; border: none; color: white; font-size: 1.5rem; cursor: pointer;">✕</button>
        </div>
        
        <div id="cart-list" style="max-height: 180px; overflow-y: auto; margin-bottom: 15px; border-top: 1px solid rgba(255,255,255,0.2); padding-top: 10px;"></div>
        
        <div style="background: rgba(255,255,255,0.1); padding: 10px; border-radius: 10px; margin-bottom: 15px;">
            <div style="display: flex; gap: 8px;">
                <input type="text" id="coupon-code" class="input-style" style="margin-bottom: 0; padding: 8px;" placeholder="Cupón de Descuento">
                <button onclick="aplicarCupom()" style="background: var(--warning); border: none; padding: 0 15px; border-radius: 8px; font-weight: bold; cursor: pointer;">OK</button>
            </div>
        </div>

        <div style="font-size: 1.3rem; font-weight: bold; display: flex; justify-content: space-between; margin-bottom: 15px;">
            <span>TOTAL ESTIMADO:</span>
            <span>U$ <span id="total-val">0.00</span></span>
        </div>
        
        <button class="btn-add" onclick="abrirCheckout()" style="background-color: var(--white); color: var(--primary);">CONTINUAR AL PAGO</button>
    </div>

    <div id="modalCheckout" class="modal">
        <div class="modal-content">
            <h3 style="margin-top: 0; color: var(--primary);">DATOS PARA EL ENVÍO</h3>
            <p style="font-size: 0.8rem; color: #888; margin-bottom: 15px;">Complete la información para generar el pedido por WhatsApp.</p>
            
            <input type="text" id="f_nome" class="input-style" placeholder="Nombre y Apellido Completo *">
            <input type="tel" id="f_tel" class="input-style" placeholder="WhatsApp (con código de área) *">
            
            <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 10px;">
                <input type="text" id="f_end" class="input-style" placeholder="Calle / Dirección *">
                <input type="text" id="f_num" class="input-style" placeholder="N° / Depto *">
            </div>
            
            <input type="text" id="f_ba" class="input-style" placeholder="Barrio / Localidad *">
            <input type="text" id="f_ci" class="input-style" placeholder="Ciudad / Provincia *">
            
            <label style="font-size: 0.8rem; font-weight: bold; color: #666;">MÉTODO DE PAGO PREFERIDO:</label>
            <select id="f_pgto" class="input-style">
                <option value="TRANSFERENCIA BANCARIA">TRANSFERENCIA BANCARIA (ARS/USD)</option>
                <option value="USDT / CRIPTOMONEDAS">USDT / CRIPTOMONEDAS</option>
                <option value="TARJETA DE CRÉDITO">TARJETA DE CRÉDITO (Link de Pago)</option>
                <option value="EFECTIVO">EFECTIVO (Puntos seleccionados)</option>
            </select>
            
            <button onclick="enviarPedidoFinal()" class="btn-add" style="margin-top: 10px;">CONFIRMAR Y ENVIAR WHATSAPP</button>
            <button onclick="fecharCheckout()" style="background: none; border: none; width: 100%; color: #999; margin-top: 15px; cursor: pointer;">VOLVER AL CARRINHO</button>
        </div>
    </div>

    <script>
        const PRODUTOS = {js_produtos};
        let carrinho = [];
        let cupomAtivo = null;

        function adicionarAoCarrinho(id) {{
            const p = PRODUTOS.find(x => x.id === id);
            carrinho.push({{...p, uid: Date.now()}});
            atualizarInterface();
            document.getElementById('cart-panel').style.display = 'block';
        }}

        function removerItem(uid) {{
            carrinho = carrinho.filter(x => x.uid !== uid);
            atualizarInterface();
            if(carrinho.length === 0) document.getElementById('cart-panel').style.display = 'none';
        }}

        function aplicarCupom() {{
            const code = document.getElementById('coupon-code').value.trim().toUpperCase();
            const cuponsValidos = {{ 'BRUNA5': 0.05, 'BRUNA10': 0.10, 'PROMO2026': 0.15 }};
            
            if(cuponsValidos[code]) {{
                cupomAtivo = {{ nome: code, desc: cuponsValidos[code] }};
                alert("✅ ¡Cupón " + code + " aplicado con éxito!");
            }} else {{
                cupomAtivo = null;
                alert("❌ Cupón no válido o expirado.");
            }}
            atualizarInterface();
        }}

        function atualizarInterface() {{
            const listElement = document.getElementById('cart-list');
            const countElement = document.getElementById('cart-count');
            const totalElement = document.getElementById('total-val');
            
            countElement.innerText = carrinho.length;
            let subtotal = 0;
            let html = "";
            
            carrinho.forEach(item => {{
                subtotal += item.preco;
                html += `
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; background: rgba(255,255,255,0.05); padding: 5px; border-radius: 5px;">
                        <span style="font-size: 0.9rem;">${{item.nome}}</span>
                        <div style="display: flex; align-items: center; gap: 10px;">
                            <span style="font-weight: bold;">U$ ${{item.preco.toFixed(2)}}</span>
                            <button onclick="removerItem(${{item.uid}})" style="background: #ff4444; border: none; color: white; border-radius: 50%; width: 22px; height: 22px; cursor: pointer; font-size: 12px;">✕</button>
                        </div>
                    </div>
                `;
            }});

            if(cupomAtivo && cupomAtivo.nome === 'BRUNA5') {{
                html += `<div style="color: #2ecc71; font-weight: bold; font-size: 0.85rem; margin-top: 10px;">🎁 REGALO INCLUIDO: Bacteriostatic Water 7ml</div>`;
            }}

            const desconto = cupomAtivo ? subtotal * cupomAtivo.desc : 0;
            const totalFinal = subtotal - desconto;
            
            listElement.innerHTML = html;
            totalElement.innerText = totalFinal.toLocaleString('en-US', {{minimumFractionDigits: 2, maximumFractionDigits: 2}});
        }}

        function abrirInfo(id) {{
            const p = PRODUTOS.find(x => x.id === id);
            document.getElementById('info-titulo').innerText = p.nome;
            document.getElementById('info-texto').innerText = p.info;
            document.getElementById('modalInfo').style.display = 'block';
        }}
        function fecharInfo() {{ document.getElementById('modalInfo').style.display = 'none'; }}
        function toggleCart() {{ 
            const p = document.getElementById('cart-panel');
            p.style.display = (p.style.display === 'none' || p.style.display === '') ? 'block' : 'none';
        }}
        function abrirCheckout() {{ document.getElementById('modalCheckout').style.display = 'block'; }}
        function fecharCheckout() {{ document.getElementById('modalCheckout').style.display = 'none'; }}

        function enviarPedidoFinal() {{
            const campos = {{
                n: document.getElementById('f_nome').value.trim().toUpperCase(),
                t: document.getElementById('f_tel').value.trim(),
                e: document.getElementById('f_end').value.trim().toUpperCase(),
                nu: document.getElementById('f_num').value.trim().toUpperCase(),
                ba: document.getElementById('f_ba').value.trim().toUpperCase(),
                ci: document.getElementById('f_ci').value.trim().toUpperCase(),
                p: document.getElementById('f_pgto').value
            }};

            if(!campos.n || !campos.t || !campos.e || !campos.ba) {{
                alert("⚠️ Por favor, complete todos los campos obligatorios (*)");
                return;
            }}

            // Validação de segurança da água bacteriostática (Original do anexo)
            const temSolucao = carrinho.some(i => i.nome.toUpperCase().includes("BACTERIOSTATIC WATER"));
            const temBrinde = cupomAtivo && cupomAtivo.nome === 'BRUNA5';

            if(!temSolucao && !temBrinde) {{
                const confirmar = confirm("¿Está seguro de realizar el pedido sin la solución para dilución (Bacteriostatic Water)?");
                if(!confirmar) return;
            }}

            let subtotal = 0;
            carrinho.forEach(i => subtotal += i.preco);
            let descVal = cupomAtivo ? subtotal * cupomAtivo.desc : 0;

            let msg = "*NUEVO PEDIDO G-LAB PEPTIDES*%0A%0A";
            msg += "*DATOS DEL CLIENTE:*%0A";
            msg += "• *NOMBRE:* " + campos.n + "%0A";
            msg += "• *WHATSAPP:* " + campos.t + "%0A";
            msg += "• *DIRECCIÓN:* " + campos.e + " " + campos.nu + "%0A";
            msg += "• *LOCALIDAD:* " + campos.ba + " / " + campos.ci + "%0A%0A";
            
            msg += "*PRODUCTOS SELECCIONADOS:*%0A";
            carrinho.forEach(i => {{
                msg += "• " + i.nome.toUpperCase() + " (" + i.espec + ") - U$ " + i.preco.toFixed(2) + "%0A";
            }});
            
            if(temBrinde) msg += "• *REGALO:* BACTERIOSTATIC WATER 7ML (CUPÓN BRUNA5)%0A";
            
            if(cupomAtivo) msg += "%0A🏷️ *CUPÓN:* " + cupomAtivo.nome + " (-U$ " + descVal.toFixed(2) + ")";
            
            msg += "%0A%0A*TOTAL FINAL: U$ " + (subtotal - descVal).toFixed(2) + "*%0A";
            msg += "*PAGO:* " + campos.p;

            const url = "https://wa.me/+17746222523?text=" + msg;
            window.open(url, '_blank');
        }}

        // Fechar modais ao clicar fora
        window.onclick = function(event) {{
            if (event.target == document.getElementById('modalInfo')) fecharInfo();
            if (event.target == document.getElementById('modalCheckout')) fecharCheckout();
        }}
    </script>
    </body>
    </html>
    """

    # -------------------------------------------------------------------------
    # SALVAMENTO DO ARQUIVO
    # -------------------------------------------------------------------------
    
    # --- COLOQUE ESTE NOVO BLOCO ---
    caminho_dados_json = os.path.join(diretorio_atual, 'estoque.json')
    try:
        with open(caminho_dados_json, 'w', encoding='utf-8') as f:
            # Salvamos apenas a lista de produtos (js_produtos) que já foi gerada na linha 103
            f.write(js_produtos) 
        print(f"✅ Dados atualizados com sucesso em 'estoque.json'!")
        print(f"⚠️ O arquivo 'index.html' não foi tocado e o layout está preservado.")
    except Exception as e:
        print(f"❌ Error al guardar los datos: {e}")
    
if __name__ == "__main__":
    gerar_site_vendas_completo()


