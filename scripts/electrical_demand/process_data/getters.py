import json
import s3fs
import pandas as pd
from electrical_demand.logger import get_logger
from electrical_demand.database.models import Demand



def get_demand(client, region):
    query = Demand.select_query(region)
    dataframe = client.get_dataframe(query, index_col="datetime", parse_dates=True)
    return dataframe

def get_csv_path(date):
    return "csv/year=%4d/month=%02d/%02d.csv" % (date.year, date.month, date.day, )

def get_region_dicts(general_bucket):
    region_dicts = get_file_from_s3(general_bucket, "region_dicts.json")
    region_dicts = json.loads(region_dicts)
    return region_dicts

def get_csv_from_s3(bucket, csv_path, index_col=None, parse_dates=False):
    """
    Parameters
    ----------
    csv_path : str
        Path of the csv file.

    Returns
    -------
    dataframe : Pandas dataframe
        csv file as a Pandas dataframe.
    """
    logger = get_logger(get_csv_from_s3.__name__)
    try:
        dataframe = pd.read_csv("s3://" + bucket + "/" + csv_path, index_col=index_col, parse_dates=parse_dates, encoding="utf-8")
        if index_col:
            dataframe.index.name = index_col
        return dataframe
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")

def get_file_from_s3(bucket, file_path):
    logger = get_logger(get_file_from_s3.__name__)
    try:
        fs = s3fs.S3FileSystem(anon=False)
        with fs.open(bucket + "/" + file_path, "r") as f:
            file = f.read()
        return file
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
