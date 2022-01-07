import toml

class configuration:
    def __init__(self):
        config = toml.load('config.toml')
        print(config['project']['project2']['name'])