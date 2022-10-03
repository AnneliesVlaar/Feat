from __future__ import annotations
import sys
import pkg_resources

from PyQt5 import QtWidgets, uic

from feat.models.configuration import configuration


class UserInterface(QtWidgets.QMainWindow):
    def __init__(self):
        # call __init__ of parent class
        super().__init__()

        # load feat gui design
        uic.loadUi(pkg_resources.resource_stream("feat.views", "gui_feat.ui"), self)

        # slots and signals
        self.actionOpen.triggered.connect(self.open_feat_file)
        self.actionNew.triggered.connect(self.new_feat_file)

        self.student_comboBox.currentTextChanged.connect(self.update_student)

        self.NextButton.clicked.connect(self.next_student)

        self.copy_button.clicked.connect(self.copy)

    def open_feat_file(self):
        ## open file
        self.config_file, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, caption="Open feat file", filter="toml files (*.toml)"
        )
        # configure feat file
        self.config_toml()

        # initialise feedback windows
        self.init_feat()

    def new_feat_file(self):
        # # Get file location of toml file
        self.config_file, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, caption="Choose save location", filter="toml files (*.toml)"
        )
        # configure feat file
        self.config_toml()

        # load students names in toml file
        _student_f, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, caption="Open student list", filter="txt files (*.txt)"
        )
        self.config.add_students(_student_f)

        # load feedback file in toml fileft.
        _feedback_f, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, caption="Open feedback form", filter="toml files (*.toml)"
        )
        self.config.init_feedback(_feedback_f)

        # initialise feedback windows
        self.init_feat()

    def config_toml(self):
        # configure toml file
        self.config = configuration(self.config_file)

    def init_feat(self):
        # load data from toml file
        self.config_dict = self.config.fileioToml.open_toml()
        # Enable Text field edit
        self.read_only.setReadOnly(True)
        # add feedback lines and annotation fields to interface
        self.fblines = self.config.get_feedback_form()
        self.headline = {"head": {}}
        self.annotation = {"annot": {}}
        self.button = {"check": {}}
        for head in self.fblines:
            # add subject title to interface
            self.headline["head"][head] = QtWidgets.QLabel(head)
            self.vbox.addWidget(self.headline["head"][head])
            # add annotation field per subject title
            self.annotation["annot"][head] = QtWidgets.QTextEdit()
            self.vbox.addWidget(self.annotation["annot"][head])
            # add checkboxes with feedback lines
            self.button["check"][head] = {}
            for line in self.fblines[head]:
                self.button["check"][head][line] = QtWidgets.QCheckBox(
                    self.fblines[head][line]
                )
                self.vbox.addWidget(self.button["check"][head][line])

        # add student names to combobox
        for student in self.config_dict["students"]:
            full_name = self.config_dict["students"][student]["full_name"]
            self.student_comboBox.addItem(full_name, student)

        # initialise text box
        self.update_student()
        self.text_add()

        # slots and signals
        for head in self.headline["head"]:
            for box in self.button["check"][head]:
                self.button["check"][head][box].stateChanged.connect(self.check_box)

        for field in self.annotation["annot"]:
            self.annotation["annot"][field].textChanged.connect(self.add_annotations)

    def current_student(self):
        # index of current selected student
        current_student = self.student_comboBox.currentData()
        return current_student

    def update_student(self):
        feedback = self.config.get_feedback()
        current_student = self.current_student()

        for head in self.headline["head"]:
            # uncheck all checkboxes, check when checkbox name is in toml file
            for box in self.button["check"][head]:
                self.button["check"][head][box].setChecked(False)
                if box in feedback["checkbox"][current_student]:
                    self.button["check"][head][box].setChecked(True)

        # clear all annotations and show annotations from toml file
        for i, field in enumerate(self.annotation["annot"]):
            self.annotation["annot"][field].clear()
            try:
                text = feedback["annotations"][current_student][i]
            except:
                text = None
            self.annotation["annot"][field].append(text)

        # update read_only text field
        self.text_add()

    def text_add(self):

        # clear text field
        self.read_only.clear()

        # index of current selected student
        current_student = self.current_student()

        # add salutation text to text field
        first_line = (
            "Hoi " + self.config_dict["students"][current_student]["first_name"] + ","
        )
        self.read_only.append(first_line + "\r")

        # add headline to textfield
        for head in self.headline["head"]:
            self.read_only.append(f"[{head}]")

            # add annotations right under headline
            self.read_only.append(self.annotation["annot"][head].toPlainText())

            # add feedback lines to text field
            for line in self.button["check"][head]:
                if self.button["check"][head][line].isChecked():
                    self.read_only.append(
                        self.button["check"][head][line].text() + "\r"
                    )

    def check_box(self):
        current_student = self.current_student()

        feedback = []
        for head in self.headline["head"]:
            for box in self.button["check"][head]:
                if self.button["check"][head][box].isChecked():
                    feedback.append(box)

        # save checked feedback lines in toml
        self.config.update_feedback(current_student, "checkbox", feedback)

        # update read_only text field
        self.text_add()

    def add_annotations(self):
        current_student = self.current_student()

        annotations = []
        for field in self.annotation["annot"]:
            text = self.annotation["annot"][field].toPlainText()
            annotations.append(text)

        # save annotations in toml
        self.config.update_feedback(current_student, "annotations", annotations)

        # update read_only text field
        self.text_add()

    def next_student(self):
        index = self.student_comboBox.currentIndex()
        index += 1
        max_index = self.student_comboBox.count()
        if index < max_index:
            pass
        else:
            index = 0
        self.student_comboBox.setCurrentIndex(index)

    def copy(self):
        self.read_only.selectAll()
        self.read_only.copy()


def main():
    app = QtWidgets.QApplication(sys.argv)
    ui = UserInterface()
    ui.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
