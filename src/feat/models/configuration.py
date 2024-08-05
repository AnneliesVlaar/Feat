import toml
import datetime
import re
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
                "title": "Feedback Realisatie Experiment Aansturing Konfiguratie",
                "data": {"created": datetime.datetime.now()},
                "students": {},
                "feedback": {"checkbox": {}, "annotations": {}, "grades": {}},
                "general text": {"sign-off": ""},
            }
            self.dump_toml(init_dict)

    def open_toml(self):
        """Opens toml file and creates dictionary from content.

        Returns:
            dictionary: containing all data from toml file
        """
        with open(self._toml_file, "r", encoding="utf-8") as f:
            content = toml.load(f)

        return content

    def dump_toml(self, dict):
        """Writes data from dictionary to toml file.

        Args:
            dict (dictionary): All data to write in toml file.
        """
        with open(self._toml_file, "w", encoding="utf-8") as f:
            toml.dump(dict, f)

    def update_toml(self, feat, key, value):
        """Add information to toml file.

        If information is added to a subkey of the toml file,
        the key must be the name of the main key in the toml file
        and the value must be a dictionary containing all information belonging to that main key.

        Args:
            feat (dictionary): compleet content of the toml file
            key (string): Name of the main key in toml file
            value (string or dictionary): information to add to file
        """

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
        # create instance of fileIO to open en dump content of feat file.
        self.fileioFeat = fileIO(IOfile=feat_f)

        # initialise feat file
        self.fileioFeat.init_feat_file()

        # create dictionary from feat file
        self.read_feat()

    def add_students(self, student_filename):
        """Add students to feat file.

        Read students from seperate text file. Structure: first_name lastname (student_id).
        Lines with # will be skipped. First names with spaces must be connected with "_" .

        Args:
            student_filename (str): List of students names with sis_user_ids.
        """
        # create dictionary of student data were key is the sis_user_id
        if Path(student_filename).is_file():
            self.students = {}
            with open(student_filename, "r", encoding="utf-8") as f:
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

    def init_feedback(self, feedback_filename):
        """Initialize feedback in .feat file to get the right structure for saving feedback per student. Feedback form is saved within .feat file.

        Feedback form is in toml-structure where headlines with spaces must be put between " ", keys for feedback lines must be unique.
        A "main" headline is added to create an annotation for main feedback, which is unique per student.

        Args:
            feedback_filename (str): Feedback form containing headlines and feedback lines to connect to checkboxes and annotation fields.
        """
        # Open feedback form and create feedback form dictionary
        self.fileioFB = fileIO(feedback_filename)
        feedback_form = self.fileioFB.open_toml()
        # TODO: create a good error message and return to main window

        # add main headline as first item in feedback form dictionary
        feedback_form = {"main": {}} | feedback_form
        # add feedback form to feat file
        self.update_feat("feedbackform", feedback_form)

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

        # TODO If init_feedback is only called with new file. Feedback key cannot already exist. And we do not allow updating the feedback form (yet?)

    def read_feat(self):
        """Read feat file and return dictionary from content.

        Returns:
            dictionary: compleet content from feat file

        """
        self.feat = self.fileioFeat.open_toml()
        return self.feat

        # TODO: check if this function is needed

    def update_feat(self, key, value):
        """Update information in feat file.

        Args:
            key (string): Name of the main key in toml file
            value (string or dictionary): information to add to file
        """
        # save to .feat file
        self.fileioFeat.update_toml(self.feat, key, value)
        # update dictionary
        self.feat[key] = value

        # TODO new dictionary is created twice, here and in update_toml. See if it can be simpeler.

    def get_feat(self):
        """Get dictionary of feat file without opening feat file.

        Returns:
            dictionary: compleet content of feat file
        """
        return self.feat

    def get_feedback_form(self):
        """Read feedback form from .feat file.

        Returns:
            dictionary: Containing feedback subject (main key) and feedback lines (key) -> dict[subject][line]
        """

        return self.feat["feedbackform"]

    def get_feedback(self):
        """Read configurations of checkboxes and annotations from all students in .feat file.

        Returns:
            dictionary: containing per student list of checked boxes and annotations to construct feedback.
        """
        return self.feat["feedback"]

    def update_feedback(self, student, type, feedback):
        """Update the feedback in .feat file.

        Read feedback in .feat file. Update feedback and write it to .feat file. For 1 student and 1 feedback type (checkbox or annotations) at the time.

        Args:
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

    def save_feat_file(self):
        """Save the information to the feat file."""
        self.fileioFeat.dump_toml(self.feat)

        # TODO: check if save_feat_file is not the same as update_feat


if __name__ == "__main__":
    configuration()
