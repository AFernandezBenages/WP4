import pandas as pd
import numpy as np
import requests as req
import argparse
import joblib
import pathlib

def getWeatherData(self):
    lat = self.params["weatherbit"]["latitude"]
    lon = self.params["weatherbit"]["longitude"]
    start_date = self.params["prediction"]["startDate"]
    end_date = self.params["prediction"]["startDate"]
    key = self.params["weatherbit"]["key"]
    forecast_weather_data = 'https://api.weatherbit.io/v2.0/history/hourly?lat={}&lon={}&start_date={}&end_date={}&tz=local&key={}'.format(lat, lon, start_date, end_date, key)
    response = req.get(forecast_weather_data)
    if response.status_code == 200:
        data = response.json()
        print(data)
    else:
        print("Error al realizar la solicitud de Predicción de Datos Meteorológicos")


#Leer parámetros
parser = argparse.ArgumentParser(
    prog='Interfície para la predicción de demanda eléctrica. Introducid los inputs de configuración:'
)
parser.add_argument(
    "-rm",
    "--ruta_modelo",
    type = pathlib.Path,
    help = "Introducid la ruta del modelo a utilizar en la predicción.",
    default = "/results/models/xgboost_model.pkl" 
)

args = parser.parse_args()

#Cargar Datos
#1- Request a las base de datos
#2- Request API Weather
#3- Construir dataframe
 
#Cargar Modelo
model = joblib.load(args.ruta_modelo)

#Realizar Predicción
y_pred = model.predict()

#Guardar Predicción en base de datos
