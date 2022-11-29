import s3fs
import pandas as pd
from electrical_demand.logger import get_logger

def load_holidays(file_path, bucket_path, file_name):
    dataframe = pd.read_csv(file_path)
    dataframe["date"] = pd.to_datetime(dataframe[["year", "month", "day"]])
    dataframe.set_index("date", inplace=True)
    dataframe.drop(columns=["year", "month", "day"], inplace=True)
    dataframe.to_csv("s3://" + bucket_path + "/" + file_name, index=True)
    return dataframe

def load_historical_demand(file_path, bucket_path, file_name):
    dataframe = pd.read_excel(file_path, header=3)
    dataframe.drop(columns=["AÑO", "MES", "N° MES", "N° DIA", "TIPO DIA", "DIA", "TOTAL"], inplace=True)
    dataframe["datetime"] = dataframe["FECHA"] + pd.to_timedelta(dataframe["HORA"], unit="h")
    dataframe.rename(columns={"SGO.DEL ESTERO": "SANTIAGO DEL ESTERO"}, inplace=True)
    dataframe.drop(columns=["HORA", "FECHA"], inplace=True)
    dataframe = pd.melt(dataframe, id_vars=["datetime"], var_name="region", value_name="demand")
    dataframe.set_index("datetime", inplace=True)
    dataframe.to_csv("s3://" + bucket_path + "/" + file_name)
    return dataframe

def load_file_to_s3(local_file_path, bucket, s3_file_path):
    with open(local_file_path, "r") as f:
        file = f.read()
    fs = s3fs.S3FileSystem(anon=False)
    with fs.open(bucket + "/" + s3_file_path, "w") as f:
        f.write(file)

def load_to_db(dataframe, table_model, client, keep_index=False):
    """
    Parameters
    ----------
    dataframe : Pandas dataframe
        Pandas dataframe to be load to the database
    table_model: SQAlchemy _DeclarativeBase
        Table model of the table where the dataframe is to be inserted.
    client : stock.database Client
        Database client.
    """
    logger = get_logger(load_to_db.__name__)
    try:
        if not dataframe.empty:
            if keep_index:
                dataframe[dataframe.index.name] = dataframe.index
            dataframe_dict = dataframe.to_dict(orient="records")
            fn_session = client.get_session()
            with fn_session() as session:
                table_model.insert(session, dataframe_dict)
                session.commit()
    except Exception as e:
        logger.error(f"Exception: {e}")
        raise e

def load_df_csv_to_s3(dataframe, bucket, csv_path, index=True):
    dataframe.to_csv("s3://" + bucket + "/" + csv_path, index=index)
    return dataframe