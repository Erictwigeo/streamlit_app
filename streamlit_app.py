import streamlit as st
import pandas as pd
from gsheetsdb import connect
import plotly.graph_objects as go
import datetime
import plotly.express as px

st.set_page_config(layout="wide")
st.title("Twigeo Incrementality")
st.sidebar.write("Insert data on the url below: https://docs.google.com/spreadsheets/d/1ky2lnpZd1dQCRvc0Zvux1wIzkIgB_c2s1qpib0ftYgw/edit#gid=0")
gsheet_url = "https://docs.google.com/spreadsheets/d/1ky2lnpZd1dQCRvc0Zvux1wIzkIgB_c2s1qpib0ftYgw/edit#gid=0"
#gsheet_url = st.secrets["public_url"]

conn = connect()
rows = conn.execute(f'SELECT * FROM "{gsheet_url}"')
df = pd.DataFrame(rows)

# Sidebar
metrics = df.columns
metrics = metrics[2:]
select_metric = st.sidebar.selectbox("Select Metric", metrics)
start_date = st.sidebar.date_input('Start Date', df['date'].min())
end_date = st.sidebar.date_input('End Date', df['date'].max())

check_manual_budget = st.sidebar.checkbox("Insert Manual budget")
if check_manual_budget:
    number = st.sidebar.number_input('Insert Manual budget for the test ')
    st.sidebar.write('Seöected budget:', number)

check_run = st.sidebar.button('Run Incrementality Analysis')
if check_run:
    st.sidebar.write("**Measurment completed**")

df_selected = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
diff = end_date - start_date + pd.Timedelta(days=1)
other_date = start_date - diff
df_before = df[(df['date'] >= other_date) & (df['date'] < start_date)]

investment_pop = (df_selected['investment'].sum() / df_before['investment'].sum()) - 1
investment_pop = (investment_pop * 100).astype(int)
kpi_pop = (df_selected[select_metric].sum() / df_before[select_metric].sum()) - 1
kpi_pop = (kpi_pop * 100).astype(int)
incremental_kpi = df_selected[select_metric].sum() - df_before[select_metric].sum()
incrmemental_cost = round(df_selected['investment'].sum() / df_selected[select_metric].sum(), 2)

if check_run:
    col1, col2, col3, col4 = st.columns(4)
    if check_manual_budget:
        col1.metric("Investment", str(number))
        col4.metric("incr CP" + select_metric, "$" + str(round(number / df_selected[select_metric].sum(),2)))
    else:
        col1.metric("Investment", str(df_selected['investment'].sum()), str(investment_pop) + "% PoP")
        col4.metric("incr CP" + select_metric, "$" + str(incrmemental_cost))
    col2.metric(select_metric, df_selected[select_metric].sum(), str(kpi_pop) + "% PoP")
    col3.metric("incremental " + select_metric, incremental_kpi)
    #col5.metric("% incremental", "50%")

    st.caption('Selected Period')
    df_chart = df_selected.set_index('date')
    df_chart = df_chart[[select_metric]]
    st.bar_chart(df_chart)

if check_run:
    st.caption("Results compared to period before")
    times = ['Baseline', 'After budget change']
    fig = go.Figure([go.Bar(x=times, y=[df_before[select_metric].sum(), df_selected[select_metric].sum()])])
    st.plotly_chart(fig, use_container_width=True)

with st.expander("Full dataset"):
    st.write("""
        Full dataset for whole period.
    """)
    st.line_chart(df[select_metric])
