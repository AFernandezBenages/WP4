# Data Manipulation
import numpy as np
import pandas as pd
import os

# for API requests
import openmeteo_requests
import requests_cache
from retry_requests import retry

lat = 41.32062    # casal de la montserratina
lon = 2.0105984   # casal de la montserratina
start_date = '2021-01-01' # YYYY-MM-DD
end_date = '2024-05-07' # YYYY-MM-DD
url = "https://archive-api.open-meteo.com/v1/archive"


def make_request(url, lat, lon, start_date, end_date):
    # Setup the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession('.cache', expire_after = -1)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)

    # Make sure all required weather variables are listed here
    # The order of variables in hourly or daily is important to assign them correctly below

    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": 
            [
                "temperature_2m", "relative_humidity_2m", "dew_point_2m",
                "precipitation", "shortwave_radiation",
                "diffuse_radiation", "direct_normal_irradiance"
            ],
    }

    responses = openmeteo.weather_api(url, params=params)
    response = responses[0]

    # Process hourly data. The order of variables needs to be the same as requested.
    hourly = response.Hourly()
    hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
    hourly_relative_humidity_2m = hourly.Variables(1).ValuesAsNumpy()
    hourly_dew_point_2m = hourly.Variables(2).ValuesAsNumpy()
    hourly_precipitation = hourly.Variables(5).ValuesAsNumpy()
    hourly_shortwave_radiation = hourly.Variables(43).ValuesAsNumpy()
    hourly_diffuse_radiation = hourly.Variables(45).ValuesAsNumpy()
    hourly_direct_normal_irradiance = hourly.Variables(46).ValuesAsNumpy()

    hourly_data = {"Date": pd.date_range(
        start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
        end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
        freq = pd.Timedelta(seconds = hourly.Interval()),
        inclusive = "left"
    )}
    hourly_data["temperature_2m_C"] = hourly_temperature_2m
    hourly_data["relative_humidity_2m_%"] = hourly_relative_humidity_2m
    hourly_data["dew_point_2m_C"] = hourly_dew_point_2m
    hourly_data["precipitation_mm"] = hourly_precipitation
    hourly_data["shortwave_radiation_W/m2"] = hourly_shortwave_radiation
    hourly_data["diffuse_radiation_W/m2"] = hourly_diffuse_radiation
    hourly_data["direct_normal_irradiance_W/m2"] = hourly_direct_normal_irradiance

    return pd.DataFrame(data = hourly_data)

if __name__ == "__main__":
    df = make_request(url, lat, lon, start_date, end_date)
    
    # Format the date column
    df['Date'] = df['Date'].dt.strftime("%Y-%m-%d %H:%M:%S")
    df["Date"] = pd.to_datetime(df["Date"], format="%Y-%m-%d %H:%M:%S")

    # Resample the dataset
    df.set_index("Date", inplace=True)
    df = df.groupby(df.index).first().resample('15T').interpolate(method='linear')





