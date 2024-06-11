import pandas as pd
import numpy as np
import argparse
import joblib
import pathlib

#Leer parámetros
parser = argparse.ArgumentParser(
    prog='Interfície para la predicción de demanda eléctrica. Introducid los inputs de configuración:',
    #description='What the program does',
    #epilog='Text at the bottom of help'
)
parser.add_argument(
    "-ip",
    "--inicio_prediccion",
    help = "Especificad el día y hora a partir del cuál se debe iniciar la predicción.",
    default = "2020-07-16 00:00:00"
)
parser.add_argument(
    "-fp",
    "--final_prediccion",
    help = "Especificad el día y hora a partir del cuál se debe finalizar la predicción.",
    default = "2020-07-16 00:00:00"
)
parser.add_argument(
    "-df",
    "--date_format",
    help = "Introducid el formato de las fechas de predicción introducidas.",
    default = "%Y-%m-%d %H:%M:%S"
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

#Cargar Modelo
model = joblib.load(args.ruta_modelo)


#Realizar Predicción
y_pred = model.predict()
#Guardar Predicción
