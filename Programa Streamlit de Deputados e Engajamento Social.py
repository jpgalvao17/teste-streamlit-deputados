import streamlit as st
import pandas as pd
import altair as alt

# Função para carregar e combinar os dados
@st.cache_data
def load_data():
    try:
        df_deputados = pd.read_csv('deputados.csv')
        df_engajamento = pd.read_csv('engajamento_redes.csv')
        df_completo = pd.merge(df_deputados, df_engajamento, on='nome_deputado', how='left')

        # Renomeia para clareza
        df_completo.rename(columns={'seguidores_x': 'seguidores_twitter'}, inplace=True)

        # Garante colunas presentes e sem valores nulos
        for col in ['seguidores_twitter', 'curtidas_instagram', 'visualizacoes_tiktok']:
            if col not in df_completo.columns:
                df_completo[col] = 0
            df_completo[col] = df_completo[col].fillna(0).astype(int)

        return df_completo

    except FileNotFoundError:
        st.error("Erro: Arquivos 'deputados.csv' ou 'engajamento_redes.csv' não encontrados.")
        return pd.DataFrame()

# Função para criar gráfico de barras com Altair
def create_bar_chart(data, x_col, y_col, title):
    return alt.Chart(data).mark_bar().encode(
        x=alt.X(x_col, title=title.split("por ")[1], axis=alt.Axis(labelAngle=0)),
        y=alt.Y(y_col, title="Nome do Deputado", sort='-x'),
        tooltip=[y_col, x_col, 'partido', 'uf']
    ).properties(
        title=title
    ).interactive()

# Função principal do Streamlit
def main():
    st.set_page_config(page_title="Análise de Deputados e Engajamento", layout="wide")

    st.title("📊 Análise de Deputados e Engajamento em Redes Sociais")
    st.markdown("""
    Este aplicativo permite explorar dados de deputados federais e seu engajamento nas plataformas X (Twitter), Instagram e TikTok.
    Use os filtros na barra lateral para refinar sua busca.
    """)

    with st.spinner("Carregando dados..."):
        df = load_data()

    if df.empty:
        st.warning("Não foi possível carregar os dados. Verifique os arquivos CSV.")
        return

    # --- Filtros ---
    st.sidebar.header("Filtros de Dados")
    ufs = ["Todas"] + sorted(df['uf'].dropna().unique().tolist())
    partidos = ["Todos"] + sorted(df['partido'].dropna().unique().tolist())

    selected_uf = st.sidebar.selectbox("Filtrar por UF:", ufs)
    selected_partido = st.sidebar.selectbox("Filtrar por Partido:", partidos)
    search_name = st.sidebar.text_input("Pesquisar por Nome do Deputado:")

    filtered_df = df.copy()

    if selected_uf != "Todas":
        filtered_df = filtered_df[filtered_df['uf'] == selected_uf]
    if selected_partido != "Todos":
        filtered_df = filtered_df[filtered_df['partido'] == selected_partido]
    if search_name:
        filtered_df = filtered_df[filtered_df['nome_deputado'].str.contains(search_name, case=False, na=False)]

    # --- Tabela de Deputados ---
    st.subheader(f"Lista de Deputados ({len(filtered_df)} encontrados)")
    if not filtered_df.empty:
        cols_to_display = ['nome_deputado', 'partido', 'uf', 'seguidores_twitter', 'curtidas_instagram', 'visualizacoes_tiktok']

        st.dataframe(
            filtered_df[cols_to_display].style
            .format({
                'seguidores_twitter': '{:,.0f}',
                'curtidas_instagram': '{:,.0f}',
                'visualizacoes_tiktok': '{:,.0f}'
            })
            .highlight_max(subset=['seguidores_twitter', 'curtidas_instagram', 'visualizacoes_tiktok'], color='#d3f9d8')
        )

        # --- Botão de download dos dados filtrados ---
        csv = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Baixar dados filtrados", data=csv, file_name="dados_deputados_filtrados.csv", mime="text/csv")
    else:
        st.info("Nenhum deputado encontrado com os filtros selecionados.")
        return

    # --- Gráficos de Engajamento ---
    st.subheader("Visualizações de Engajamento por Plataforma")
    num_top_deputies = st.slider("Número de deputados para exibir nos gráficos de Top N:", 5, 20, 10)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.write(f"### Top {num_top_deputies} por Seguidores no X")
        top_x = filtered_df.nlargest(num_top_deputies, 'seguidores_twitter')
        if not top_x.empty:
            st.altair_chart(create_bar_chart(top_x, 'seguidores_twitter', 'nome_deputado', f"Top {num_top_deputies} por Seguidores no X"), use_container_width=True)

    with col2:
        st.write(f"### Top {num_top_deputies} por Curtidas no Instagram")
        top_instagram = filtered_df.nlargest(num_top_deputies, 'curtidas_instagram')
        if not top_instagram.empty:
            st.altair_chart(create_bar_chart(top_instagram, 'curtidas_instagram', 'nome_deputado', f"Top {num_top_deputies} por Curtidas no Instagram"), use_container_width=True)

    with col3:
        st.write(f"### Top {num_top_deputies} por Visualizações no TikTok")
        top_tiktok = filtered_df.nlargest(num_top_deputies, 'visualizacoes_tiktok')
        if not top_tiktok.empty:
            st.altair_chart(create_bar_chart(top_tiktok, 'visualizacoes_tiktok', 'nome_deputado', f"Top {num_top_deputies} por Visualizações no TikTok"), use_container_width=True)

# Ponto de entrada
if __name__ == '__main__':
    main()
