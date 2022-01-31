import toml
import datetime
import pandas as pd
import csv




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
        init_dict = {'title': "Feedback Realisatie Experimenten Automatisering Konfiguratie", 
                        "data": {"created": datetime.datetime.now()}}

        # write init data to toml
        self.dump_toml(init_dict)

    def open_toml(self, tomlfile=_conf_f):
        """Returns dictionary of data in toml file.

        Returns:
            dictionary: containing all data from toml file
        """
        config = toml.load(tomlfile)
        
        return config

    def dump_toml(self, dict):
        with open(self._conf_f, 'w') as f:
            toml.dump(dict,f)

    def update_toml(self, key, value):
        # get data of toml file as dictionary
        config = self.open_toml()
        # add data to dictionary
        config[key] = value
        # write new dictionary to toml file
        self.dump_toml(config)



class configuration:
    def __init__(self, filename):

        self.fileio = fileIO()

        # initialise configuration toml
        self.fileio.init_toml()

        # add students to toml file
        self.add_students(filename)

    def open_toml(self, tomlfile=None):
        if tomlfile:
            config = self.fileio.open_toml(tomlfile=tomlfile)
        else:
            config = self.fileio.open_toml()
        return config
        
    def add_students(self, filename):
        # create dictionary of student data were key is the FullName
        header_list = ["FirstName", "FullName", "ID"]
        students = pd.read_csv(filename, sep=",", header=0, names=header_list, index_col='FullName').T.to_dict()

        # write student names to toml file
        self.fileio.update_toml("students", students)
 


if __name__ == "__main__":
    configuration('test-student.txt')