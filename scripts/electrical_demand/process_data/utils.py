import pandas as pd
from datetime import timedelta
import pendulum


def get_new_data_date(current_date):
    current_date = pendulum.parse(current_date)
    new_data_date = current_date.subtract(days=1)
    return new_data_date

def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)

def new_rows(region_dicts, holidays_df, start_date, end_date=None):
    if end_date is None:
        end_date = start_date + timedelta(hours=24)
    end_date_adjusted = end_date + timedelta(days=4)
    df_list = []
    for region in region_dicts:
        datetime_index = pd.date_range(start=start_date, end=end_date_adjusted, freq='60min')[1:]
        df = pd.DataFrame(columns=["region"], index=datetime_index)
        df["region"] = region["region"]
        df["date"] = df.index.date
        df["date"] = pd.to_datetime(df["date"])
        df = df.reset_index().merge(holidays_df, how="left", left_on="date", right_on="date").set_index("index")
        df["day_type"].fillna("working_day", inplace = True)
        df.drop(columns=["date"], inplace=True)
        df_list.append(df)
    dataframe = pd.concat(df_list)
    dataframe.index.name = "datetime"
    return dataframe