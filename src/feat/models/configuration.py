import toml
import datetime


class fileIO:
    def __init__(self):
        pass

    def init_toml(self):
        
        # Check if configuration toml already exist
        try:
            open('test.toml', 'r').close()
        except IOError:
            # create configuration file
            open('test.toml', 'w').close()

        # initialize toml file with time and date of creation
        init_dict = {'title': "Feedback Realisation Exeperimenten Automatisering Konfiguration", 
                        "data": {"created": datetime.datetime.now()}}

        with open('test.toml', 'w') as f:
            toml.dump(init_dict,f)


class configuration:
    def __init__(self):

        fileio = fileIO()
        
        # initialise configuration toml
        fileio.init_toml()

        



        # config = toml.load('config.toml')
        # print(config['project']['project2']['name'])

if __name__ == "__main__":
    configuration()