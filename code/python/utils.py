import yaml

def getConfiguration(path):
    with open(path, 'r') as f:
        try:
            config = yaml.safe_load(f)
            return config
        except yaml.YAMLError as exc:
            print(exc)
    
