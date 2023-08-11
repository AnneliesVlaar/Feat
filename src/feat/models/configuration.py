import toml
import datetime
import re
import pandas as pd
from pathlib import Path


RE_FIRST_LAST_NAME_ID = r"([\w'-]+) ([\w' -]+) (\(\d+\))"


class fileIO:
    """Handle input and output of toml-structured files like .feat files."""

    def __init__(self, IOfile="test.toml"):
        self._toml_file = IOfile
        pass

    def init_feat_file(self):
        """Creates a structure in .feat file to add new information.

        If file exists, it updates time and data of last update.

        Raises:
            IOError: If new file is initialized, to create data structure.
        """
        # Check if configuration toml already exist
        try:
            open(self._toml_file, "r").close()

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
                "general text": {"sign-off": ""},
            }
            self.dump_toml(init_dict)

    def open_toml(self):
        """Returns dictionary of data in toml file.

        Returns:
            dictionary: containing all data from toml file
        """
        print("hellupie")
        with open(self._toml_file, "r", encoding="utf-8") as f:
            config = toml.load(f)

        return config

    def dump_toml(self, dict):
        """Writes data from dict to configuration file.

        Args:
            dict (dictionary): All data to write in configuration file.
        """
        with open(self._toml_file, "w", encoding="utf-8") as f:
            toml.dump(dict, f)

    def update_toml(self, feat, key, value):
        """Add information to configuration file.

        If information is added to a subkey of the configuration file. The key must be the name of the main key in the configuration file. And the value must be a dictionary containing all information belonging to that main key.

        Args:
            key (string): Name of the main key in configuration file
            value (string or dictionary): information to add to file
        """
        # get data of toml file as dictionary
        # config = self.open_toml()
        # add data to dictionary
        feat[key] = value
        # write new dictionary to toml file
        self.dump_toml(feat)


class configuration:
    """Get information .feat file. Return specific information read from .feat file. Feedback lines, student specific feedback and sign-off text."""

    def __init__(self, feat_f):
        """Initialize .feat file and create instance of fileIO to change information in .feat file.

        Args:
            feat_f (string): file location of the .feat file
        """

        self.fileioFeat = fileIO(IOfile=feat_f)

        # initialise configuration toml
        self.fileioFeat.init_feat_file()

        self.read_feat()

    def open_toml(self):
        return self.fileioToml.open_toml()

    def add_students(self, student_filename="teststudenten.txt"):
        """_summary_

        Args:
            student_filename (str, optional): List of students names with sis_user_ids. Structure: first_name lastname (student_id). Lines with # will be skipped. First names with spaces must be connected with "_" . Defaults to "test2-studenten.txt".
        """
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
            # TODO: create a good error message and return to main window

        # write student names to toml file
        self.update_feat("students", self.students)

    def init_feedback(self, feedback_filename="feedbackpunten.toml"):
        """Initialize feedback in .feat file to get the right structure for saving feedback per student. Feedback form is saved within .feat file.

        A "main" headline is added to create an annotation for main feedback.

        Args:
            feedback_filename (str, optional): Feedback form containing headlines and feedback lines to connect to checkboxes and annotation fields.
            In toml-structure where headlines with spaces must be put between " ", keys for feedback lines must be unique. Defaults to "feedbackpunten.toml".
        """
        # add feedback form to toml file
        self.fileioFB = fileIO(feedback_filename)
        feedback_form = self.fileioFB.open_toml()
        # TODO: create a good error message and return to main window

        feedback_form = {"main": {}} | feedback_form
        # TODO: combine main and feedback_form such that main is the first item in dictionary
        self.update_feat("feedbackform", feedback_form)

        # initialise feedback per student
        feedback = self.get_feedback()
        print(feedback)
        # for checkboxes and annotations
        for type in feedback:
            for student in self.students:
                try:
                    # check if student feedback key excists
                    feedback[type][student]
                except:
                    # create student feedback key if not already excist
                    self.update_feedback(student, type, [])

        # TODO If init_feedback is only called with new file. Feedback key cannot already exist. And we do not allow updating the feedback form (yet?)

    def read_feat(self):
        self.feat = self.fileioFeat.open_toml()
        return self.feat

    def update_feat(self, key, value):
        # save to .feat file
        self.fileioFeat.update_toml(self.feat, key, value)
        # update dictionary
        self.feat[key] = value

    def get_feat(self):
        return self.feat

    def get_feedback_form(self):
        """Read feedback form from .feat file.

        Args:
            feat (dict): dictonary of feat file

        Returns:
            dictionary: Containing feedback subject (main key) and feedback lines (key) -> dict[subject][line]
        """

        return self.feat["feedbackform"]

    def get_feedback(self):
        """Read configurations of checkboxes and annotations from all students in .feat file.

        Args:
            feat (dict): dictonary of feat file

        Returns:
            dictionary: containing per student list of checked boxes and annotations to construct feedback.
        """
        return self.feat["feedback"]

    def update_feedback(self, student, type, feedback):
        """Update the feedback in .feat file.

        Read feedback in .feat file. Update feedback and write it to .feat file. For 1 student and 1 feedback type (checkbox or annotations) at the time.

        Args:
            feat (dict): dictonary of feat file
            student (int): student_id of student to update feedback
            type (str): key of feedback type, checkbox or annotations
            feedback (str): value of the feedback
        """
        feedback_all = self.get_feedback()
        feedback_all[type][student] = feedback
        self.update_feat("feedback", feedback_all)

    def get_sign_off(self):
        """Return sign-off string saved in .feat file.

        Sign-off text is not student specific.

        Returns:
            str: Sign-off string from .feat file
        """
        return self.feat["general text"]["sign-off"]

    def save_sign_off(self, sign_off):
        """Save sign-off text in .feat file.

        Args:
            sign_off (str): Sign-off text to send your kind regards to students.
        """
        sign_off_dict = {"sign-off": sign_off}
        self.update_feat("general text", sign_off_dict)

    def get_main_annotation(self, student):
        """Return main annotation string saved in .feat file.

        Args:
            feat (dict): dictonary of feat file
            student (str): student_id of student

        Returns:
            str: main annotation string from .feat file for the specific student
        """
        try:
            main = self.feat["feedback"]["annotations"][student][0]
        except IndexError:
            main = ""

        return main

    def save_feat_file(self, feat):
        """Save the information to the feat file.

        Args:
            feat (dict): dictionary of the feat file
        """
        self.fileioToml.dump_toml(feat)
        # TODO: check if save_feat_file is not the same as update_feat


if __name__ == "__main__":
    configuration()
