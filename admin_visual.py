import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Configuração da Página
st.set_page_config(page_title="G-LAB - Painel Administrativo", layout="wide")

def localizar_planilha():
    diretorio_atual = os.path.dirname(os.path.abspath(__file__))
    for nome in ['stock_0202 - NOVA.xlsx', 'stock_2901.xlsx']:
        caminho = os.path.join(diretorio_atual, nome)
        if os.path.exists(caminho):
            return caminho
    return None

def main():
    st.title("🧪 G-LAB PEPTIDES - Gestão de Estoque")
    
    caminho_planilha = localizar_planilha()
    if not caminho_planilha:
        st.error("Arquivo de excel não encontrado no diretório!")
        return

    # Carregar dados
    df = pd.read_excel(caminho_planilha)
    
    # --- ABA 1: TABELA GERAL ---
    tab1, tab2 = st.tabs(["📊 Estoque Atual", "💰 Registrar Venda"])

    with tab1:
        st.subheader("Visualização em Tempo Real")
        # Destaca produtos com estoque baixo ou zerado
        st.dataframe(df.style.highlight_between(left=0, right=0, color='#ffcccc', subset=['QTD']), use_container_width=True)

    # --- ABA 2: REGISTRO DE VENDA ---
    with tab2:
        st.subheader("Baixa de Produto e Histórico")
        
        with st.form("form_venda"):
            col1, col2 = st.columns(2)
            
            with col1:
                produto_sel = st.selectbox("Selecione o Produto", df['PRODUTO'].tolist())
                qtd_venda = st.number_input("Quantidade Vendida", min_value=1, value=1)
                cliente = st.text_input("Nome do Cliente").upper()
            
            with col2:
                valor_pago = st.number_input("Valor Total (R$)", min_value=0.0, format="%.2f")
                metodo = st.selectbox("Método de Pagamento", ["PIX", "CARTÃO"])
                confirmar = st.form_submit_button("CONFIRMAR PAGAMENTO E ABATER ESTOQUE")

        if confirmar:
            # Lógica de atualização
            idx = df[df['PRODUTO'] == produto_sel].index[0]
            estoque_antigo = df.at[idx, 'QTD']
            
            if estoque_antigo < qtd_venda:
                st.warning(f"Atenção: Estoque atual ({estoque_antigo}) é menor que a venda!")
            
            # Atualiza DataFrame
            df.at[idx, 'QTD'] = estoque_antigo - qtd_venda
            
            # Registro de Log
            venda_log = {
                'DATA': datetime.now().strftime('%d/%m/%Y %H:%M'),
                'CLIENTE': cliente,
                'PRODUTO': produto_sel,
                'QTD': qtd_venda,
                'VALOR_TOTAL': valor_pago,
                'FORMA_PGTO': metodo
            }

            try:
                with pd.ExcelWriter(caminho_planilha, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
                    df.to_excel(writer, sheet_name=writer.book.sheetnames[0], index=False)
                    
                    try:
                        df_pedidos = pd.read_excel(caminho_planilha, sheet_name='PEDIDOS_PAGOS')
                        df_final_pedidos = pd.concat([df_pedidos, pd.DataFrame([venda_log])], ignore_index=True)
                    except:
                        df_final_pedidos = pd.DataFrame([venda_log])
                    
                    df_final_pedidos.to_excel(writer, sheet_name='PEDIDOS_PAGOS', index=False)
                
                st.success(f"✅ Venda de {produto_sel} registrada! Novo estoque: {df.at[idx, 'QTD']}")
                st.balloons()
                
            except Exception as e:
                st.error(f"Erro ao salvar: {e}")

    # Botão para Regerar o Site
    st.sidebar.markdown("---")
    if st.sidebar.button("🚀 ATUALIZAR SITE (Gerar index.html)"):
        try:
            from seu_arquivo_principal import gerar_site_vendas_completo
            gerar_site_vendas_completo()
            st.sidebar.success("Site index.html atualizado com sucesso!")
        except Exception as e:
            st.sidebar.error(f"Erro ao gerar site: {e}")

if __name__ == "__main__":
    main()