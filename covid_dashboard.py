from codecs import ignore_errors
import pandas as pd
import streamlit as st
from datetime import timedelta
from datetime import datetime
from pylab import plt
today = datetime.today().date()


@st.cache(allow_output_mutation=True)
def load_dataset():
    try:
        df = pd.read_csv(
            "https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv", sep=",")
        states = list(df['state'].unique())
    except:
        Exception
    return df, states


def pct_change(data, state, today):
    data = data.query('state==@state')
    last_month = today - timedelta(days=30)
    last_week = today - timedelta(days=15)
    data['date'] = pd.to_datetime(data['date'])
    last_month_df = data.query("date>=@last_month")
    last_month_df = last_month_df[['date', 'cases', 'deaths']]
    grouped_df = last_month_df.groupby(['date']).sum().reset_index()
    # last_week_df.drop_duplicates(inplace=True)
    grouped_df['diff_cases'] = grouped_df['cases'].diff(periods=1)
    grouped_df['diff_deaths'] = grouped_df['deaths'].diff(periods=1)
    #last_week_df.query("diff != 0", inplace=True)
    # last_week_df.dropna(inplace=True)
    grouped_df['case_avg'] = grouped_df.rolling(window=7)['diff_cases'].mean()
    grouped_df['death_avg'] = grouped_df.rolling(
        window=7)['diff_deaths'].mean()
    recent_cases_obv = grouped_df['case_avg'].iloc[-1]
    recent_death_obv = grouped_df['death_avg'].iloc[-1]
    old_case_obv = grouped_df.query("date==@last_week")['case_avg'].iloc[0]
    old_death_obv = grouped_df.query("date==@last_week")['death_avg'].iloc[0]
    case_chg = round(100 * ((recent_cases_obv - old_case_obv)/old_case_obv))
    death_chg = round(100 * ((recent_death_obv - old_death_obv)/old_death_obv))
    data_dict = {'Cases': round(recent_cases_obv), 'Deaths': round(recent_death_obv),
                 'Case Change': case_chg, 'Death Change': death_chg}
    return data_dict


def chart_data(data, state):
    data['date'] = pd.to_datetime(data['date'])
    filtered_data = data.query('state==@state')
    grouped_df = filtered_data[['date', 'cases', 'deaths']].groupby(
        ['date']).sum().reset_index()
    grouped_df['new cases'] = grouped_df['cases'].diff(periods=1)
    return grouped_df[['date', 'new cases']].set_index('date')


df, states = load_dataset()

state_dropdown = st.selectbox('Select a State', states)

if state_dropdown:
    data_dict = pct_change(df, state_dropdown, today)
    col1, col2, col3, col4 = st.columns(4)
    col1.markdown(f"New Cases: {data_dict['Cases']}")
    col2.markdown(
        f"""<p>14-Day Change: <span style="color:red">{data_dict['Case Change']}%</span></p>""", unsafe_allow_html=True)
    col3.markdown(f"New Deaths: {data_dict['Deaths']}")
    col4.markdown(
        f"""<p>14-Day Change: <span style="color:red">{data_dict['Death Change']}%</span></p>""", unsafe_allow_html=True)
    chart_data = chart_data(df, state_dropdown)
    st.line_chart(chart_data)