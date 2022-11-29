from fastapi import FastAPI
import os
from electrical_demand.database.client import ComplexClient
from electrical_demand.database_api.config import DATABASE_TYPE, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_NAME
from electrical_demand.logger import get_logger
logger = get_logger("api", "INFO")

app = FastAPI()
current_path = os.path.dirname(__file__)
client = ComplexClient(DATABASE_TYPE, DATABASE_NAME, DATABASE_HOST, DATABASE_USER, DATABASE_PASSWORD)

@app.get("/get-region/{region}/{day}")
def get_region(region, day):
    logger.info("region: " + region + "; day: " + day)
    if region == "TOTAL":
        query_path = "total.sql"
    else:
        query_path = "regions.sql"
    # region = region.replace("_", " ")
    # day = day.replace("_", " ")
    with open(current_path + "/api_queries/" + query_path, "r") as file:
        query = file.read()
        if region == "TOTAL":
            query = query.format(day=day)
        else:
            query = query.format(region=region, day=day)
            print(query)
        data = client.get_dataframe(query)
    logger.info("data: " + data.to_json())
    return {"data": data.to_json()}