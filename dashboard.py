import streamlit as st
import pandas as pd
import os
import unicodedata

# Configuração da página Web
st.set_page_config(page_title="GMA Locações 2026", layout="wide")

def normalizar_coluna(col):
    """Remove acentos, espaços extras e padroniza para maiúsculo"""
    nfkd = unicodedata.normalize('NFKD', str(col))
    col_limpa = "".join([c for c in nfkd if not unicodedata.combining(c)])
    return col_limpa.strip().upper().replace("/", "_")

def carregar_dados():
    arquivo = "dados_locacao.xlsx"
    if not os.path.exists(arquivo):
        return None
    try:
        df = pd.read_excel(arquivo)
        # Limpeza profunda de colunas para evitar KeyError
        df.columns = [normalizar_coluna(c) for c in df.columns]
        return df
    except Exception as e:
        st.error(f"Erro ao ler o Excel: {e}")
        return None

st.title("📊 Painel de Consulta de Locação GMA")
df = carregar_dados()

if df is not None:
    # FILTROS LATERAIS OU TOPO
    col1, col2, col3 = st.columns(3)
    
    with col1:
        cat_opcoes = sorted(df['CATEGORIA'].unique().astype(str))
        categoria_sel = st.selectbox("Selecione o Equipamento", cat_opcoes)
    
    with col2:
        per_opcoes = sorted(df['PERIODO'].unique().astype(str))
        periodo_sel = st.selectbox("Selecione o Período", per_opcoes)
        
    with col3:
        busca = st.text_input("Filtrar por Modelo ou Potência").strip().upper()

    # Mapeamento dinâmico das suas colunas de preço
    col_8h = "8_HORAS_DIA" 
    col_24h = "24_HORAS_DIA"

    # Aplicação dos Filtros
    dados = df[(df['CATEGORIA'] == categoria_sel) & (df['PERIODO'] == periodo_sel)]
    
    if busca:
        # Busca na coluna POTENCIA_VAZAO normalizada
        dados = dados[
            (dados['POTENCIA_VAZAO'].astype(str).str.upper().str.contains(busca, na=False)) | 
            (dados['MODELOS'].astype(str).str.upper().str.contains(busca, na=False))
        ]

    st.markdown("---")

    if not dados.empty:
        for _, row in dados.iterrows():
            with st.container():
                c1, c2, c3 = st.columns([2, 1, 1])
                c1.subheader(f"{row['MODELOS']}")
                c1.write(f"**Vazão/Potência:** {row['POTENCIA_VAZAO']}")
                
                # Exibição dos valores formatados
                val8h = row[col_8h] if col_8h in row else 0
                val24h = row[col_24h] if col_24h in row else 0
                
                c2.metric("Locação 8h", f"R$ {val8h:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                c3.metric("Locação 24h", f"R$ {val24h:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                st.divider()
    else:
        st.info("Nenhum item encontrado com esses filtros.")
else:
    st.error("Arquivo 'dados_locacao.xlsx' não encontrado.")