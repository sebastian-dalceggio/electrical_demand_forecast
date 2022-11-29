import streamlit as st
import pandas as pd
import requests
import altair as alt
from electrical_demand.logger import get_logger
logger = get_logger("streanlit.log", level="INFO")

def get_data(api_url, region, day):
    logger.info("region: " + region + "; day: " + str(day))
    data = pd.read_json(requests.get(api_url + f"/get-region/{region}/{day}").json()["data"])
    logger.info("get data: " + str(data))
    return data

def line_plot(data, title):
    logger.info("data raw: " + str(data))
    data = data.rename(columns={"demand": "demand_real"})
    data = data.melt('hour', var_name='demand_type', value_name='MW')
    logger.info("data after melt: " + str(data))
    chart = alt.Chart(data).mark_line().encode(
        x=alt.X('hour:N'),
        y=alt.Y('MW:Q', sort="ascending"),
        color=alt.Color("demand_type:N")
    ).properties(title=title)
    st.altair_chart(chart, use_container_width=True)
    return 0
