import toml
import datetime
import re
import pandas as pd
from pathlib import Path


RE_FIRST_LAST_NAME_ID = r"([\w'-]+) ([\w' -]+) (\(\d+\))"


class fileIO:
    def __init__(self, IOfile="test.toml"):
        self._config_f = IOfile
        pass

    def init_toml(self):

        # Check if configuration toml already exist
        try:
            open(self._config_f, "r").close()

            # open toml to add time and date of last update
            config = self.open_toml()
            try:
                config["data"]["last update"] = datetime.datetime.now()
            except:
                raise IOError
            self.dump_toml(config)

        except IOError:
            # initialize toml file with time, date of creation, key for students and feedback
            init_dict = {
                "title": "Feedback Realisatie Experiment Automatisering Konfiguratie",
                "data": {"created": datetime.datetime.now()},
                "students": {},
                "feedback": {"checkbox": {}, "annotations": {}},
            }
            self.dump_toml(init_dict)

    def open_toml(self):
        """Returns dictionary of data in toml file.

        Returns:
            dictionary: containing all data from toml file
        """
        config = toml.load(self._config_f)

        return config

    def dump_toml(self, dict):
        with open(self._config_f, "w") as f:
            toml.dump(dict, f)

    def update_toml(self, key, value):
        # get data of toml file as dictionary
        config = self.open_toml()
        # add data to dictionary
        config[key] = value
        # write new dictionary to toml file
        self.dump_toml(config)


class configuration:
    def __init__(self, toml_f):

        self.toml_f = toml_f
        self.fileioToml = fileIO(IOfile=toml_f)

        # initialise configuration toml
        self.fileioToml.init_toml()

    def open_toml(self, tomlfile=None):
        if tomlfile:
            # open different toml file
            self.fileioFB = fileIO(tomlfile)
            config = self.fileioFB.open_toml()
        else:
            # open configuration toml
            config = self.fileioToml.open_toml()
        return config

    def add_students(self, student_filename="test2-studenten.txt"):
        # create dictionary of student data were key is the sis_user_id
        if Path(student_filename).is_file():
            self.students = {}
            with open(student_filename, "r") as f:
                for line in f.readlines():
                    m = re.match(RE_FIRST_LAST_NAME_ID, line)
                    if m:
                        first_name, last_name, sis_user_id = m.group(1, 2, 3)
                        first_name = first_name.replace("_", " ")
                        self.students[sis_user_id] = {
                            "first_name": first_name,
                            "last_name": last_name,
                            "full_name": first_name + " " + last_name,
                        }
        else:
            print(f"File {student_filename} does not exits, skipping.")

        # write student names to toml file
        self.fileioToml.update_toml("students", self.students)

    def init_feedback(self, feedback_filename="feedbackpunten.toml"):
        # add feedback form to toml file
        feedback_form = self.open_toml(feedback_filename)
        self.fileioToml.update_toml("feedbackform", feedback_form)

        # initialise feedback per student
        feedback = self.get_feedback()
        # for checkboxes and annotations
        for type in feedback:
            for student in self.students:
                try:
                    # check if student feedback key excists
                    feedback[type][student]
                except:
                    # create student feedback key if not already excist
                    self.update_feedback(student, type, [])

    def get_feedback_form(self):
        config = self.open_toml()
        return config["feedbackform"]

    def get_feedback(self):
        config = self.open_toml()
        return config["feedback"]

    def update_feedback(self, student, type, feedback):
        feedback_all = self.get_feedback()
        feedback_all[type][student] = feedback
        self.fileioToml.update_toml("feedback", feedback_all)


if __name__ == "__main__":
    configuration()
