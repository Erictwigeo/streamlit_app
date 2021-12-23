import streamlit as st
import pandas as pd
from gsheetsdb import connect
import plotly.graph_objects as go
import datetime
import plotly.express as px

st.set_page_config(layout="wide")

# Connect to data
#todo: option to switch between google sheet and manual file
gsheet_url = st.secrets["public_url"]
conn = connect()
rows = conn.execute(f'SELECT * FROM "{gsheet_url}"')
df = pd.DataFrame(rows)

# Sidebar
st.sidebar.write("Insert data on the url below: https://docs.google.com/spreadsheets/d/1ky2lnpZd1dQCRvc0Zvux1wIzkIgB_c2s1qpib0ftYgw/edit#gid=0")
metrics = df.columns[2:]
select_metric = st.sidebar.selectbox("Select Metric", metrics)
start_date = st.sidebar.date_input('Start Date', df['date'].min())
end_date = st.sidebar.date_input('End Date', df['date'].max())

with st.sidebar.expander("Advanced Settings"):
    check_manual_budget = st.checkbox("Add Manual Budget")
    if check_manual_budget:
        number = st.number_input('Manual budget')
        st.write('Selected budget:', number)

    custom_period = st.checkbox("Custom comparison period")
    if custom_period:
        start_date_comp_custom = st.date_input('Start Date baseline', df['date'].min())
        end_date_comp_custom = st.date_input('End Date baseline', df['date'].max())

    check_reported_conversions = st.checkbox("Add reported conversions")
    if check_reported_conversions:
        reported_conversions = st.number_input("Reported Conversions")


check_run = st.sidebar.button('Run Incrementality Analysis')
if check_run:
    st.sidebar.write("**Measurment completed**")

# Manipulate data
df_selected = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
diff = end_date - start_date + pd.Timedelta(days=1)

if custom_period:
    start_date_comp = start_date_comp_custom
    end_date_comp = end_date_comp_custom
else:
    start_date_comp = start_date - diff
    end_date_comp = start_date - pd.Timedelta(days=1)

df_before = df[(df['date'] >= start_date_comp) & (df['date'] <= end_date_comp)]

investment_pop = (df_selected['investment'].sum() / df_before['investment'].sum()) - 1
investment_pop = (investment_pop * 100).astype(int)
kpi_pop = (df_selected[select_metric].sum() / df_before[select_metric].sum()) - 1
kpi_pop = (kpi_pop * 100).astype(int)
incremental_kpi = df_selected[select_metric].sum() - df_before[select_metric].sum()
incremental_cost = round(df_selected['investment'].sum() / incremental_kpi, 2)

st.title("Twigeo Incrementality")
if check_run:
    #todo: fix graph
    if check_reported_conversions:
        col1, col2, col3, col4, col5 = st.columns(5)
        incremental_comp = incremental_kpi - reported_conversions
        pct_incremental = int(((incremental_kpi / reported_conversions)-1)*100)
        col5.metric("Compared to reported conv.", incremental_comp, str(pct_incremental) + "%")
    else:
        col1, col2, col3, col4 = st.columns(4)

    if check_manual_budget:
        col1.metric("Investment", str(number))
        col4.metric("incr CP" + select_metric, "$" + str(round(number / df_selected[select_metric].sum(),2)))
    else:
        col1.metric("Investment", str(df_selected['investment'].sum()), str(investment_pop) + "% PoP")
        col4.metric("incr CP" + select_metric, "$" + str(incremental_cost))
    col2.metric(select_metric, df_selected[select_metric].sum(), str(kpi_pop) + "% PoP")
    col3.metric("incremental " + select_metric, incremental_kpi)
    #col5.metric("% incremental", "50%")
    st.sidebar.write("Test period: " + str(start_date) + " to " + str(end_date) + "   " +
                     "Control period: " + str(start_date_comp) + " to " + str(end_date_comp))
    st.caption('Selected Period')
    df_chart = df_selected.set_index('date')
    df_chart = df_chart[[select_metric]]
    st.bar_chart(df_chart)

if check_run:
    #todo:fix graph
    st.caption("Results compared to period before")
    times = ['Baseline', 'After budget change']
    fig = go.Figure([go.Bar(x=times, y=[df_before[select_metric].sum(), df_selected[select_metric].sum()])])
    st.plotly_chart(fig, use_container_width=True)

with st.expander("Full dataset"):
    st.write("""
        Full dataset for whole period.
    """)
    # todo: Colour full dataset by selected periods
    st.line_chart(df[select_metric])

