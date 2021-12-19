import streamlit as st
import pandas as pd
from gsheetsdb import connect
import plotly.graph_objects as go
import datetime
import plotly.express as px

st.title("Incrementality View")
#gsheet_url = st.secrets["public_url"]
gsheet_url = "https://docs.google.com/spreadsheets/d/1ky2lnpZd1dQCRvc0Zvux1wIzkIgB_c2s1qpib0ftYgw/edit#gid=0"

conn = connect()
rows = conn.execute(f'SELECT * FROM "{gsheet_url}"')
df = pd.DataFrame(rows)

# Sidebar
metrics = df.columns
metrics = metrics[2:]
select_metric = st.sidebar.selectbox("Select Metric", metrics)
start_date = st.sidebar.date_input('Start Date', df['date'].min())
end_date = st.sidebar.date_input('End Date', df['date'].max())
check = st.sidebar.checkbox('Advanced results')
if check:
    st.sidebar.write("Advanced results selected (Feature is WIP)")

st.sidebar.color_picker('Pick a color')


#todo: build comparison and metrics
#df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]

col1, col2, col3, col4 = st.columns(4)
col1.metric("Investment", "$5000", "1.2 °F")
col2.metric("Total Free Trials", "300", "-8%")
col3.metric("incremental cost", "$10")
col4.metric("% incremental", "50%")


# build out plots
df_chart = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
df_chart = df_chart.set_index('date')
df_chart = df_chart[[select_metric]]

st.caption('Selected Period')
st.bar_chart(df_chart)

with st.expander("Results compared to period before"):
    times = ['before', 'after']
    fig = go.Figure([go.Bar(x=times, y=[100, 200])])
    st.plotly_chart(fig, use_container_width=True)

with st.expander("Full dataset"):
    st.write("""
        Full dataset for whole period.
    """)
    st.line_chart(df[select_metric])
