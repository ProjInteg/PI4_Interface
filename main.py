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
    base_dados = pd.read_excel('dados_clean.xlsx')
    return base_dados


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
        base_dados: pd.DataFrame = None,
        filtered: pd.DataFrame = None) -> dict:
    if filtered is None:
        df = base_dados
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


def visualizer(base_dados: pd.DataFrame):
    st.header(":bar_chart: Taxa de Inadimplencia")
    st.markdown("#")

    adimplentes = base_dados[base_dados['inadimplente'] == 0.0]
    inadimplentes = base_dados[base_dados['inadimplente'] == 1.0]
    populacao = base_dados['uf'].value_counts(normalize=True) * 100
    inadimplencia = inadimplentes['uf'].value_counts(normalize=True) * 100

    qtd_inadim_adim = base_dados['inadimplente'].value_counts()


    fig_pop_inad = px.bar(
        x=inadimplencia,
        y=populacao,
        barmode='group',
        labels={'x': '% Inadimplência','y': '% População'},
        color_discrete_sequence=["#f17b1b"]
    )

    fig_adim_inadim = px.pie(
        title='<b>Porcentagem de Adimplentes e Inadimplentes</b>',
        names=qtd_inadim_adim.index.map({0: 'Adimplentes', 1: 'Inadimplentes'}),
        values=qtd_inadim_adim.values,
        color_discrete_sequence=['#f17b1b'],


    )

    st.plotly_chart(fig_pop_inad)
    st.plotly_chart(fig_adim_inadim)

    st.dataframe(base_dados)


def main(dataframe):
    filter_res = set_sidebar(base_dados=dataframe)
    # print("STATE HERE", filter_results)
    filter_pattern = clause(filter_res=filter_res)
    # print("FILTER PATTERN", filter_pattern)
    df_selection = dataframe.query(
        expr=eval(filter_pattern),
        engine='python'
    ) if filter_pattern else dataframe

    visualizer(base_dados=df_selection)


FILTER_LIST = ["uf", "modalidade"]

base_dados = load_data()
main(dataframe=base_dados)
