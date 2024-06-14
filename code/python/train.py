#Data Manipulation
import pandas as pd
import requests as req

#Utilities
import warnings
from sklearn.preprocessing import QuantileTransformer
import utils

#Model
from xgboost import XGBRegressor
import joblib

#Plots
import plotly.graph_objects as go

warnings.filterwarnings("ignore")
warnings.simplefilter('ignore')


class Model():
    def __init__(self, dataset_path, config_path):
        super(Model, self).__init__()
        #Read Dataset
        try:
            #Read Dataset
            self.dataset = pd.read_csv(dataset_path, index_col=None)

            #Read Configuration Params
            self.params = utils.getConfiguration(config_path)

            #Data Preprocessing
            
            #Prepare Dataset
            self.prepareDataset()

            print("Clase inicializada correctamente.")
        except:
            print("Ha habido un error al inicializar la clase.")

    def prepareDataset(self):
        self.dates = pd.to_datetime(self.dataset["Date"])
        self.dataset = self.dataset.drop(columns=["Date"], axis=1)

        #Apply Quantile Transformation to Demand
        quantile_transformer = QuantileTransformer(output_distribution='uniform', random_state=42) 
        self.dataset["Demand"] = quantile_transformer.fit_transform(self.dataset["Demand"].values.reshape(-1, 1)).flatten() 
        
        #Add Lags as Predictors
        self.dataset = utils.addNLags(self.dataset, 20)

        # Target Variable
        y = self.dataset["Demand"]
        X = self.dataset.drop(columns=["Demand"], axis=1)
        self.col_names = list(X.columns)

        # Training Size
        trainingSize = int(self.params["dataset"]["trainingSize"] * len(self.dataset))

        #Split Dataset
        self.X_train, self.y_train = X.loc[:trainingSize, :].copy(), y.loc[:trainingSize].copy()
        self.X_test, self.y_test = X.loc[trainingSize:, :].copy(), y.loc[trainingSize:].copy()

        #Split Dates 
        self.X_train_dates = self.dates.loc[:trainingSize].copy()
        self.X_test_dates = self.dates.loc[trainingSize:].copy()

    def plotDatasetSplit(self):
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=self.X_train_dates, y=self.y_train, mode="lines", name="Train"))
        fig.add_trace(go.Scatter(x=self.X_test_dates, y=self.y_test, mode="lines", name="Test"))
        fig.update_layout(
            title = "Dataset Partition",
            xaxis_title = "Date",
            yaxis_title ="Demand (kWh)",
            width = 1000,
            height = 400,
            margin = dict(l=30, r=20, t=35, b=60),
            legend = dict(
                orientation = "h",
                yanchor = "bottom",
                y = 1.05,
                xanchor = "right",
                x=1
            )
        )
        fig.show()

    def saveDataset(self):
        joblib.dump(self.model, '/results/xgboost_model.pkl')

    def train(self):
        try:
            xgboost = self.params["xgboost"]
            self.model =  XGBRegressor(
                objective='reg:absoluteerror', 
                n_estimators=xgboost["n_estimators"], 
                learning_rate = xgboost["learning_rate"], 
                max_depth=xgboost["max_depth"], 
                colsample_bytree = xgboost["colsample_bytree"], 
                colsample_bynode = xgboost["colsample_bynode"], 
                gamma=xgboost["gamma"], 
                random_state=123
            )
            self.model.fit(
                X = self.X_train,
                y = self.y_train,
                verbose=0
            )
        except:
            print("Ha habido un error al realizar el entrenamiento del modelo")

        self.saveDataset()


model = Model("/olds/prueba_csv.csv", "/data/config.yaml")


        
        

    
