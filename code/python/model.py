#Data Manipulation
import pandas as pd
import numpy as np
import requests as req
#Utilities
from sklearn.metrics import mean_absolute_error, root_mean_squared_error
import warnings
from tqdm import tqdm
from sklearn.model_selection import ParameterGrid
from sklearn.preprocessing import QuantileTransformer, MinMaxScaler
import utils

#Plots
warnings.filterwarnings("ignore")
warnings.simplefilter('ignore')


class Model():
    def __init__(self, dataset_path, config_path):
        super(Model, self).__init__()
        self.dataset = pd.read_csv(dataset_path, index_col=None)
        self.params = utils.getConfiguration(config_path)


    def splitDataset(self):
        self.dates = pd.to_datetime(self.dataset["Date"])
        self.dataset = self.dataset.drop(columns=["Date"], axis=1)
        
        # Target Variable
        y = self.dataset["Demand"]
        X = self.dataset.drop(columns=["Demand"], axis=1)
        self.col_names = list(X.columns)

        # 

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
        
        

    
