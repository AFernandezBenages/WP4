import pandas as pd
import numpy as np
import requests as req
import os
import utils

class Dataset():
    def __init__(self, config_path, consumption_path_csv):
        super(Dataset, self).__init__()
        self.config_path = config_path
        self.params = utils.getConfiguration(config_path)
        self.consumption_df = pd.read_csv(consumption_path_csv)
        

    def getMeteoDataset(self):
        latitud = self.params[""]
        longitud = self.params[""]
        pass
    



#Path to the Consumption Dataset
consumption_path_csv = ""
#Path tp the Configuration File
configuration_file_path = "./data/config.yaml"
dataset = Dataset(configuration_file_path)