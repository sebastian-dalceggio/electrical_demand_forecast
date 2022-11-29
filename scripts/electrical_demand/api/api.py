"""
This module provides a serie of abstractions of different APIs.
An API instance can be createad and then call the etl method with the
appropriate keywords to get the data as a dataframe and load it to S3.
"""

import requests
import pandas as pd
import json
from datetime import datetime
from electrical_demand.process_data.loaders import load_df_csv_to_s3
from electrical_demand.logger import get_logger



# HistoricalSNMPApi
FILTER_ROWS = [" ", "F"]
HISTORICAL_STATIONS = ["CORDOBA AERO"]

# ForecastSMNApi
POSITION_FIRST_STATION = 5
LINES_BETWEEN_STATIONS = 46
HEADER_LINES = 4
LOWER_LINES = 1
DAYS = 5
POINTS_PER_DAY = 8
TOTAL_DATA_POINTS = POINTS_PER_DAY * DAYS
MONTHS_DICT = {
    "ENE": "Jan",
    "FEB": "Feb",
    "MAR": "Mar",
    "ABR": "Apr",
    "MAY": "May",
    "JUN": "Jun",
    "JUL": "Jul",
    "AGO": "Aug",
    "SEP": "Sep",
    "OCT": "Oct",
    "NOV": "Nov",
    "DIC": "Dec"
}

class BaseApi():
    """
    Abstract class used to call different APIs.
    This is an abstract class. For each API there is a class that inherits this one.
    With this class you get a connection to the actual API. Using the etl method with the correct
    parameters returns the data as a pandas dataframe.
    ...

    Attributes
    ----------
    bucket : str
        S3 bucket where the data is loaded.
    url_prefix : str
        general prefix url for an api
    logger : python logger
        python logger
    ...
    Methods
    -------
    _get_url(*args, **kwargs)
        Return the api url with the keywords provided.
    _get_url_postfix(*args, **kwargs)
        Return the api url with the keywords provided.
    _download(*args, **kwargs)
        Return the text response of the api call
    _process_data(*args, **kwargs)
        Process the data and return a list of dicts
    _to_df(*args, **kwargs)
        Process the list of dicts and return a Pandas dataframe
    etl(*args, **kwargs)
        Run the whole process and upload the data as a csv to S3
    _get_file_path(date, file_type)
        Returns the specific file path where the data is stored in the bucket

    """
    def __init__(self, bucket):
        """
        Parameters
        ----------
        bucket : string
            S3 bucket where the data is loaded.
        """
        self.url_prefix = None
        self.bucket = bucket
        self.logger = get_logger(name=self.__class__.__name__)

    def _get_url(self, *args, **kwargs):
        """
        Gets the complete url by concatenating the url_prefix of the api and the 
        specific url_postfix.

        Parameters
        ----------
        *args :
            The args parameters are specific of each inherited class.
            See the docstring of each for a detailed list of arguments.
        **kwargs :
            The kwargs parameters are specific of each inherited class.
            See the docstring of each for a detailed list of arguments.

        Returns
        -------
        url : string
            Return complete url of the api
        """
        url = self.url_prefix + self._get_url_postfix(*args, **kwargs)
        return url
    
    def _get_url_postfix(self, *args, **kwargs):
        """
        Gets the postfix url with the given arguments.

        Parameters
        ----------
        *args :
            The args parameters are specific of each inherited class.
            See the docstring of each for a detailed list of arguments.
        **kwargs :
            The kwargs parameters are specific of each inherited class.
            See the docstring of each for a detailed list of arguments.

        Returns
        -------
        url_postfix : string
            Returns a specific postfix url for a given api call
        """

    def _download(self, *args, **kwargs):
        """
        Call the api with the given arguments and returns the raw data as an string.

        Parameters
        ----------
        *args :
            The args parameters are specific of each inherited class.
            See the docstring of each for a detailed list of arguments.
        **kwargs :
            The kwargs parameters are specific of each inherited class.
            See the docstring of each for a detailed list of arguments.

        Returns
        -------
        response : string
            Returns a specific postfix url for a given api call
        """
        try:
            response = requests.get(self._get_url(*args, **kwargs)).text
            return response
        except requests.exceptions.RequestException as e:
            self.logger.error(str(e))

    def _process_data(self, *args, **kwargs):
        """
        It receives the raw text data and returns as a list of dicts.

        Parameters
        ----------
        *args :
            The args parameters are specific of each inherited class.
            See the docstring of each for a detailed list of arguments.
        **kwargs :
            The kwargs parameters are specific of each inherited class.
            See the docstring of each for a detailed list of arguments.

        Returns
        -------
        dict_data : list of dicts
            Returns the processed data as a list of dicts
        """

    def _to_df(self, *args, **kwargs):
        """
        It receives the data as a list of dicts and returns a Pandas dataframe.

        Parameters
        ----------
        *args :
            The args parameters are specific of each inherited class.
            See the docstring of each for a detailed list of arguments.
        **kwargs :
            The kwargs parameters are specific of each inherited class.
            See the docstring of each for a detailed list of arguments.

        Returns
        -------
        dataframe : Pandas dataframe
            Returns the processed data as pandas dataframe
        """
    
    def etl(self, *args, **kwargs):
        """
        Calls the _download, _process_data and _to_df methods. It is the only one method exposed.
        It loads the pandas dataframe as a csv to the S3 bucket.

        Parameters
        ----------
        *args :
            The args parameters are specific of each inherited class.
            See the docstring of each for a detailed list of arguments.
        **kwargs :
            The kwargs parameters are specific of each inherited class.
            See the docstring of each for a detailed list of arguments.

        Returns
        -------
        dataframe : Pandas dataframe
            Returns the processed data as pandas dataframe
        """

    def _get_file_path(self, date, file_type):
        """
        Gets the specific file path where the data is stored in the bucket.

        Parameters
        ----------
        *args :
            The args parameters are specific of each inherited class.
            See the docstring of each for a detailed list of arguments.
        **kwargs :
            The kwargs parameters are specific of each inherited class.
            See the docstring of each for a detailed list of arguments.

        Returns
        -------
        postfix_dir : string
            Returns the specific file path where the data is stored in the bucket.
        """
        postfix_dir = "%s/year=%4d/month=%02d/%02d.%s" % (file_type, date.year, date.month, date.day, file_type, )
        return postfix_dir

class CammesaApi(BaseApi):
    def __init__(self, bucket):
        super().__init__(bucket)
        self.url_prefix = "https://api.cammesa.com/demanda-svc/demanda/"

class DemandByDateByRegionApi(CammesaApi):
    def _get_url_postfix(self, demand_date, region_id):
        """
        Gets the postfix url for a given date and region.

        Parameters
        ----------
        demand_date : datetime.date
            Date
        region_id : string
            Region id. The values can be consulted in https://api.cammesa.com/demanda-svc/swagger-ui.html#/.

        Returns
        -------
        url_postfix : string
            Returns a specific postfix url for a given api call
        """
        url_postfix = "ObtieneDemandaYTemperaturaRegionByFecha?fecha=%4d-%02d-%02d&id_region=%s" % (demand_date.year, demand_date.month, demand_date.day, region_id)
        return url_postfix

    def _process_data(self, text_data):
        """
        It receives the raw text data and returns as a list of dicts.
        The raw data is in a list of dict format, so no particular transformation is necessary..

        Parameters
        ----------
        text_data :
            Raw text data.
        Returns
        -------
        dict_data : list of dicts
            Returns the processed data as a list of dicts
        """
        dict_data = json.loads(text_data)
        return dict_data

    def _to_df(self, dict_data, region_name):
        """
        It receives the data as a list of dicts and returns a Pandas dataframe.
        The 'temp' field is droped.

        Parameters
        ----------
        *args :
            The args parameters are specific of each inherited class.
            See the docstring of each for a detailed list of arguments.
        **kwargs :
            The kwargs parameters are specific of each inherited class.
            See the docstring of each for a detailed list of arguments.

        Returns
        -------
        dataframe : Pandas dataframe
            Returns the processed data as pandas dataframe
        """
        dataframe = pd.DataFrame(dict_data)
        dataframe["fecha"] = pd.to_datetime(dataframe["fecha"])
        dataframe = dataframe[dataframe["fecha"].dt.minute == 0]
        dataframe["fecha"] = dataframe["fecha"].dt.tz_localize(None)
        dataframe.drop(columns=["temp"], inplace=True, errors="ignore")
        dataframe.rename(columns={"fecha": "datetime", "dem": "demand"}, inplace=True)
        dataframe.set_index("datetime", inplace=True)
        dataframe["region"] = region_name
        return dataframe
    
    def etl(self, demand_date, region_dicts, save=True):
        """
        Calls the _download, _process_data and _to_df methods. It is the only one method exposed.
        It loads the pandas dataframe as a csv to the S3 bucket.

        Parameters
        ----------
        demand_date : datetime.date
            Date
        region_dicts : list of dicts
            list of dicts with all regions and corresponding region ids
        save : boolean
            if True the dataframe is save in the bucket as a csv
        Returns
        -------
        dataframe : Pandas dataframe
            Returns the processed data as pandas dataframe
        """
        list_df = []
        for region_dict in region_dicts:
            for region_id in region_dict["api_ids"]:
                text_data = self._download(demand_date, region_id)
                dict_data = self._process_data(text_data)
                list_df.append(self._to_df(dict_data, region_dict["region"]))
        dataframe = pd.concat(list_df)
        dataframe = dataframe.groupby(by=["datetime", "region"])["demand"].sum()
        if save and not dataframe.empty:
            csv_path = self._get_file_path(demand_date, "csv")
            load_df_csv_to_s3(dataframe, self.bucket, csv_path, index=True)
        return dataframe

class SMNApi(BaseApi):
    def __init__(self, bucket, stations_df):
        super().__init__(bucket)
        self.stations_df = stations_df
        self.url_prefix = "https://ssl.smn.gob.ar/dpd/descarga_opendata.php?file="
   
    def _to_df(self, dict_data):
        dataframe = pd.DataFrame(dict_data)
        if not dataframe.empty:
            dataframe = dataframe.merge(self.stations_df, how="left", on="station_raw")
            dataframe.drop(columns=["station_raw"], inplace=True)
            dataframe.fillna(value={"station": "ERROR"}, inplace=True)
            dataframe.set_index("datetime", inplace=True)
        return dataframe

    def etl(self, temp_date, save=True):
        text_data = self._download(temp_date)
        dict_data = self._process_data(text_data, temp_date)
        dataframe = self._to_df(dict_data)
        if save and not dataframe.empty:
            csv_path = self._get_file_path(temp_date, "csv")
            load_df_csv_to_s3(dataframe, self.bucket, csv_path, index=True)
        return dataframe
    

class ForecastSMNApi(SMNApi):

    def _get_url_postfix(self, temp_date):
        return "pron5d/pron%4d%02d%02d.txt" % (temp_date.year, temp_date.month, temp_date.day,)

    def _process_data(self, text_file, temp_date):
        for i, _ in enumerate(text_file.splitlines()):
            pass
        station_positions = range(POSITION_FIRST_STATION, i+1, HEADER_LINES + TOTAL_DATA_POINTS + LOWER_LINES + 1)
        data_positions = []
        for j in station_positions:
            data_positions = data_positions + list(range(j+HEADER_LINES+1, j+TOTAL_DATA_POINTS+POSITION_FIRST_STATION))
        temp_forecast = [] #{"station_name": {"datetime": temperature}}
        current_station = None
        current_datetime = None
        current_temperature = None
        current_dict = {}
        try:
            for i, line in enumerate(text_file.splitlines()):
                if line.strip() == "FORECAST NOT AVAILABLE":
                    self.logger.error(f"forecast - file_date: {temp_date} - FORECAST NOT AVAILABLE")
                    break
                if i in station_positions:
                    current_station = line.rstrip()
                current_dict["station_raw"] = current_station
                if i in data_positions:
                    current_datetime = line[1:15]
                    current_datetime = current_datetime[:3] + MONTHS_DICT[current_datetime[3:6]] + current_datetime[6:]
                    current_datetime = datetime.strptime(current_datetime, "%d/%b/%Y %H")
                    current_temperature = line[26:30].lstrip()
                    current_dict["datetime"] = str(current_datetime)
                    current_dict["temperature_forecast"] = current_temperature
                    current_dict["file_date"] = str(temp_date)
                    temp_forecast.append(current_dict)
                    current_dict = {}
        except Exception as e:
            self.logger.error(str(e))
        return temp_forecast


class HistoricalSNMPApi(SMNApi):

    def _get_url_postfix(self, temp_date):
        return "observaciones/datohorario%4d%02d%02d.txt" % (temp_date.year, temp_date.month, temp_date.day,)
  
    def _process_data(self, text_file, temp_date):
        temp_historical = [] #[{"station": "", "datetime": "", "temperature: ""}]
        try:
            for i, line in enumerate(text_file.splitlines()):
                current_dict = {}
                if line[0] in FILTER_ROWS:
                    continue
                current_station = line[48:].rstrip()
                current_datetime = line[:8] + " " + line[12:14]
                current_datetime = datetime.strptime(current_datetime, "%d%m%Y %H")
                if current_datetime.date() != temp_date:
                    self.logger.error(f"historical - file_date: {temp_date} - station: {current_station} - current_datetime: {current_datetime}")
                current_temperature = line[15:20].strip()
                current_dict["station_raw"] = current_station
                current_dict["datetime"] = str(current_datetime)
                current_dict["temperature"] = current_temperature
                current_dict["file_date"] = str(temp_date)
                temp_historical.append(current_dict)
        except Exception as e:
            self.logger.error(str(e))
        return temp_historical