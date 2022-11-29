SELECT EXTRACT(HOUR FROM datetime) AS hour, demand, demand_forecast
FROM demand
WHERE region = '{region}' and  DATE(datetime) = '{day}';