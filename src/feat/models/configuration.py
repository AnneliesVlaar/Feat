import toml
import datetime
import pandas as pd



class fileIO:

    _conf_f = 'test.toml'

    def __init__(self):
        pass

    def init_toml(self):
        
        # Check if configuration toml already exist
        try:
            open(self._conf_f, 'r').close()

            # open toml to add time and date of last update
            config = self.open_toml()
            config['data']['last update'] = datetime.datetime.now()
            self.dump_toml(config)

        except IOError:
            # initialize toml file with time, date of creation, key for students and feedback
            init_dict = {'title': "Feedback Realisatie Experimenten Automatisering Konfiguratie", 
                            "data": {"created": datetime.datetime.now()},
                            'students': {},
                            'feedback': {"checkbox": {}, "annotations": {}}}
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
    def __init__(self):

        self.fileio = fileIO()

        # initialise configuration toml
        self.fileio.init_toml()

    def open_toml(self, tomlfile=None):
        if tomlfile:
            # open different toml file
            config = self.fileio.open_toml(tomlfile=tomlfile)
        else:
            # open configuration toml
            config = self.fileio.open_toml()
        return config
        
    def add_students(self, filename='test-student.txt'):
        # create dictionary of student data were key is the FullName
        header_list = ["FirstName", "FullName", "ID"]
        students = pd.read_csv(filename, sep=",", header=0, names=header_list, index_col='FullName').T.to_dict()

        # write student names to toml file
        self.fileio.update_toml("students", students)

        
        # initialise feedback
        feedback = self.get_feedback()
        # for checkboxes and annotations
        for type in feedback: 
            for student in students:
                try:
                    # check if student feedback key excists
                    feedback[type][student]
                except:
                    # create student feedback key if not already excist 
                    self.update_feedback(student, type, [])

    def get_feedback(self):
        config = self.open_toml()
        return config['feedback']

    def update_feedback(self, student, type, feedback):
        feedback_all = self.get_feedback()
        feedback_all[type][student] = feedback
        self.fileio.update_toml('feedback', feedback_all)


if __name__ == "__main__":
    configuration()