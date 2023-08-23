import sys
import pkg_resources

from PyQt5.QtGui import QFont, QIcon, QMovie
from PyQt5 import QtWidgets, uic

import textwrap

from feat.models.configuration import configuration

FONT_STYLE_BUTTONS = QFont("Firacode NF", 12, QFont.Bold)
FONT_STYLE_TEXT = QFont("Firacode NF", 9)


class NewFileWindow(QtWidgets.QWidget):
    """
    This window appears when new file is selected from the menu.

    The file contains three line edits to provide the paths to 1) save the feat file 2) get the student file and 3) the feedback form.
    """

    def __init__(self):
        # call __init__ of parent class
        super().__init__()

        # load feat gui design
        uic.loadUi(
            pkg_resources.resource_stream("feat.views", "gui_feat_new_file.ui"), self
        )

        # set icon
        self.setWindowIcon(QIcon("FT-logo128.jpg"))

        # add icon to line edit and connect to file dialogs
        # savelocation icon-action
        save_action = self.line_save_location.addAction(
            QIcon("folder-open-regular.svg"), 0
        )
        save_action.triggered.connect(self.get_file_location)

        # studentlist icon-action
        student_action = self.line_students.addAction(
            QIcon("folder-open-regular.svg"), 0
        )
        student_action.triggered.connect(self.get_student_location)

        # feedbackform icon-action
        feedbackform_action = self.line_feedbackform.addAction(
            QIcon("folder-open-regular.svg"), 0
        )
        feedbackform_action.triggered.connect(self.get_feedbackform_location)

        # slots and signals
        self.save_location.clicked.connect(self.get_file_location)
        self.students_location.clicked.connect(self.get_student_location)
        self.feedbackform_location.clicked.connect(self.get_feedbackform_location)

    def get_file_location(self):
        # Get file location of toml file
        _save_loc, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, caption="Choose save location", filter="feat files (*.feat)"
        )
        self.line_save_location.setText(_save_loc)

    def get_student_location(self):
        # load students names in toml file
        _student_loc, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, caption="Open student list", filter="txt files (*.txt)"
        )
        self.line_students.setText(_student_loc)

    def get_feedbackform_location(self):
        # load feedback file in toml file.
        _feedbackform_loc, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, caption="Open feedback form", filter="toml files (*.toml)"
        )
        self.line_feedbackform.setText(_feedbackform_loc)

    def get_files(self):
        self.files_locations = {
            "save": self.line_save_location.text(),
            "students": self.line_students.text(),
            "feedbackform": self.line_feedbackform.text(),
        }
        return self.files_locations


class UserInterface(QtWidgets.QMainWindow):
    """Feat application can construct fast feedback text, based on a list of students and a feedback form. In annotations fields the user can add personal feedback."""

    def __init__(self):
        """Load design of feat app and add basic slots and signals.

        Slots and signals for feedback form and annotation fields are coupled in method init_feat.
        """
        # call __init__ of parent class
        super().__init__()

        # load feat gui design
        uic.loadUi(pkg_resources.resource_stream("feat.views", "gui_feat.ui"), self)

        # set icons
        self.setWindowIcon(QIcon("FT-logo128.jpg"))
        self.actionNew.setIcon(QIcon("plus-solid.svg"))
        self.actionOpen.setIcon(QIcon("folder-open-regular.svg"))
        self.actionSave.setIcon(QIcon("floppy-disk-solid.svg"))

        # Enable show feedback panel edit
        self.read_only.setReadOnly(True)
        self.read_only.setFont(FONT_STYLE_TEXT)

        # slots and signals
        # menu
        self.actionOpen.triggered.connect(self.open_feat_file)
        self.actionNew.triggered.connect(self.new_file_window)
        self.actionSave.triggered.connect(self.save_feat_file)

        # student selection
        self.student_comboBox.currentTextChanged.connect(self.update_student)
        self.NextButton.clicked.connect(self.next_student)
        self.NextButton2.clicked.connect(self.next_student)
        self.PreviousButton.clicked.connect(self.previous_student)
        self.PreviousButton2.clicked.connect(self.previous_student)

        # buttons
        self.copy_button.clicked.connect(self.copy)

    def new_file_window(self):
        """Open a second window where the user can provide information about the paths where file can be saved and found."""
        # open second window
        self.w = NewFileWindow()
        self.w.show()

        # connect the create button in the second window to new_feat_file function in UserInterface class
        self.w.create_new_file.clicked.connect(self.new_feat_file)

    def new_feat_file(self):
        """Menu option New. Create a new .feat file.

        In the second window 3 loctions are provided for save location of .feat file, for student names and feedback form.
        """

        # get locations from new file window
        files_locs = self.w.get_files()

        # create .feat file
        self.config_feat_file(files_locs["save"])

        # load students names in toml file
        self.config.add_students(files_locs["students"])

        # load feedback file in toml file.
        self.config.init_feedback(files_locs["feedbackform"])

        # initialise give feedback panel
        self.init_feat()

        # close new file window
        self.w.close()

    def open_feat_file(self):
        """Menu option New. Open .feat file to construct panels with list of students, feedback form and annotation fields."""

        # open file
        self.config_file, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, caption="Open feat file", filter="feat files (*.feat)"
        )
        if self.config_file == "":
            return
        else:
            # configure feat file
            self.config_feat_file(self.config_file)

            # initialise give feedback panel
            self.init_feat()

    def config_feat_file(self, file_path):
        """Configure .feat file. Create Toml structure if file is new, otherwise update date-data."""
        # configure toml file
        self.config = configuration(file_path)

    def init_feat(self):
        """Initialize feat application.

        From data in .feat file add check boxes with feedback lines. Add annotation field per feedback subject. Add greeting annotation field.
        Add students to combobox. Slots and signals for check boxes and annotation fields are coupled.
        """

        # load data from toml file
        self.feat_total = self.config.read_feat()
        # add feedback lines and annotation fields to interface
        self.fblines = self.config.get_feedback_form()
        self.headline = {"head": {}}
        self.annotation = {"annot": {}}
        self.button = {"check": {}}

        for head in self.fblines:
            # add subject title to interface
            self.headline["head"][head] = QtWidgets.QLabel(head)
            self.headline["head"][head].setFont(FONT_STYLE_BUTTONS)
            self.vbox.addWidget(self.headline["head"][head])
            # add annotation field per subject title
            self.annotation["annot"][head] = QtWidgets.QTextEdit()
            self.annotation["annot"][head].setFont(FONT_STYLE_TEXT)
            self.vbox.addWidget(self.annotation["annot"][head])
            # add checkboxes with feedback lines
            self.button["check"][head] = {}
            for line in self.fblines[head]:
                # manualy create multiline feedback lines
                text = self.fblines[head][line]
                split_text = textwrap.wrap(text, width=65)
                combine_text = "\n".join(split_text)

                self.button["check"][head][line] = QtWidgets.QCheckBox(combine_text)
                self.button["check"][head][line].setFont(FONT_STYLE_TEXT)
                self.vbox.addWidget(self.button["check"][head][line])

        # add greeting text field
        self.headline_sign_off = QtWidgets.QLabel("Afscheidsgroet")
        self.headline_sign_off.setFont(FONT_STYLE_BUTTONS)
        self.vbox.addWidget(self.headline_sign_off)

        self.annotation_sign_off = QtWidgets.QTextEdit()
        self.annotation_sign_off.setFont(FONT_STYLE_TEXT)

        # check if sign off text is present in feat file otherwise set placeholder text
        sign_off_text = self.config.get_sign_off()
        if sign_off_text:
            self.annotation_sign_off.append(sign_off_text)
        else:
            self.annotation_sign_off.setPlaceholderText("Doe hier de groetjes")

        # add sign off annotation field to give feedback panel
        self.vbox.addWidget(self.annotation_sign_off)

        # add student names to combobox
        for student in self.feat_total["students"]:
            full_name = self.feat_total["students"][student]["full_name"]
            self.student_comboBox.addItem(full_name, student)

        # initialise text box
        self.update_student()

        # slots and signals
        self.annotation_sign_off.textChanged.connect(self.add_sign_off)

        for head in self.headline["head"]:
            for box in self.button["check"][head]:
                self.button["check"][head][box].stateChanged.connect(self.check_box)

        for field in self.annotation["annot"]:
            self.annotation["annot"][field].textChanged.connect(self.add_annotations)

    def current_student(self):
        """Retrieve student_id of selected student in combobox.

        Returns:
            current_student: student_id of current selected student
        """
        # index of current selected student
        current_student = self.student_comboBox.currentData()
        return current_student

    def update_student(self):
        """Checks boxes and add annotation to annotation fields based on information in .feat file.

        Display of feedback text in read_only field is done by self.text_add()
        """

        feedback = self.config.get_feedback()
        current_student = self.current_student()

        for head in self.headline["head"]:
            # check when checkbox name is in feat file, uncheck otherwise
            for box in self.button["check"][head]:
                self.button["check"][head][box].blockSignals(True)
                if box in feedback["checkbox"][current_student]:
                    self.button["check"][head][box].setChecked(True)

                else:
                    self.button["check"][head][box].setChecked(False)
                self.button["check"][head][box].blockSignals(False)

        # clear annotation and show annotations from feat file
        for i, field in enumerate(self.annotation["annot"]):
            self.annotation["annot"][field].blockSignals(True)
            self.annotation["annot"][field].clear()
            try:
                text = feedback["annotations"][current_student][i]
                self.annotation["annot"][field].append(text)
            except:
                pass
            self.annotation["annot"][field].blockSignals(False)
            # TODO: create dictionary for annotation field, then check if annotation is present like with checkbox. Then blockSignals
            # is not needed anymore

        # update read_only show feedback panel
        self.text_add()

    def text_add(self):
        """Add text to display feedback text in read-only field.

        Based on the check boxes and annotation field the feedback text is constructed.
        """
        # clear show feedback panel
        self.read_only.clear()

        # get dictionary
        self.feat_total = self.config.get_feat()
        # TODO: check if updating feat_total is needed here and if it should be placed earlier

        # index of current selected student
        current_student = self.current_student()

        # add salutation text to show feedback panel
        first_line = (
            "Hoi " + self.feat_total["students"][current_student]["first_name"] + ","
        )
        self.read_only.append(first_line + "\r")

        for head in self.headline["head"]:
            # set headline main to salutation in give feedback field
            if head == "main":
                self.headline["head"][head].setText(first_line)
                if self.annotation["annot"][head].toPlainText() == "":
                    # set placeholder text if main annotation is empty
                    self.annotation["annot"][head].setPlaceholderText(
                        "Laat in een of twee regels weten wat je algehele indruk is."
                    )
            else:
                # add headline to textfield
                self.read_only.append(f"[{head}]")

            # add annotations in show feedback field
            self.read_only.append(self.annotation["annot"][head].toPlainText())
            # TODO: read annotations from feat file

            # add feedback lines to show feedback panel
            for line in self.button["check"][head]:
                if self.button["check"][head][line].isChecked():
                    self.read_only.append(
                        self.feat_total["feedbackform"][head][line] + "\r"
                    )

        # add sign-off
        sign_off_text = self.config.get_sign_off()
        if sign_off_text:
            self.read_only.append("\r" + self.feat_total["general text"]["sign-off"])
        else:
            self.annotation_sign_off.setPlaceholderText("Doe hier de groetjes")

    def check_box(self):
        """Create list of checked boxes, save configuration of check boxes in .feat file. And display feedback lines of checked boxes in read-only field with self.text_add()."""
        current_student = self.current_student()

        feedback = []
        for head in self.headline["head"]:
            for box in self.button["check"][head]:
                if self.button["check"][head][box].isChecked():
                    feedback.append(box)

        # save checked feedback lines in toml
        self.config.update_feedback(current_student, "checkbox", feedback)

        # update feat dictionary to match current feat file
        self.feat_total = self.config.get_feat()
        # TODO: check if this is needed here or if it is (implicitly) done somewhere else

        # update read_only show feedback panel
        self.text_add()

    def add_annotations(self):
        """Create list of annotations from annotation fields. Save annotation list to .feat file. Display annotations in read-only field with self.text_add()."""
        current_student = self.current_student()

        annotations = []
        for field in self.annotation["annot"]:
            text = self.annotation["annot"][field].toPlainText()
            annotations.append(text)

        # save annotations in toml
        self.config.update_feedback(current_student, "annotations", annotations)

        # update feat dictionary to match current feat file
        self.feat_total = self.config.get_feat()
        # TODO: check if this is needed here or if it is (implicitly) done somewhere else

        # update read_only show feedback panel
        self.text_add()

    def add_sign_off(self):
        """Save sign-off to .feat file and use self.text_add() to display sign-off in read-only field."""
        # get sign-off text and save to toml
        sign_off = self.annotation_sign_off.toPlainText()
        self.config.save_sign_off(sign_off)
        # add sign-off to read_only show feedback panel
        self.text_add()

    def next_student(self):
        """Displays feedback for next student below current student.

        If last student in the row is selected the next student is top one.
        """
        count = self.student_comboBox.count()
        if count == 0:
            return
        index = self.student_comboBox.currentIndex()
        index += 1
        if index < count:
            pass
        else:
            index = 0
        self.student_comboBox.setCurrentIndex(index)
        self.update_student()

    def previous_student(self):
        """Displays feedback for previous student above current student.

        If first student in the row is selected the previous student is bottom one.
        """
        count = self.student_comboBox.count()
        if count == 0:
            return
        index = self.student_comboBox.currentIndex()
        if index == 0:
            index = count
        else:
            pass
        index -= 1
        self.student_comboBox.setCurrentIndex(index)
        self.update_student()

    def copy(self):
        """The displayed feedback in the read-only field is copied to the clipboard"""
        self.read_only.selectAll()
        self.read_only.copy()

    def save_feat_file(self):
        """Menu option Save. Feat application auto-saves adjustments immediately.

        This save option is for the user to have a sense of control.
        """

        # save configurations of check-boxes
        try:
            self.config.save_feat_file()
        except:
            pass
        # TODO: Do not do auto-save? Create a real save option?


def main():
    app = QtWidgets.QApplication(sys.argv)
    ui = UserInterface()
    ui.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
