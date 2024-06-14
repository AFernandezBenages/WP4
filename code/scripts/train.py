#Data Manipulation
import pandas as pd
import requests as req

#Utilities
import warnings
from sklearn.preprocessing import QuantileTransformer
import utils
from tqdm import tqdm
from sklearn.model_selection import ParameterGrid
from sklearn.metrics import mean_absolute_error

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
        try:
            #Read Dataset
            self.dataset = pd.read_csv(dataset_path, index_col=None)

            #Read Configuration Params
            self.params = utils.getConfiguration(config_path)

            #Data Preprocessing
            
            #Prepare Dataset
            self.prepareDataset()

            #Grid Search
            self.gridSearch()

            #Save new configuration parameters
            utils.saveConfiguration(self.params)

            #Train Model
            self.train()

            print("Clase inicializada correctamente.")
        except:
            print("Ha habido un error al inicializar la clase.")

    def prepareDataset(self):

        #Convert dates to datetime format
        dates = pd.to_datetime(self.dataset["Date"])
        self.dataset = self.dataset.drop(columns=["Date"], axis=1)

        #Apply Quantile Transformation to Demand
        self.quantile_transformer = QuantileTransformer(output_distribution='uniform', random_state=42) 
        self.dataset["Demand"] = self.quantile_transformer.fit_transform(self.dataset["Demand"].values.reshape(-1, 1)).flatten() 
        
        #Add Lags as Predictors
        self.dataset = utils.addNLags(self.dataset, 20)

        # Target Variable
        y = self.dataset["Demand"]
        X = self.dataset.drop(columns=["Demand"], axis=1)
        self.col_names = list(X.columns)

        # Training Size
        trainingSize = int(self.params["training"]["trainingSize"] * len(self.dataset))

        #Split Dataset
        self.X_train, self.y_train = X.loc[:trainingSize, :].copy(), y.loc[:trainingSize].copy()
        self.X_test, self.y_test = X.loc[trainingSize:, :].copy(), y.loc[trainingSize:].copy()

        #Split Dates 
        self.X_train_dates = dates.loc[:trainingSize].copy()
        self.X_test_dates = dates.loc[trainingSize:].copy()

    #Plots the Demand curve coloring the division of training and test.
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

    #Save XGBoost Model
    def saveModel(self):
        try:
            joblib.dump(self.model, self.params['training']['save_path'])
        except:
            print("Ha habido un error al guardar el modelo")

    #Train Model
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

        self.saveModel()

    #Finds the combination of parameters that gets better results
    def gridSearch(self):
        paramsXGB = {
            'max_depth': [7, 8],
            'learning_rate': [0.005, 0.003],
            'gamma': [7, 8, 9],
            'colsample_bytree' : [0.7, 0.9, 1],
            'colsample_bynode': [ 0.7, 0.9, 1],
            'n_estimators': [1300]
        }
        best_mae = float('inf')
        config = {}
        for param in tqdm(ParameterGrid(paramsXGB), total=len(list(ParameterGrid(paramsXGB)))):
            max_depth = param.get('max_depth')
            n_estimators = param.get('n_estimators')
            lr = param.get('learning_rate')
            gamma = param.get('gamma')
            colsample_bytree = param.get('colsample_bytree')
            colsample_bynode = param.get('colsample_bynode')
            regressorXGBR = XGBRegressor(objective='reg:absoluteerror', n_estimators=n_estimators, learning_rate = lr, max_depth=max_depth, colsample_bytree = colsample_bytree, colsample_bynode = colsample_bynode, gamma=gamma, random_state=123, eval_metric='mae', early_stopping_rounds=100)
            
            regressorXGBR.fit(
                X = self.X_train,
                y = self.y_train,
                verbose=0
            )  
            y_pred = regressorXGBR.predict(self.X_test)
            y_pred = self.quantile_transformer.inverse_transform(y_pred.reshape(-1, 1)).flatten()

            mae = mean_absolute_error(self.y_test, y_pred)
            if mae < best_mae: 
                best_mae = mae
                config = param
            print(f"MAE: {mae}, n_Estimators: {n_estimators}, Learning_rate: {lr}, Max_depth: {max_depth}, Gamma: {gamma}, Col_Sample_By_Tree: {colsample_bytree}, Col_Sample_By_Node: {colsample_bynode}")
        config["mae"] = best_mae
        self.setNewConfiguration(config)

    #Sets the parameters of the grid search results, to the configuration field
    def setNewConfiguration(self, config):
        self.params["xgboost"]["max_depth"] = config["max_depth"]
        self.params["xgboost"]["gamma"] = config["gamma"]
        self.params["xgboost"]["n_estimators"] = config["n_estimators"]
        self.params["xgboost"]["colsample_bytree"] = config["max_decolsample_bytreepth"]
        self.params["xgboost"]["colsample_bynode"] = config["colsample_bynode"]
        self.params["xgboost"]["learning_rate"] = config["learning_rate"]

if '__name__' == '__main__':
    model = Model("/olds/prueba_csv.csv", "/data/config.yaml")
    model.train()

        
        

    
