from typing import List

import pandas as pd
import numpy as np
import streamlit as st
import plotly_express as px
import plotly.figure_factory as ff


with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


@st.cache_data
def load_data() -> pd.DataFrame:
    bd = pd.read_excel('dados_selecionados.xlsx')
    return bd.drop(["Unnamed: 0", "indexador"], axis=1)


def clause(filter_res: dict) -> str:
    clause_list = list()
    for column in FILTER_LIST:
        if filter_res[column] != []:
            clause_list.append(f"`{column}` in {filter_res[column]}")

    clause_treated = str(clause_list) \
                         .replace('", "', ' & ')[1:-1] \
        .replace('[', '(') \
        .replace(']', ')')
    return clause_treated


def set_sidebar(
        bd: pd.DataFrame = None,
        filtered: pd.DataFrame = None) -> dict:
    if filtered is None:
        df = bd
    else:
        df = filtered

    filter_res = dict()
    for i, name in enumerate(FILTER_LIST):
        component = st.sidebar.multiselect(
            key=i,
            label=name.upper(),
            options=df[name].unique(),
            help=f"Escolha um(a) {name}"
        )

        filter_res.update({str(name): component})
    return filter_res


def visualizer(bd: pd.DataFrame):
    st.header(":bar_chart: Análise de Inadimplência")
    st.markdown("#")

    inadimplentes= round(bd['inadimplente'].value_counts())

    inadim = bd.groupby('inadimplente').get_group(1)
    rendimento = inadim.groupby(['renda']).agg({'inadimplente': 'count'}).reset_index()
    total_rend = round(rendimento['inadimplente'].sum())
    percent1 = round(((rendimento['inadimplente'] / total_rend)*100),2)

    ocupa = inadim.groupby(['ocupacao']).agg({'inadimplente': 'count'}).reset_index()
    total_ocupa = round(ocupa['inadimplente'].sum())
    percent2 = round(((ocupa['inadimplente'] / total_ocupa) * 100), 2)

    renda_ocupa = inadim.groupby(['renda', 'ocupacao']).agg({'inadimplente': 'count'}).reset_index()
    total = round(renda_ocupa['inadimplente'].sum())
    percentual = round(((renda_ocupa['inadimplente'] / total_ocupa) * 100), 2)

    categorias = {'0': 'Indisponível','1': 'Sem rendimento',
                 '2':'Até 1 salário mínimo', '3':'1 a 2 salários mínimos',
                 '4':'2 a 3 salários mínimos', '5':'3 a 5 salários mínimos',
                 '6':'5 a 10 salários mínimos', '7':'10 a 20 salários mínimos',
                 '8':'Acima de 20 salários mínimos'}



    fig_renda = px.bar(rendimento,
                       title='Inadimplencia por Renda',
                       x='renda',
                       y=percent1,
                       color_discrete_sequence=["#DB5418"],
                       labels={'y':'% inadimplentes'},
                       text= categorias)

    fig_ocupa = px.bar(ocupa,
                       title='Inadimplencia por Ocupação',
                       x='ocupacao',
                       y=percent2,
                       color_discrete_sequence=["#326b63"],
                       labels={'y': '% inadimplentes', 'ocupacao':''})

    fig_renda_ocupa = px.line(renda_ocupa,
                             x='renda',
                             y=percentual,
                             color='ocupacao',
                             labels={'y': '% inadimplentes'})



    st.plotly_chart(fig_renda)
    st.plotly_chart(fig_ocupa)



    st.dataframe(bd)


def main(dataframe):
    filter_res = set_sidebar(bd=dataframe)
    # print("STATE HERE", filter_results)
    filter_pattern = clause(filter_res=filter_res)
    # print("FILTER PATTERN", filter_pattern)
    df_selection = dataframe.query(
        expr=eval(filter_pattern),
        engine='python'
    ) if filter_pattern else dataframe

    visualizer(bd=df_selection)


FILTER_LIST = ["uf", "modalidade"]

bd = load_data()
main(dataframe=bd)
