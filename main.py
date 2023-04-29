import pandas as pd
import streamlit as st
import plotly_express as px

with open('estilo.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

@st.cache_data

def load_data() -> pd.DataFrame:
    expect = pd.read_csv('expectative_vida.csv')
    expect["Year"] = expect["Year"].astype('string')
    return expect

def build_where_clause(filter_results: dict) -> str:
    clause_list = list()
    for column in FILTER_LIST:
        if filter_results[column] != []:
            clause_list.append(f"`{column}` in {filter_results[column]}")

    clause_treated = str(clause_list) \
        .replace('", "', ' & ')[1:-1] \
        .replace('[', '(') \
        .replace(']', ')')
    return clause_treated

def set_sidebar(
        expect:pd.DataFrame = None,
        filtered: pd.DataFrame = None) -> dict:
    if filtered is None:
        df = expect
    else:
        df = filtered

    filter_results = dict()
    for i, name in enumerate(FILTER_LIST):
        component = st.sidebar.multiselect(
            key=i,
            label=name,
            options=df[name].unique(),
            help=f"Select a {name}"
        )
        filter_results.update({str(name): component})
    return filter_results

def build_visualizations(expect: pd.DataFrame):
    st.header(":bar_chart: Expectativa de Vida")
    st.markdown("#")

    expectativa = round(expect['Life expectancy'].mean(),2)


    expect_by_year = (
        expect.groupby(by="Year").mean(numeric_only=True)[['Life expectancy']].sort_values("Year")
        )
    expect_by_status = (
        expect.groupby(by="Status").mean(numeric_only=True)[["Life expectancy"]].sort_values("Status")
    )
    expenditure_by_year =(
        expect.groupby(by="Year").mean(numeric_only=True)[["Total expenditure"]].sort_values("Year")
    )
    expect_by_country = (
       expect.groupby(by="Country").mean(numeric_only=True)[["Life expectancy"]].sort_values("Country")
    )
    idh_year = (
        expect.groupby(by="Year").mean(numeric_only=True)[["Income composition of resources"]].sort_values("Year")
    )

    fig_expect_by_year = px.line(
        expect_by_year,
        title="<b>Expectativa de Vida Mundial por ano</b>",
        x=expect_by_year.index,
        y="Life expectancy",
        color_discrete_sequence=["#f17b1b"] * len(expect_by_year),
    )
    fig_expenditure_by_year = px.bar(
        expenditure_by_year,
        title="<b>Média Anual de Gastos do Governo com Saúde(%)</b>",
        x=expenditure_by_year.index,
        y="Total expenditure",
        orientation="v",
        text="Total expenditure",
        color_discrete_sequence=["#f17b1b"] * len(expenditure_by_year),
        width=500,
    )

    fig_expect_by_status = px.pie(
        expect_by_status,
        title='<b>Expectativa de Vida por Status</b>',
        names=expect_by_status.index,
        values='Life expectancy',
        color_discrete_sequence=['#f17b1b'],
        width=450,
    )

    fig_expect_by_country = px.choropleth(
        expect,
        locations="Code",
        color="Country",
        hover_name="Life expectancy",
        width=900,
        color_continuous_scale=px.colors.sequential.Plasma
    )

    fig_idh_year = px.scatter(
        expect,
        x="Year",
        y="Income composition of resources",
        color="Country",
        title="IDH Mundial ",
        color_discrete_sequence=['#f17b1b']
    )

    st.markdown('Média da expectativa de vida entre os anos de 2000 e 2015')

    st.subheader(f":orange[{expectativa:,}]")

    chart_column1_left, chart_column1_right = st.columns([0.5, 0.3])

    chart_column1_left.plotly_chart(fig_expect_by_year)
    with chart_column1_right:
        st.plotly_chart(fig_expenditure_by_year)


    chart_column2_left, chart_column2_right = st.columns(2)
    chart_column2_left.plotly_chart(fig_expect_by_status)
    with chart_column2_right:
        st.plotly_chart(fig_idh_year)


    st.plotly_chart(fig_expect_by_country)
    st.dataframe(expect)

def main(dataframe):
    filter_results = set_sidebar(expect=dataframe)
    # print("STATE HERE", filter_results)
    filter_pattern = build_where_clause(filter_results=filter_results)
    # print("FILTER PATTERN", filter_pattern)
    df_selection = dataframe.query(
        expr=eval(filter_pattern),
        engine='python'
    ) if filter_pattern else dataframe

    build_visualizations(expect=df_selection)


FILTER_LIST = ["Country", "Year"]

expect = load_data()
main(dataframe=expect)