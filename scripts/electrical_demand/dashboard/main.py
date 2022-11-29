import streamlit as st
from electrical_demand.dashboard.utils import get_data, line_plot
from electrical_demand.process_data.utils import daterange
from datetime import date, timedelta
from electrical_demand.dashboard.config import DATABASE_API_CONTAINER_NAME, DATABASE_API_PORT

start_date = date(2019,1,1)
end_date = date(2022,12,31)
dates = tuple(str(d) for d in daterange(start_date, end_date))

def main():
    api_url = "http://" + DATABASE_API_CONTAINER_NAME + ":" + DATABASE_API_PORT

    st.write("""
    ## Electrical demand and forecast in Argentina
    """)

    data_to_show = st.sidebar.radio(
        "Select region",
        ("TOTAL", "BUENOS AIRES", "CATAMARCA", "CHACO", "CHUBUT", "CORDOBA", "CORRIENTES", "ENTRE RIOS", "FORMOSA", "JUJUY", "LA PAMPA", "LA RIOJA", "MENDOZA", "MISIONES", "NEUQUEN",
        "RIO NEGRO", "SALTA", "SAN JUAN", "SAN LUIS", "SANTA CRUZ", "SANTA FE", "SANTIAGO DEL ESTERO", "TUCUMAN"))

    st.write(f"""### {data_to_show}""")

    yesterday = date.today() - timedelta(days = 1)

    option = st.date_input(
        "Date",
        yesterday)

    data = get_data(api_url, data_to_show, option)

    line_plot(data, "Electrical demand")

if __name__ == "__main__":

    main()