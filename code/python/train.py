#Data Manipulation
import pandas as pd
import numpy as np
import argparse
#Utilities
from sklearn.metrics import mean_absolute_error, root_mean_squared_error
import warnings
from tqdm import tqdm
from sklearn.model_selection import ParameterGrid
from sklearn.preprocessing import QuantileTransformer, MinMaxScaler

warnings.filterwarnings("ignore")
warnings.simplefilter('ignore')

parameters = {
    "dataset":{
        "path": "../olds/prueba_csv.csv",
        "trainingSize": .60,
        "validationSize": .2,
        "testSize": .2
    },
    "validation": {
        "n_splits" : 6
    }
}

#Parámetros para entrenar:
# ->
# ->
# ->



