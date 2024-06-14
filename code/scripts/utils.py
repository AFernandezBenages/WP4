import yaml

#Read configuration
def getConfiguration(path):
    with open(path, 'r') as f:
        try:
            config = yaml.safe_load(f)
            return config
        except yaml.YAMLError as exc:
            print(exc)

#Save new Configuration
def saveConfiguration(path, config):
    with open(path, 'w') as yaml_file:
        try:
            yaml.dump(config, yaml_file, default_flow_style=False)
        except yaml.YAMLError as exc:
            print(exc)

#Add N Lags as Predictors/Exogenous Variables
def addNLags(df, lags):
    lag_df= df.copy()
    for i in range(1, lags + 1):
        lag_df[f'lag_{i}'] = lag_df["Demand"].shift(i * 96).fillna(0)
    
    return lag_df.fillna(0)
