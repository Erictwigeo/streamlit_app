import streamlit as st
import pandas as pd
from gsheetsdb import connect
import plotly.graph_objects as go

st.set_page_config(layout="wide")


# function for inserting data from selected Google Sheet
def insert_data(url):
    st.subheader("Insert your data in the url below:")
    st.write(url)
    gsheet_url = url
    # gsheet_url = st.secrets["public_url"]
    conn = connect()
    rows = conn.execute(f'SELECT * FROM "{gsheet_url}"')
    df = pd.DataFrame(rows)
    with st.expander('Inpect data'):
        if not df.empty:
            if not 'date' == df.columns[0]:
                st.error('Add the "date" column and put it as the fist column in the dataset')
            st.warning('If cost/spend/investment is added, make sure it is labeled "investment" (lower case)')
            df
            st.success('Nice! Move ahead :point_down:')
        else:
            st.error('No data was found.')

    st.warning('Make sure to inspect the dataset above before moving on')
    return df

# Connect to data
#todo: select what dashboard. Switching between dashbaords
#todo: option to switch between google sheet and manual file
app_mode = st.sidebar.selectbox("Select step", ["Introduction", "Run Analysis"])
if app_mode == "Introduction":
    st.sidebar.success('To continue select "Run Analysis".')
    st.title('Twigeo Incrementality Dashboard :bar_chart:')
    st.subheader('This web app help you analyse our marketing efforts by comparing 2 periods of time and calculate the incremental difference in '
                 'conversions between the periods.')
    st.write('This type of incrementality analysis is simple and effective for getting a rough readout on incrementality.'
             'However, it does not take things like seasonality and external factors into account. For a more exact and scientific approach, Geo Experiments or MMM should be explored. ')
    st.subheader(':point_left: Give it a try!')

if app_mode == 'Run Analysis':
    df = pd.DataFrame()
    st.header('Step 1 - Insert Data')
    file_type = st.selectbox('Select sheet', ['Select sheet: ', 'Example dataset', 'Google Sheet 1',
                                              'Google Sheet 2', 'Google Sheet 3', 'Google Sheet 4', 'Google Sheet 5'])
    #todo: implement CSV solution
    #if file_type == 'CSV':
    #    csv_file = st.file_uploader("Upload CSV file")
    #    df = csv_file
    #    st.text('Select Run the App in the sidebar to start incrementality analysis.')
    #    st.subheader('Inpect data')

    if file_type == 'Example dataset':
        df = insert_data("https://docs.google.com/spreadsheets/d/1ky2lnpZd1dQCRvc0Zvux1wIzkIgB_c2s1qpib0ftYgw/edit#gid=0")

    elif file_type == 'Google Sheet 1':
        df = insert_data("https://docs.google.com/spreadsheets/d/1ky2lnpZd1dQCRvc0Zvux1wIzkIgB_c2s1qpib0ftYgw/edit#gid=484928885")

    elif file_type == 'Google Sheet 2':
        df = insert_data(
            "https://docs.google.com/spreadsheets/d/1ky2lnpZd1dQCRvc0Zvux1wIzkIgB_c2s1qpib0ftYgw/edit#gid=641902215")

    elif file_type == 'Google Sheet 3':
        df = insert_data(
            "https://docs.google.com/spreadsheets/d/1ky2lnpZd1dQCRvc0Zvux1wIzkIgB_c2s1qpib0ftYgw/edit#gid=1653926147")

    elif file_type == 'Google Sheet 4':
        df = insert_data(
            "https://docs.google.com/spreadsheets/d/1ky2lnpZd1dQCRvc0Zvux1wIzkIgB_c2s1qpib0ftYgw/edit#gid=971857681")

    elif file_type == 'Google Sheet 1':
        df = insert_data(
            "https://docs.google.com/spreadsheets/d/1ky2lnpZd1dQCRvc0Zvux1wIzkIgB_c2s1qpib0ftYgw/edit#gid=1772097629")

    st.text(" ")
    st.text(" ")
    st.text(" ")
    st.write("###")
    st.write("###")
    #todo: Add text and area where you can
    if not df.empty:
        metrics = df.columns[1:]
        st.sidebar.subheader('Select parameters for analysis :point_down:')
        select_metric = st.sidebar.selectbox("Select Metric", metrics)
        start_date = st.sidebar.date_input('Start Date', df['date'].min())
        end_date = st.sidebar.date_input('End Date', df['date'].max())

        with st.sidebar.expander("Advanced Settings"):
            check_manual_budget = st.checkbox("Add Manual Budget")
            if check_manual_budget:
                number_sel = st.number_input('Manual budget selected period')
                st.write('Selected budget:', number_sel)
                number_control = st.number_input('Manual budget control period')
                st.write('Selected budget:', number_control)

            custom_period = st.checkbox("Custom comparison period")
            if custom_period:
                start_date_comp_custom = st.date_input('Start Date baseline', df['date'].min())
                end_date_comp_custom = st.date_input('End Date baseline', df['date'].max())

            check_reported_conversions = st.checkbox("Add reported conversions")
            if check_reported_conversions:
                reported_conversions = st.number_input("Reported Conversions",
                                                       help='Add reported/last-touch converisons to be compared to incremental conversions.')

            check_marginal_incr = st.checkbox("Calculate Marginal incrementality",
                                              help='Check this box if you want to take the marginal investment into account as well (total investment = spend selected period - spend control period)')

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
        investment_diff = df_selected['investment'].sum() - df_before['investment'].sum()
        investment_pop = (investment_pop * 100).astype(int)
        kpi_pop = (df_selected[select_metric].sum() / df_before[select_metric].sum()) - 1
        kpi_pop = (kpi_pop * 100).astype(int)
        incremental_kpi = df_selected[select_metric].sum() - df_before[select_metric].sum()

        if check_marginal_incr:
            incremental_cost = round(investment_diff / incremental_kpi, 2)
        else:
            incremental_cost = round(df_selected['investment'].sum() / incremental_kpi, 2)

        st.header("Step 2 - Incrementality Analysis")
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
                col1.metric("Investment", str(int(number_sel)))
                if check_marginal_incr:
                    incremental_cost = round((number_sel - number_control) / incremental_kpi, 1)
                else:
                    incremental_cost = round(number_sel / incremental_kpi, 1)
                col4.metric("incr CP" + select_metric, "$" + str(int(incremental_cost)))
            else:
                col1.metric("Investment", str(df_selected['investment'].sum().astype(int)), str(investment_pop) + "% PoP")
                col4.metric("incr CP" + select_metric, "$" + str(incremental_cost))
            col2.metric(select_metric, int(df_selected[select_metric].sum()), str(kpi_pop) + "% PoP")
            col3.metric("incremental " + select_metric, int(incremental_kpi))
            #col5.metric("% incremental", "50%")
            st.sidebar.write("Selected period: " + str(start_date) + " to " + str(end_date))
            st.sidebar.write("Control period: " + str(start_date_comp) + " to " + str(end_date_comp))

            times = ['Control Period', 'Selected Period']
            comp_col = ['darkred', 'darkgreen']
            fig = go.Figure([go.Bar(x=times,
                                    y=[df_before[select_metric].sum(), df_selected[select_metric].sum()],
                                    text=[int(df_before[select_metric].sum()), int(df_selected[select_metric].sum())],
                                    textposition='auto',
                                    marker_color=comp_col)])
            fig.update_layout(uniformtext_minsize=20, uniformtext_mode='hide')
            fig.layout.plot_bgcolor = '#fff'
            st.plotly_chart(fig, use_container_width=True)

            fig = go.Figure(data=[go.Bar(
                x=df_selected['date'],
                y=df_selected[select_metric],
                marker_color='lightslategray'
            )])
            fig.update_layout(title_text=select_metric + ' for selected period', title_x=0.5)
            st.plotly_chart(fig, use_container_width=True)

        colors = ['lightslategray', ] * df.shape[0]
        if check_run:
            bef_period = df_before.index
            sel_period = df_selected.index
            for i in bef_period:
                colors[i] = 'darkred'
            for i in sel_period:
                colors[i] = 'darkgreen'
        fig = go.Figure(data=[go.Bar(
            x=df['date'],
            y=df[select_metric],
            marker_color=colors  # marker color can be a single color value or an iterable
        )])

        if check_run:
            fig.update_layout(title_text='Full dataset (Green = selected period, Red = comparison period)', title_x=0.5)
        else:
            fig.update_layout(title_text='Full dataset', title_x=0.5)
        st.plotly_chart(fig, use_container_width=True)

        if check_run:
            with st.expander('Show comparison data'):
                if check_manual_budget:
                    d = {'metric': ['Investment', select_metric],
                         'selected_period': [number_sel, df_selected[select_metric].sum()],
                         'control_period': [number_control, df_before[select_metric].sum()],
                         'difference': [(number_sel - number_control),incremental_kpi]}
                else:
                    d = {'metric': ['Investment', select_metric],
                         'Selected Period': [df_selected['investment'].sum(), df_selected[select_metric].sum()],
                         'Control Period': [df_before['investment'].sum(), df_before[select_metric].sum()],
                         'Diff': [investment_diff, incremental_kpi]}
                df_output = pd.DataFrame(data=d)
                st.table(df_output)

        with st.expander("Show Investment for whole period"):
            fig = go.Figure(data=[go.Bar(
                x=df['date'],
                y=df['investment']
            )])
            st.plotly_chart(fig, use_container_width=True)
