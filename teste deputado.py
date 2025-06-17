import streamlit as st
import requests

st.title("Buscar Deputados Federais")

ufs = [''] + ['AC', 'AL', 'AM', 'AP', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 'MG',
              'MS', 'MT', 'PA', 'PB', 'PE', 'PI', 'PR', 'RJ', 'RN', 'RO', 'RR',
              'RS', 'SC', 'SE', 'SP', 'TO']

partidos = [''] + ['PT', 'PL', 'PSOL', 'PP', 'MDB', 'PSDB', 'PSD', 'Republicanos', 'União']

nome = st.text_input("Nome do Deputado (opcional):")
uf = st.selectbox("UF (Estado)", ufs)
partido = st.selectbox("Partido", partidos)

if st.button("Buscar"):
    base_url = "https://dadosabertos.camara.leg.br/api/v2/deputados?"
    params = []

    if nome:
        params.append(f"nome={nome}")
    if uf:
        params.append(f"siglaUf={uf}")
    if partido:
        params.append(f"siglaPartido={partido}")

    url = base_url + "&".join(params)

    response = requests.get(url)
    if response.status_code == 200:
        dados = response.json().get("dados", [])
        if dados:
            for deputado in dados:
                st.markdown(f"### {deputado['nome']}")
                st.image(deputado['urlFoto'], width=100)
                st.write(f"- Partido: {deputado['siglaPartido']}")
                st.write(f"- UF: {deputado['siglaUf']}")
                st.markdown("---")
        else:
            st.warning("Nenhum deputado encontrado com os filtros selecionados.")
    else:
        st.error("Erro ao consultar a API da Câmara.")
