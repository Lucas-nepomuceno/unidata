import pandas as pd
import numpy as np
import streamlit as st
import altair as alt


#-------------------------------

st.set_page_config(page_title='Unidata', layout='wide')
st.markdown("""
<style>
.stButton > button {
    background-color: #0eae37;
    color: white;
    border: None;
    border-radius: 5px;
    padding: 10px 20px;
    cursor: pointer;
    font-size: 16px;
}
.stButton > button:hover {
    background-color: #0a8e2a; 
    color: white
}
.stButton > button:focus {
    background-color: #0a8e2a; 
    color: white
}
</style>
""", unsafe_allow_html=True)


# Initialize the session state
if 'page' not in st.session_state:
    st.session_state.page = 'home'  # Default page


#-------------------------------
df = None
# Load the data
with st.sidebar.header("Faça aqui o Upload da Base de Dados da Unipar"):
    uploaded_file = st.sidebar.file_uploader("Base de Sinistros enviada pelo Inteli")
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)

st.title('UniData')
st.markdown('&ensp; Esse projeto visa auxiliar a Unipar na tomada de decisões para desenvolver programas de saúde mais eficazes e eficientes, proporcionando melhorias significativas no bem-estar dos colaboradores a longo prazo.')

if df is not None:
    df['categoria'] = df['categoria'].str.lower()
    df['categoria'] = df['categoria'].str.title()
    df['elegibilidade_sinistro'] = df['elegibilidade_sinistro'].str.lower()
    df['elegibilidade_sinistro'] = df['elegibilidade_sinistro'].str.title()

    if st.session_state.page == "home":

        st.header('Impressões Iniciais')
        st.markdown('&ensp; Uma das primeiras perguntas a se fazer quando tratamos da base da Unipar é entender algumas características básicas, como tamanho, máximo e mínimo de algumas colunas... Estas estão abaixo:')
        st.write('')

        # Your summary metrics
        st.markdown(f"""
        <ul>
            <li><strong>Quantidade de Sinistros na base:</strong> 
            <span style="color: #0eae37;">{df.shape[0]}</span></li>
            <li><strong>Quantidade de Pessoas que ativaram o sinistro:</strong> 
            <span style="color: #0eae37;">{df['segurado'].nunique()}</span></li>
            <li><strong>Quantidade Média de Sinistro por Pessoa:</strong> 
            <span style="color: #0eae37;">{round(df.shape[0]/df['segurado'].nunique(), 2)}</span></li>
            <li><strong>Máximo Valor Pago: </strong> 
            <span style="color: #0eae37;">R${round(df['valor_pago_sinistro'].max(), 2)}</span></li>
            <li><strong>Prestador Mais Frequente:</strong> 
            <span style="color: #0eae37;">{df['nome_prestador_sinistro'].mode()[0]}</span></li>
        </ul>
        """, unsafe_allow_html=True)

        st.markdown('<br>', unsafe_allow_html=True)

        st.header('Visualizando Distribuições')
        st.markdown('&ensp; Após compreender o básico do que era a base de dados, partimos para algumas distribuições preliminares <br> <br>', unsafe_allow_html=True)

        # Gráfico Sexo
        quantidade_sexo = df['sexo_colaborador_sinistro'].value_counts()
        data_sexo = pd.DataFrame({
            'Sexo': ['Feminino', 'Masculino'],
            'Quantidade de Ocorrências': quantidade_sexo.values
        })

        chart_sexo = alt.Chart(data_sexo).mark_arc().encode(
            theta=alt.Theta(field="Quantidade de Ocorrências", type="quantitative"),
            color=alt.Color('Sexo:N', scale=alt.Scale(domain=['Feminino', 'Masculino'], 
                                                      range=['#008A26', '#00FF3C'])),
            tooltip=['Sexo', 'Quantidade de Ocorrências']
        ).properties(
            title='Distribuição de Sexo por Sinistro'
        )
        #00FF3C

        # Gráfico Elegibilidade
        quantidade_elegibilidade = df['elegibilidade_sinistro'].value_counts()
        data_elegibilidade = pd.DataFrame({
            'Elegibilidade': quantidade_elegibilidade.index,
            'Quantidade de Ocorrências': quantidade_elegibilidade.values
        })

        chart_elegibilidade = alt.Chart(data_elegibilidade).mark_arc().encode(
            theta=alt.Theta(field="Quantidade de Ocorrências", type="quantitative"),
            color=alt.Color('Elegibilidade:N', scale=alt.Scale(domain=['Dependente', 'Titular'], 
                                                               range=['#006343', 'lightgreen'])),
            tooltip=['Elegibilidade', 'Quantidade de Ocorrências']
        ).properties(
            title='Distribuição de Elegibilidade por Sinistro'
        )

        # Cria duas colunas
        col1, col2 = st.columns(2)

        # Coloca cada gráfico em uma coluna
        with col1:
            st.altair_chart(chart_sexo, use_container_width=True)

        with col2:
            st.altair_chart(chart_elegibilidade, use_container_width=True)

        # Gráfico Sexo por faixa etária
        grouped = df.groupby(['faixa_etaria_colaborador_sinistro', 'sexo_colaborador_sinistro']).size().reset_index(name='count')
        grouped['sexo_colaborador_sinistro'] = grouped['sexo_colaborador_sinistro'].map({'M': 'Masculino', 'F': 'Feminino'})

        chart_faixa_etaria_sexo = alt.Chart(grouped).mark_bar().encode(
            x=alt.X('faixa_etaria_colaborador_sinistro:O', title='Faixa Etária'),
            y=alt.Y('count:Q', title='Número de Ocorrências'),
            color=alt.Color('sexo_colaborador_sinistro:N', title='Gênero', scale=alt.Scale(
                                domain=['Masculino', 'Feminino'],
                                range=['#00FF3C', '#008A26']
                            )),
            xOffset='sexo_colaborador_sinistro:N',  # Desloca as barras pelo gênero
            tooltip=['faixa_etaria_colaborador_sinistro', 'sexo_colaborador_sinistro', 'count']
        ).properties(
            title='Distribuição por Faixa Etária e Gênero'
        )

        st.markdown('<br><br>', unsafe_allow_html=True)
        st.altair_chart(chart_faixa_etaria_sexo, use_container_width=True)
        st.write('<br><br>', unsafe_allow_html=True)

        # Gráfico ocorrências por mês
        df['data_ocorrencia_sinistro'] = pd.to_datetime(df['data_ocorrencia_sinistro'], format='%d/%m/%Y')
        df['month'] = df['data_ocorrencia_sinistro'].dt.to_period('M')
        monthly_counts = df.groupby('month').size().reset_index(name='count')
        monthly_counts['month'] = monthly_counts['month'].dt.to_timestamp()

        line_chart_mes = alt.Chart(monthly_counts).mark_line(point=True).encode(
            x=alt.X('month:T', title='Mês/Ano', axis=alt.Axis(format='%b %Y')),  # Formatação correta do eixo X
            y=alt.Y('count:Q', title='Número de Ocorrências'), 
            tooltip=[alt.Tooltip('month:T', title='Mês/Ano', format='%b %Y'), alt.Tooltip('count:Q',    title='Número de Ocorrências')],
            color=alt.value('#0eae37')
        ).properties(
            title='Número de Ocorrências por Mês'
        )

        st.altair_chart(line_chart_mes, use_container_width=True)
        st.markdown('<br><br>', unsafe_allow_html=True)

        #Gráfico top 3 categorias mais usadas por titulares
        categorias_mais_usadas_titulares = df.loc[df['elegibilidade_sinistro'] == 'Titular', 'categoria'].value_counts()[:3]

        data_categoria_titulares = pd.DataFrame({
            'Categoria': categorias_mais_usadas_titulares.index,
            'Quantidade de Ocorrências': categorias_mais_usadas_titulares.values
        })
        chart_categoria_titulares = alt.Chart(data_categoria_titulares).mark_bar().encode(
            x='Quantidade de Ocorrências',
            y='Categoria',
            color=alt.value('lightgreen') 
        ).properties(
            title='Top 3 Categorias mais utilizadas por Titulares'
        )

        #Gráfico top 3 categorias mais usadas por dependentes
        categorias_mais_usadas_dependentes = df.loc[df['elegibilidade_sinistro'] == 'Dependente', 'categoria'].value_counts()[:3]
        data_categoria_dependentes = pd.DataFrame({
            'Categoria': categorias_mais_usadas_dependentes.index,
            'Quantidade de Ocorrências': categorias_mais_usadas_dependentes.values
        })
        chart_categoria_dependentes = alt.Chart(data_categoria_dependentes).mark_bar().encode(
            x='Quantidade de Ocorrências',
            y='Categoria',
            color=alt.value('#006343') 
        ).properties(
            title='Top 3 Categorias mais utilizadas por Dependentes'
        )

        #Gráfico top 3 prestadores mais usadas por titulares
        prestadores_mais_usados_titulares = df.loc[df['elegibilidade_sinistro'] == 'Titular', 'nome_prestador_sinistro'].value_counts()[:3]

        data_prestador_titulares = pd.DataFrame({
            'Prestador': prestadores_mais_usados_titulares.index,
            'Quantidade de Ocorrências': prestadores_mais_usados_titulares.values
        })
        chart_prestador_titulares = alt.Chart(data_prestador_titulares).mark_bar().encode(
            x='Quantidade de Ocorrências',
            y='Prestador',
            color=alt.value('lightgreen') 
        ).properties(
            title='Top 3 Prestadores mais utilizados por Titulares'
        )

        #Gráfico top 3 categorias mais usadas por dependentes
        prestadores_mais_usados_dependentes = df.loc[df['elegibilidade_sinistro'] == 'Dependente', 'nome_prestador_sinistro'].value_counts()[:3]
        data_prestador_dependentes = pd.DataFrame({
            'Prestador': prestadores_mais_usados_dependentes.index,
            'Quantidade de Ocorrências': prestadores_mais_usados_dependentes.values
        })
        chart_prestador_dependentes = alt.Chart(data_prestador_dependentes).mark_bar().encode(
            x='Quantidade de Ocorrências',
            y='Prestador',
            color=alt.value('#006343') 
        ).properties(
            title='Top 3 Prestadores mais utilizadas por Dependentes'
        )


        # Create two columns
        col3, col4 = st.columns(2)

        # Place the charts in each column
        with col3:
            st.altair_chart(chart_categoria_titulares, use_container_width=True)
            st.markdown('<br>', unsafe_allow_html=True)
            st.altair_chart(chart_prestador_titulares, use_container_width=True)

        with col4:
            st.altair_chart(chart_categoria_dependentes, use_container_width=True)
            st.markdown('<br>', unsafe_allow_html=True)
            st.altair_chart(chart_prestador_dependentes, use_container_width=True)

        st.markdown('<br><br>', unsafe_allow_html=True)
        st.header('Série Temporal das Categorias')
        st.markdown('&ensp; Entre todas as colunas, uma se destaca: a categoria. Esta se relaciona à que categoria de serviço foi utilizada no sinistro. Abaixo é possível visualizar o uso dessas categorias no tempo. Para tanto, basta escolher se deseja ver de titulares, dependentes ou ambos e qual categoria se busca.')

        st.markdown('<br>', unsafe_allow_html=True)

        df['data_ocorrencia_sinistro'] = pd.to_datetime(df['data_ocorrencia_sinistro'], format='%d/%m/%Y')
        df['month'] = df['data_ocorrencia_sinistro'].dt.to_period('M')

        # Seleção de elegibilidade
        elegibilidade_selecionada = st.multiselect("Escolha a Elegibilidade", ['Titular', 'Dependente'], default=['Titular'])

        if elegibilidade_selecionada:
            # Seleção da categoria
            categoria_selecionada = st.selectbox("Selecione uma Categoria", list(df['categoria'].unique())[::-1])

            # Filtrando os dados
            df_filtrado = df[(df['categoria'] == categoria_selecionada) & (df['elegibilidade_sinistro'].isin(elegibilidade_selecionada))]

            if not df_filtrado.empty:
                # Agrupando os dados e contando as ocorrências por mês
                monthly_counts = df_filtrado.groupby('month').size().reset_index(name='count')
                monthly_counts['month'] = monthly_counts['month'].dt.to_timestamp()

                # Gerando uma lista de meses completa para garantir que o eixo X seja constante
                min_month = df['data_ocorrencia_sinistro'].min().to_period('M').to_timestamp()
                max_month = df['data_ocorrencia_sinistro'].max().to_period('M').to_timestamp()
                all_months = pd.date_range(start=min_month, end=max_month, freq='MS')  # 'MS' para o início de cada mês

                # Criando um DataFrame com todos os meses
                all_months_df = pd.DataFrame({'month': all_months})

                # Fazendo um merge para garantir que todos os meses estejam presentes no gráfico
                full_monthly_counts = pd.merge(all_months_df, monthly_counts, on='month', how='left').fillna(0)

                # Criação do gráfico com a formatação do eixo X e tooltip
                line_chart_mes = alt.Chart(full_monthly_counts).mark_line(point=True).encode(
                    x=alt.X('month:T', title='Mês/Ano', axis=alt.Axis(format='%b %Y')),  # Formatação do eixo X
                    y=alt.Y('count:Q', title='Número de Ocorrências'), 
                    tooltip=[alt.Tooltip('month:T', title='Mês/Ano', format='%b %Y'), alt.Tooltip('count:Q', title='Número de Ocorrências')],
                    color=alt.value('#0eae37')
                ).properties(
                    title=f'Número de Ocorrências de {categoria_selecionada} por Mês'
                )

                # Exibindo o gráfico
                st.altair_chart(line_chart_mes, use_container_width=True)
                st.markdown('<br>', unsafe_allow_html=True)
            else:
                st.markdown('<br>', unsafe_allow_html=True)
                st.markdown('Não há dados disponíveis para estes parâmetros')
                st.markdown('<br>', unsafe_allow_html=True)

        footer = """
        <style>
        .footer {
            a:link {
                color: black;
            }

            /* visited link */
            a:visited {
              color: black;
            }

            /* mouse over link */
            a:hover {
              color: lightgreen;
            }

            /* selected link */
            a:active {
              color: lightgreen;
            }
        }

        </style>
        <div class="footer">
            <a href="https://drive.google.com/file/d/1Q1OVR2rYqxuyL6j1HJb9wKE7rltpYvGp/view?usp=drive_link" target="_blank">Acesse aqui nossa Política de privacidade</a>
        </div>
        """

        # Navigation button
        if st.button("Veja Nossas Análises"):
            st.session_state.page = "analises"

        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown(footer, unsafe_allow_html=True)

    elif st.session_state.page == "analises":
        st.title("Nossas Análises")

        st.write("&ensp;O projeto de desenvolvimento do modelo preditivo para traçar perfis de uso do convênio médico da Unipar demonstrou a importância da análise de dados na compreensão dos padrões de comportamento dos colaboradores em relação aos serviços de saúde. A metodologia adotada incluiu a aplicação de diferentes técnicas de clusterização, como K-means, DBSCAN, Gaussian Mixture Model (GMM), Affinity Propagation e Spectral Clustering. Essa abordagem permitiu uma análise abrangente das variáveis relacionadas ao uso do convênio, como sexo, faixa etária, tipos de procedimentos e valores pagos, contribuindo para uma segmentação mais precisa dos perfis de saúde.<br>", unsafe_allow_html=True)

        st.write("&ensp;Não obstante o uso de diversas técnicas de agrupamento para a visualização de perfis nos dados, apenas uma delas rendeu resultados positivos. Esses resultados são resumidos abaixo.<br>", unsafe_allow_html=True)

        st.header("Resultados Preditivos")

        st.write("&ensp;A máquina, usando-se de técnicas matemáticas, é capaz de agrupar perfis com base em sua similaridade de comportamento por vezes ocultos à reflexão humana. Um dos métodos de se aplicar isso é baseando-se no agrupamento gerado pelo Gaussian Mixture Model. Este algoritmo de agrupamento encontrou nos dados os seguintes perfis:<br>", unsafe_allow_html=True)

        st.write("- Homens jovens de 0 a 18 anos;", unsafe_allow_html=True)
        st.write("- Homens mais velhos, prioritariamente de 59 anos ou mais;", unsafe_allow_html=True)
        st.write("- Mulheres entre 34 e 43 ou de 59 ou mais.", unsafe_allow_html=True)

        st.write("&ensp;Segundo os resultados do GMM, esses três grupos apresentam comportamentos distintos entre si à maneira como utilizam o plano de saúde. Vejamos abaixo algumas características desses três grupos.", unsafe_allow_html=True)

        st.write("<br><br>", unsafe_allow_html=True)


        df_clusters = df.loc[df['cluster'].isin([1,7,8])]
        quantidade_cluster = df_clusters['cluster'].value_counts()
        data_quantidade_cluster = pd.DataFrame({
            'cluster': ['3', '2', '1'],
            'quantidade': quantidade_cluster.values
        })
        chart_quantidade_cluster = alt.Chart(data_quantidade_cluster).mark_bar().encode(
            x=alt.X('cluster:O', title='Perfil'),
            y=alt.Y('quantidade:Q', title='Número de Ocorrências'),
            color=alt.Color('cluster:N', title='Perfil', scale=alt.Scale(
                                domain=['1', '2', '3'],
                                range=['#00FF3C', '#00B432', '#006343']
                            )),
        ).properties(
            title='Distribuição de Ocorrências por Perfil'
        )

        quantidade_cluster_segurado = df_clusters.drop_duplicates(subset=['segurado'], keep=
        'first')['cluster'].value_counts()
        data_quantidade_cluster_segurado = pd.DataFrame({
            'cluster': ['2', '1', '3'],
            'quantidade': quantidade_cluster_segurado.values
        })
        chart_quantidade_cluster_segurado = alt.Chart(data_quantidade_cluster_segurado).mark_bar().encode(
            x=alt.X('cluster:O', title='Perfil'),
            y=alt.Y('quantidade:Q', title='Número de Ocorrências'),
            color=alt.Color('cluster:N', title='Perfil', scale=alt.Scale(
                                domain=['1', '2', '3'],
                                range=['#00FF3C', '#00B432', '#006343']
                            )),
        ).properties(
            title='Distribuição de Segurados por Perfil'
        )

        col5, col6 = st.columns(2)

        with col5:
            st.altair_chart(chart_quantidade_cluster, use_container_width=True)
        with col6:
            st.altair_chart(chart_quantidade_cluster_segurado, use_container_width=True)

        st.write("<br>", unsafe_allow_html=True)

        st.write("&ensp;Pelos gráficos acima, verifica-se que os três perfis comprimem poucas ocorrências do total do banco de dados. Mesmo o mais proeminente deles (mulheres entre 34 e 43 ou de 59 ou mais) não chega a 10000 ocorrências. Deve-se notar, porém, que comprimem uma quantidade significativa de segurados: o comportamento de, pelo menos, 250 pessoas em cada<br>", unsafe_allow_html=True)

        st.header('Comportamento por perfil')

        st.write("&ensp;O GMM conseguiu encontrar a relação entre esses perfis demográficos em nosso banco de dados. É necessário agora, investigar seus comportamentos.", unsafe_allow_html=True)

        st.write("&ensp;Primeiro, em relação à categoria do sinistro:<br><br>", unsafe_allow_html=True)

        # Agrupar por categoria e cluster, e contar as ocorrências
        grouped_cluster_categoria = df_clusters.groupby(['categoria', 'cluster']).size().reset_index    (name='count')

        # Para cada cluster, obter as três maiores categorias
        top_3_categorias_por_cluster = (
            grouped_cluster_categoria
            .sort_values(by=['cluster', 'count'], ascending=[True, False])
            .groupby('cluster')
            .head(3)
        )
        top_3_categorias_por_cluster['cluster'] = top_3_categorias_por_cluster['cluster'].replace({8: '1', 1: '2', 7: '3'})


        # Criar o gráfico de barras com Altair
        chart_categoria_cluster = alt.Chart(top_3_categorias_por_cluster).mark_bar().encode(
            x=alt.X('count:Q', title='Número de Ocorrências'),
            y=alt.Y('categoria:O', title='Categoria', sort='-x'),
            color=alt.Color('cluster:N', title='Perfil', scale=alt.Scale(
                domain=['1', '2', '3'],
                range=['#00FF3C', '#00B432', '#006343']
            )),
            yOffset='cluster:N',  # Desloca as barras pelo cluster
            tooltip=['cluster', 'categoria', 'count']
        ).properties(
            title='Distribuição de Categorias por Perfil'
        )

        # Exibir o gráfico com Streamlit
        st.altair_chart(chart_categoria_cluster, use_container_width=True)

        st.write("<br>", unsafe_allow_html=True)
        st.write("&ensp;Em relação à categoria, observa-se a predominância de categorias gerais. Os três perfis utilizam o plano de saúde, principalmente, para realizar exames clínicos e procedimentos diagnósticos. Entretanto, uma categoria que se destaca no perfil de jovens de 0 à 18 anos é o recorrente uso do plano para consultas.<br>", unsafe_allow_html=True)

        st.write("&ensp;Segundo, em relação ao prestador:<br><br>", unsafe_allow_html=True)

        # Agrupar por categoria e cluster, e contar as ocorrências
        grouped_cluster_prestador = df_clusters.groupby(['nome_prestador_sinistro', 'cluster']).size().reset_index    (name='count')

        # Para cada cluster, obter as três maiores categorias
        top_3_prestadores_por_cluster = (
            grouped_cluster_prestador
            .sort_values(by=['cluster', 'count'], ascending=[True, False])
            .groupby('cluster')
            .head(3)
        )
        top_3_prestadores_por_cluster['cluster'] = top_3_prestadores_por_cluster['cluster'].replace({8: '1', 1: '2', 7: '3'})

        # Criar o gráfico de barras com Altair
        chart_prestador_cluster = alt.Chart(top_3_prestadores_por_cluster).mark_bar().encode(
            x=alt.X('count:Q', title='Número de Ocorrências'),
            y=alt.Y('nome_prestador_sinistro:O', title='Prestador', sort='-x'),
            color=alt.Color('cluster:N', title='Perfil', scale=alt.Scale(
                domain=['1', '2', '3'],
                range=['#00FF3C', '#00B432', '#006343']
            )),
            yOffset='cluster:N',  # Desloca as barras pelo cluster
            tooltip=['cluster', 'nome_prestador_sinistro', 'count']
        ).properties(
            title='Distribuição de Prestadores por Perfil'
        )

        st.altair_chart(chart_prestador_cluster, use_container_width=True)
        st.write("<br>", unsafe_allow_html=True)

        st.write("&ensp;A partir da distribuição acima, observa-se que entre os três, o prestador predominante é o Instituto de Análises Clinícas de Santos, uma instituição voltada à medicina diagnóstica. Porém, evidencia-se à ida frequente de pessoas do perfil 1 ao Hospital Ribeirão Pires e de homens idosos no prestador Delboni Auriemo. <br>", unsafe_allow_html=True)

        st.write("&ensp;Por último, em relação ao valor pago:<br><br>", unsafe_allow_html=True)
        df_clusters_valor_pago = pd.DataFrame({
         'cluster': ['1', '2', '3'],
         'valor_pago': [
             df_clusters.loc[df_clusters['cluster'] == 8, 'valor_pago_sinistro'].mean(),
             df_clusters.loc[df_clusters['cluster'] == 1, 'valor_pago_sinistro'].mean(),
             df_clusters.loc[df_clusters['cluster'] == 7, 'valor_pago_sinistro'].mean()
        ]
        })
        # Criar o gráfico de barras com Altair
        chart_valor_cluster = alt.Chart(df_clusters_valor_pago).mark_bar().encode(
            x=alt.X('cluster:O', title='Perfil'),
            y=alt.Y('valor_pago:Q', title='Média de Valor Pago', sort='-x'),
            color=alt.Color('cluster:N', title='Perfil', scale=alt.Scale(
                domain=['1', '2', '3'],
                range=['#00FF3C', '#00B432', '#006343']
            )),
            tooltip=['cluster:O', 'valor_pago:Q']  # Garantir que a quantidade esteja no tooltip como úmero
        ).properties(
            title='Distribuição da Média do Valor Pago por Perfil'
        )
        st.altair_chart(chart_valor_cluster, use_container_width=True)

        st.write("<br>", unsafe_allow_html=True)

        st.write("&ensp;A partir da análise do gráfico acima, observa-se que em ordem decrescente os que pagam os maiores valores em média são: homens mais velhos, mulheres mais velhas e, só então jovens. <br>", unsafe_allow_html=True)

        st.header("Conclusões")

        st.write("&ensp; A análise aprofundada dos perfis identificados pelo modelo preditivo denota os diferentes comportamentos destes tipos de colaboradores Unipar. Os homens mais jovens, utilizam o plano principalmente para exames e consultas, sendo que a maior parte deles é feita no Instituto de Análises Clinícas de Santos, enquanto uma parte significativa o faz no Hospital Ribeirão Pires. Os homens mais velhos, por sua vez, são os que utilizam o plano de forma mais custosa, apesar de também o fazerem para medicina diagnóstica, desta vez, em um prestador de nome Delboni Auriemo. Algo a se notar é a sua sinistralidade mais frequente para exames endócrinos (medição de glicose e níveis hormonais). Essa característica também se repete em mulheres mais velhas, as quais se utilizam bastante do prestador A+ Medicina Diagnóstica. <br>", unsafe_allow_html=True)
        st.write("&ensp; A partir dessas conclusões, observa-se o potencial da análise preditiva para a segmentação de perfis na Unipar. Para maiores eludicações, porém, deve-se angariar mais dados, dentro do permitido pela lei, do comportamento de saúde dos funcionários, como, por exemplo: sua participação em campanhas de conscientização e prevenção na empresa. Caso contrário, as limitações impostas pela Lei Geral de Proteção de Dados não permitirão maiores insights acerca do comportamento de saúde dos funcionários. <br><br>", unsafe_allow_html=True)

        footer = """
        <style>
        .footer {
            a:link {
                color: white;
            }

            /* visited link */
            a:visited {
              color: white;
            }

            /* mouse over link */
            a:hover {
              color: lightgreen;
            }

            /* selected link */
            a:active {
              color: lightgreen;
            }
        }

        </style>
        <div class="footer">
            <a href="https://drive.google.com/file/d/1Q1OVR2rYqxuyL6j1HJb9wKE7rltpYvGp/view?usp=drive_link" target="_blank">Acesse aqui nossa Política de privacidade</a>
        </div>
        """

        if st.button("Voltar para Home"):
            st.session_state.page = "home"

        st.markdown("<br><br><br>", unsafe_allow_html=True)

        st.markdown(footer, unsafe_allow_html=True)

else:
    st.info('Aguardando o upload do banco de dados enviado pelo Inteli. É necessária a base de dados tratada para a veracidade das informações apresentadas.')


