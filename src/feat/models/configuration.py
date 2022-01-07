import toml
import datetime




class fileIO:

    _conf_f = 'test.toml'

    def __init__(self):
        pass

    def init_toml(self):
        
        # Check if configuration toml already exist
        try:
            open(self._conf_f, 'r').close()
        except IOError:
            # create configuration file
            open(self._conf_f, 'w').close()

        # initialize toml file with time and date of creation
        init_dict = {'title': "Feedback Realisation Exeperimenten Automatisering Konfiguration", 
                        "data": {"created": datetime.datetime.now()}}

        with open(self._conf_f, 'w') as f:
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