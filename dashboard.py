import streamlit as st
import pandas as pd
import os
import unicodedata

# Configuração da página web
st.set_page_config(page_title="GMA Locações 2026", layout="wide")

def normalizar_coluna(col):
    """Remove acentos e espaços para garantir que o código encontre a coluna"""
    nfkd = unicodedata.normalize('NFKD', str(col))
    return "".join([c for c in nfkd if not unicodedata.combining(c)]).strip().upper().replace("/", "_")

def carregar_dados():
    arquivo = "dados_locacao.xlsx"
    if not os.path.exists(arquivo):
        return None
    try:
        df = pd.read_excel(arquivo)
        # Padroniza os nomes das colunas para evitar o erro de KeyError
        df.columns = [normalizar_coluna(c) for c in df.columns]
        return df
    except Exception as e:
        st.error(f"Erro ao ler o arquivo Excel: {e}")
        return None

st.title("📊 Painel de Consulta de Locação GMA")
st.markdown("---")

df = carregar_dados()

if df is not None:
    # --- ÁREA DE FILTROS ---
    col1, col2, col3 = st.columns(3)
    
    with col1:
        categorias = sorted(df['CATEGORIA'].unique().astype(str))
        cat_sel = st.selectbox("Selecione o Equipamento", categorias)
    
    with col2:
        periodos = sorted(df['PERIODO'].unique().astype(str))
        per_sel = st.selectbox("Selecione o Período", periodos)
        
    with col3:
        busca = st.text_input("Filtrar por Modelo ou Potência").strip().upper()

    # --- LÓGICA DE FILTRAGEM ---
    # Filtra por Categoria e Período
    dados = df[(df['CATEGORIA'] == cat_sel) & (df['PERIODO'] == per_sel)]
    
    if busca:
        # Busca nas colunas normalizadas: POTENCIA_VAZAO e MODELOS
        dados = dados[
            (dados['POTENCIA_VAZAO'].astype(str).str.upper().str.contains(busca, na=False)) | 
            (dados['MODELOS'].astype(str).str.upper().str.contains(busca, na=False))
        ]

    # --- EXIBIÇÃO DOS RESULTADOS ---
    if not dados.empty:
        for _, row in dados.iterrows():
            with st.container():
                c1, c2, c3 = st.columns([2, 1, 1])
                
                with c1:
                    st.subheader(f"{row['MODELOS']}")
                    st.write(f"**Vazão/Potência:** {row['POTENCIA_VAZAO']}")
                
                with c2:
                    # Mapeia '8 HORAS/DIA' que vira '8 HORAS_DIA' após normalização
                    val8h = row.get('8 HORAS_DIA', 0)
                    st.metric("Locação 8h", f"R$ {val8h:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                
                with c3:
                    # Mapeia '24 HORAS/DIA' que vira '24 HORAS_DIA' após normalização
                    val24h = row.get('24 HORAS_DIA', 0)
                    st.metric("Locação 24h", f"R$ {val24h:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                st.divider()
    else:
        st.info("Nenhum item encontrado com estes filtros.")
else:
    st.error("Arquivo 'dados_locacao.xlsx' não encontrado no servidor.")