import pandas as pd
import os
import json

def gerar_site_vendas_completo():
    diretorio_atual = os.path.dirname(os.path.abspath(__file__))
    
    # -------------------------------------------------------------------------
    # BUSCA DE ARQUIVOS DE DADOS
    # -------------------------------------------------------------------------
    arquivo_dados = None
    for nome in ['stock_0202 - NOVA.xlsx', 'stock_2901.xlsx - Plan1.csv', 'stock_0202.xlsx']:
        caminho = os.path.join(diretorio_atual, nome)
        if os.path.exists(caminho):
            arquivo_dados = caminho
            break

    if not arquivo_dados:
        print(f"❌ Error: Archivo de stock no encontrado.")
        return

    # -------------------------------------------------------------------------
    # DICIONÁRIO TÉCNICO
    # -------------------------------------------------------------------------
    infos_tecnicas = {
        "5-AMINO": "Inhibidor selectivo de NNMT...",
        "AICAR": "Activador de AMPK...",
        "AOD 9604": "Análogo lipolítico de hGH...",
        # ... mantenha o restante do seu dicionário aqui ...
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
            
            info_prod = "Información técnica detallada no disponible."
            for chave, texto in infos_tecnicas.items():
                if chave in nome_prod.upper():
                    info_prod = texto
                    break

            estoque_raw = str(row.get('ESTOQUE', row.get('STATUS', ''))).strip().upper()
            
            produtos_base.append({
                "id": idx,
                "nome": nome_prod,
                "espec": f"{row.get('VOLUME', '')} {row.get('MEDIDA', '')}".strip(),
                "preco": float(row.get('Preço (U$)', 0)),
                "status": estoque_raw,
                "info": info_prod
            })
        
        # Gerar o JSON
        js_produtos = json.dumps(produtos_base, indent=4)
        
        # SALVAMENTO
        caminho_dados_json = os.path.join(diretorio_atual, 'estoque.json')
        with open(caminho_dados_json, 'w', encoding='utf-8') as f:
            f.write(js_produtos) 
        
        print(f"✅ Dados atualizados em: estoque.json")
        print(f"⚠️ O 'index.html' está protegido e não foi tocado.")

    except Exception as e:
        print(f"❌ Erro ao processar ou salvar: {e}")

if __name__ == "__main__":
    gerar_site_vendas_completo()

