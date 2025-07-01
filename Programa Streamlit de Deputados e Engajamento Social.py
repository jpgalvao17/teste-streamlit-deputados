import altair as alt
import pandas as pd
import streamlit as st

# ----------------------
# Função para carregar dados dos deputados
# ----------------------
def load_data(uploaded_file=None):
    try:
        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_csv('engajamentodeputados.csv')

        # Ajuste de colunas esperadas
        for col in ['nome_deputado', 'partido', 'uf', 'seguidores_twitter', 'curtidas_instagram', 'visualizacoes_tiktok']:
            if col not in df.columns:
                df[col] = 0

        df['seguidores_twitter'] = df['seguidores_twitter'].fillna(0).astype(int)
        df['curtidas_instagram'] = df['curtidas_instagram'].fillna(0).astype(int)
        df['visualizacoes_tiktok'] = df['visualizacoes_tiktok'].fillna(0).astype(int)

        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados dos deputados: {e}")
        return pd.DataFrame()

# ----------------------
# Função para carregar os posts
# ----------------------
def load_posts(uploaded_posts=None):
    try:
        if uploaded_posts is not None:
            df_posts = pd.read_csv(uploaded_posts, delimiter=';')
        else:
            df_posts = pd.read_csv('engajamentodeputados.csv', delimiter=';')

        df_posts['Date'] = pd.to_datetime(df_posts['Date'], errors='coerce')
        df_posts['Engajamento total'] = pd.to_numeric(df_posts['Engajamento total'], errors='coerce').fillna(0).astype(int)
        return df_posts
    except Exception as e:
        st.error(f"Erro ao carregar dados dos posts: {e}")
        return pd.DataFrame()

# ----------------------
# Gráfico de barras com Altair
# ----------------------
def create_bar_chart(data, x_col, y_col, title):
    return alt.Chart(data).mark_bar().encode(
        x=alt.X(x_col, title=title.split("por ")[1] if "por " in title else x_col),
        y=alt.Y(y_col, sort='-x'),
        tooltip=[y_col, x_col]
    ).properties(title=title).interactive()

# ----------------------
# Função principal do app
# ----------------------
def main():
    st.set_page_config(page_title="📊 Análise de Deputados e Engajamento", layout="wide")
    st.title("📊 Análise de Deputados e Engajamento + Posts")

    # Uploads
    st.sidebar.header("🔽 Upload de Arquivos (opcional)")
    uploaded_file = st.sidebar.file_uploader("📂 CSV de Deputados", type="csv")
    uploaded_posts = st.sidebar.file_uploader("📂 CSV de Posts", type="csv")

    # Carregar dados
    with st.spinner("Carregando dados..."):
        df = load_data(uploaded_file)
        df_posts = load_posts(uploaded_posts)

    if df.empty:
        st.warning("Nenhum dado de deputado carregado.")
        return

    # Filtros
    st.sidebar.header("📋 Filtros")
    ufs = ["Todas"] + sorted(df['uf'].dropna().unique().tolist())
    partidos = ["Todos"] + sorted(df['partido'].dropna().unique().tolist())

    selected_uf = st.sidebar.selectbox("UF:", ufs)
    selected_partido = st.sidebar.selectbox("Partido:", partidos)
    search_name = st.sidebar.text_input("🔍 Nome do Deputado:")

    filtered_df = df.copy()
    if selected_uf != "Todas":
        filtered_df = filtered_df[filtered_df['uf'] == selected_uf]
    if selected_partido != "Todos":
        filtered_df = filtered_df[filtered_df['partido'] == selected_partido]
    if search_name:
        filtered_df = filtered_df[filtered_df['nome_deputado'].str.contains(search_name, case=False, na=False)]

    # Tabela Deputados
    st.subheader(f"📋 Lista de Deputados ({len(filtered_df)} encontrados)")
    if not filtered_df.empty:
        cols = ['nome_deputado', 'partido', 'uf', 'seguidores_twitter', 'curtidas_instagram', 'visualizacoes_tiktok']
        st.dataframe(
            filtered_df[cols].style.format({
                'seguidores_twitter': '{:,.0f}',
                'curtidas_instagram': '{:,.0f}',
                'visualizacoes_tiktok': '{:,.0f}'
            }).highlight_max(subset=cols[3:], color='#d3f9d8')
        )

        csv = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Baixar dados filtrados", data=csv, file_name="deputados_filtrados.csv", mime="text/csv")
    else:
        st.info("Nenhum resultado com os filtros aplicados.")

    # Gráficos Engajamento
    st.subheader("📈 Visualização de Engajamento por Plataforma")
    top_n = st.slider("Top N Deputados:", 5, 20, 10)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.write("### Twitter")
        top = filtered_df.nlargest(top_n, 'seguidores_twitter')
        if not top.empty:
            st.altair_chart(create_bar_chart(top, 'seguidores_twitter', 'nome_deputado', f"Top {top_n} por Seguidores no Twitter"), use_container_width=True)
    with col2:
        st.write("### Instagram")
        top = filtered_df.nlargest(top_n, 'curtidas_instagram')
        if not top.empty:
            st.altair_chart(create_bar_chart(top, 'curtidas_instagram', 'nome_deputado', f"Top {top_n} por Curtidas no Instagram"), use_container_width=True)
    with col3:
        st.write("### TikTok")
        top = filtered_df.nlargest(top_n, 'visualizacoes_tiktok')
        if not top.empty:
            st.altair_chart(create_bar_chart(top, 'visualizacoes_tiktok', 'nome_deputado', f"Top {top_n} por Visualizações no TikTok"), use_container_width=True)

    # Análise de Posts
    if not df_posts.empty:
        st.markdown("---")
        st.header("📱 Top N Posts por Engajamento")

        redes = ["Todas"] + sorted(df_posts['Top 5 values of Network.keyword'].dropna().unique().tolist())
        rede_sel = st.selectbox("Filtrar por Rede Social:", redes)

        posts_filtrados = df_posts.copy()
        if rede_sel != "Todas":
            posts_filtrados = posts_filtrados[posts_filtrados['Top 5 values of Network.keyword'] == rede_sel]

        top_post_n = st.slider("Número de Posts no Gráfico:", 5, 30, 10)
        top_posts = posts_filtrados.nlargest(top_post_n, 'Engajamento total')

        if not top_posts.empty:
            chart = alt.Chart(top_posts).mark_bar().encode(
                x=alt.X('Engajamento total', title='Engajamento Total'),
                y=alt.Y('Parlamentar', sort='-x'),
                color='Top 5 values of Network.keyword',
                tooltip=[
                    'Parlamentar',
                    'Engajamento total',
                    'Top 5 values of Network.keyword',
                    'Top 50 posts',
                    'Message'
                ]
            ).properties(title=f"Top {top_post_n} Posts por Engajamento").interactive()

            st.altair_chart(chart, use_container_width=True)
            st.dataframe(top_posts[['Date', 'Parlamentar', 'Top 5 values of Network.keyword', 'Engajamento total', 'Top 50 posts', 'Message']])
        else:
            st.info("Nenhum post encontrado.")

# Run
if __name__ == '__main__':
    main()
