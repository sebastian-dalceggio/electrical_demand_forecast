SELECT EXTRACT(HOUR FROM datetime) AS hour, SUM(demand) AS demand, SUM(demand_forecast) AS demand_forecast
FROM demand
WHERE DATE(datetime) = '{day}'
GROUP BY EXTRACT(HOUR FROM datetime);