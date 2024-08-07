import pandas as pd
import numpy as np
import time
from sklearn.metrics import mean_absolute_error, root_mean_squared_error, mean_absolute_percentage_error
from xgboost import XGBRegressor
import psutil

parameters = {
    "dataset":{
        "path": "./data/data_casal_montserratina/LaMonserratina_CLEAN.csv",
        "trainingSize": .60,
        "validationSize": .20,
        "testSize": .20
    },
    "validation": {
        "n_splits" : 6
    },
    "lstm":{
        "epochs": 20,
        "batch_size": 64,
        "lr": 0.0001
    }
}
def addNLags(df, lags_list):
    lag_df = df.copy()
    for lag in lags_list:
        lag_df[f'lag_{lag}'] = lag_df["Demanda_kWh"].shift(lag * 24)

    return lag_df.fillna(0)

def calculate_metrics(y_true, y_pred):    
    # MAE (Mean Absolute Error)
    mae = mean_absolute_error(y_true, y_pred)
    # RMSE (Root Mean Squared Error)
    rmse = root_mean_squared_error(y_true, y_pred)
    # MAPE (Mean Absolute Percentage Error)
    mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100
    # MDAPE (Median Absolute Percentage Error)
    mdape = np.median(np.abs((y_true - y_pred) / y_true)) * 100
    
    return mae, rmse, mape, mdape
def parseData(df):
    for col in df:
        df[col] = df[col].astype(float)
    return df

def medir_recursos():
    current_time = time.time()
    proceso = psutil.Process()
    mem = proceso.memory_info().rss / (1024 * 1024)  # MB
    mem_percent = proceso.memory_percent()
    cpu = psutil.cpu_percent()
    return current_time, mem, mem_percent, cpu

start_time, mem_inicio, mem_start_percent, cpu_inicio = medir_recursos()

df = pd.read_csv(parameters["dataset"]["path"], index_col=None)
df["Date"] = pd.to_datetime(df["Date"])
dates = df["Date"]
dates = pd.to_datetime(dates)
df = addNLags(df, [1, 2, 5, 7])
df = df.drop(columns=["Date"], axis=1)
df = parseData(df)
df.columns = df.columns.map(str)

y = df["Demanda_kWh"]
X = df.drop(columns=["Demanda_kWh", "pressure_msl_hPa", "dew_point_2m_C", "surface_pressure_hPa",
    "cloud_cover_%", "cloud_cover_high_%", "et0_fao_evapotranspiration_mm", "vapour_pressure_deficit_kPa",
    "wind_speed_10m_km/h", "wind_direction_10m_º", "wind_gusts_10m", "terrestrial_radiation_W/m2",
    "DayOfYear", "DayOfWeek", "temp_cluster", "Season", "Month", "relative_humidity_2m_%", "Month_sin", "is_day", "DayOfYear_sin", "sunshine_duration_sec",
    "direct_radiation_W/m2", "global_tilted_irradiance_W/m2", "DayOfYear_cos", "DayOfWeek_cos", "apparent_temperature_C", "Temp_interna_Modulo_C", "Year"], axis=1)
col_names = list(X.columns)

trainingSize = int(parameters["dataset"]["trainingSize"] * df.shape[0])
validationSize = trainingSize + int(parameters["dataset"]["validationSize"] * df.shape[0])

X_train, y_train = X.loc[:trainingSize, :].copy(), y.loc[:trainingSize].copy()
X_val, y_val = X.loc[trainingSize:validationSize, :].copy(), y.loc[trainingSize:validationSize].copy()
X_test, y_test = X.loc[validationSize:, :].copy(), y.loc[validationSize:].copy()

X_train_dates = dates.loc[:trainingSize].copy()
X_val_dates = dates.loc[trainingSize:validationSize].copy()
X_test_dates = dates.loc[validationSize:].copy()
#print(f"Total Lags: {len(df)}")
#print(f"Training Size:{len(X_train)}")
#print(f"Test Size: {len(X_test)}")
X.columns


xgboost = XGBRegressor(n_estimators=1000, random_state=123, learning_rate=0.03, max_depth=7)
xgboost.fit(X_train, y_train, eval_set=[(X_val, y_val)], 
           eval_metric='mae', 
           early_stopping_rounds=100)
y_pred = xgboost.predict(X_test)
mae, rmse, mape, mdape = calculate_metrics(y_test, y_pred)
#print(f"MAE: {mae}, RMSE: {rmse}, MAPE: {mape}, MdAPE: {mdape}")

def medir_recursos():
    current_time = time.time()
    proceso = psutil.Process()
    mem = proceso.memory_info().rss / (1024 * 1024)  # MB
    mem_percent = proceso.memory_percent()
    cpu = psutil.cpu_percent()
    return current_time, mem, mem_percent, cpu
start_time, mem_inicio, mem_start_percent, cpu_inicio = medir_recursos()

"""
CÓDIGO
"""
end_time, mem_fin,mem_end_percent,cpu_fin = medir_recursos()

print(f"Tiempo total: {end_time - start_time:.2f} segundos")
print(f"Memoria: inicio {mem_inicio:.2f} MB, fin {mem_fin:.2f} MB, diferencia {mem_fin - mem_inicio:.2f} MB")
print(f"Memoria Porcentual: inicio {mem_start_percent:.2f}%, fin {mem_end_percent:.2f}%, diferencia {mem_end_percent - mem_start_percent:.2f}%")
print(f"CPU: inicio {cpu_inicio}%, fin {cpu_fin}%")
