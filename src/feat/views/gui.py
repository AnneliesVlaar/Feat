import sys
import pkg_resources

from PyQt5.QtGui import QFont, QIcon
from PyQt5 import QtWidgets, uic

import textwrap

from feat.models.configuration import configuration

FONT_STYLE_BUTTONS = QFont("Firacode NF", 12, QFont.Bold)
FONT_STYLE_TEXT = QFont("Firacode NF", 9)


class NewFileWindow(QtWidgets.QWidget):
    """
    This window appears when new file is selected from the menu.
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

        # slots and signals
        self.save_location.clicked.connect(self.file_location)

    def file_location(self):
        # Get file location of toml file
        self.config_file, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, caption="Choose save location", filter="feat files (*.feat)"
        )
        self.line_save_location.setText(self.config_file)


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

        # set icon
        self.setWindowIcon(QIcon("FT-logo128.jpg"))

        # Enable Text field edit
        self.read_only.setReadOnly(True)
        self.read_only.setFont(FONT_STYLE_TEXT)

        # slots and signals
        # menu
        self.actionOpen.triggered.connect(self.open_feat_file)
        self.actionNew.triggered.connect(self.show_new_window)
        self.actionSave.triggered.connect(self.save_feat_file)

        # student selection
        self.student_comboBox.currentTextChanged.connect(self.update_student)
        self.NextButton.clicked.connect(self.next_student)
        self.NextButton2.clicked.connect(self.next_student)
        self.PreviousButton.clicked.connect(self.previous_student)
        self.PreviousButton2.clicked.connect(self.previous_student)

        # buttons
        self.copy_button.clicked.connect(self.copy)

    def show_new_window(self, checked):
        self.w = NewFileWindow()
        self.w.show()

    def open_feat_file(self):
        """Menu option New. Open .feat file to construct windows with list of students, feedback form and annotation fields."""
        # open file
        self.config_file, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, caption="Open feat file", filter="feat files (*.feat)"
        )
        if self.config_file == "":
            return
        else:
            # configure feat file
            self.config_toml()

            # initialise feedback windows
            self.init_feat()

    def new_feat_file(self):
        """Menu option New. Create a new .feat file.

        3 Dialogue windows open to ask for save location of .feat file. Get student names and feedback form, in this order.
        """
        # Get file location of toml file
        self.config_file, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, caption="Choose save location", filter="feat files (*.feat)"
        )
        # configure feat file
        self.config_toml()

        # load students names in toml file
        _student_f, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, caption="Open student list", filter="txt files (*.txt)"
        )
        self.config.add_students(_student_f)

        # load feedback file in toml file.
        _feedback_f, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, caption="Open feedback form", filter="toml files (*.toml)"
        )
        self.config.init_feedback(_feedback_f)

        # initialise feedback windows
        self.init_feat()

    def config_toml(self):
        """Configure .feat file. Create Toml structure if file is new, otherwise update date-data."""
        # configure toml file
        self.config = configuration(self.config_file)

    def init_feat(self):
        """Initialize feat application.

        From data in .feat file add check boxes with feedback lines. Add annotation field per feedback subject. Add students to combobox. Displays feedback in text field based on .feat file.
        Slots and signals for check boxes and annotation fields are coupled."""

        # load data from toml file
        self.feat_total = self.config.fileioToml.open_toml()
        # add feedback lines and annotation fields to interface
        self.fblines = self.config.get_feedback_form(self.feat_total)
        self.headline = {"head": {}}
        self.annotation = {"annot": {}}
        self.button = {"check": {}}

        # add salutation
        self.headline_salutation = QtWidgets.QLabel("Hoi Student,")
        self.headline_salutation.setFont(FONT_STYLE_BUTTONS)
        self.vbox.addWidget(self.headline_salutation)

        # add main annotation
        self.annotation["annot"]["main"] = QtWidgets.QTextEdit()
        self.annotation["annot"]["main"].setFont(FONT_STYLE_TEXT)
        self.vbox.addWidget(self.annotation["annot"]["main"])

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

        sign_off_text = self.config.get_sign_off(self.feat_total)
        if sign_off_text:
            self.annotation_sign_off.append(sign_off_text)
        else:
            self.annotation_sign_off.setPlaceholderText("Doe hier de groetjes")
        self.vbox.addWidget(self.annotation_sign_off)

        # add student names to combobox
        for student in self.feat_total["students"]:
            full_name = self.feat_total["students"][student]["full_name"]
            self.student_comboBox.addItem(full_name, student)

        # initialise text box
        self.update_student()
        self.add_sign_off()
        self.text_add()

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
        feedback = self.config.get_feedback(self.feat_total)
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

        # set salutations and main annotation in give feedback field
        self.update_give_feedback_field()

        # update read_only text field
        self.text_add()

    def update_give_feedback_field(self):
        """The name of the student is displayed in the give feedback field. If there is no main annotation a placeholder text is set."""

        current_student = self.current_student()

        # add salutation in give feedback field
        first_line = (
            "Hoi " + self.feat_total["students"][current_student]["first_name"] + ","
        )
        self.headline_salutation.setText(first_line)

        # set text in main annotation
        main = self.config.get_main_annotation(self.feat_total, current_student)

        if main == "":
            self.annotation["annot"]["main"].setPlaceholderText(
                "Laat in een of twee regels weten wat je algehele indruk is."
            )

    def text_add(self):
        """Add text to display feedback text in read-only field.

        Based on the check boxes and annotation field the feedback text is constructed.
        """
        # clear text field
        self.read_only.clear()

        # index of current selected student
        current_student = self.current_student()

        # add salutation text to text field
        first_line = (
            "Hoi " + self.feat_total["students"][current_student]["first_name"] + ","
        )
        self.read_only.append(first_line + "\r")
        self.read_only.append(self.annotation["annot"]["main"].toPlainText() + "\r")

        # add headline to textfield
        for head in self.headline["head"]:
            self.read_only.append(f"[{head}]")

            # add annotations right under headline
            self.read_only.append(self.annotation["annot"][head].toPlainText())

            # add feedback lines to text field
            for line in self.button["check"][head]:
                if self.button["check"][head][line].isChecked():
                    self.read_only.append(
                        self.feat_total["feedbackform"][head][line] + "\r"
                    )

        # add sign-off
        self.read_only.append("\r" + self.annotation_sign_off.toPlainText())

    def check_box(self):
        """Create list of checked boxes, save configuration of check boxes in .feat file. And display feedback lines of checked boxes in read-only field with self.text_add()."""
        current_student = self.current_student()

        feedback = []
        for head in self.headline["head"]:
            for box in self.button["check"][head]:
                if self.button["check"][head][box].isChecked():
                    feedback.append(box)

        # save checked feedback lines in toml
        feat_new = self.config.update_feedback(
            self.feat_total, current_student, "checkbox", feedback
        )

        # update feat data
        self.feat_total = feat_new

        # update read_only text field
        self.text_add()

    def add_annotations(self):
        """Create list of annotations from annotation fields. Save annotation list to .feat file. Display annotations in read-only field with self.text_add()."""
        current_student = self.current_student()

        annotations = []
        for field in self.annotation["annot"]:
            text = self.annotation["annot"][field].toPlainText()
            annotations.append(text)

        # save annotations in toml
        feat_new = self.config.update_feedback(
            self.feat_total, current_student, "annotations", annotations
        )

        # update feat data
        self.feat_total = feat_new

        # update read_only text field
        self.text_add()

    def add_sign_off(self):
        """Save sign-off to .feat file and use self.text_add() to display sign-off in read-only field."""
        # get sign-off text and save to toml
        sign_off = self.annotation_sign_off.toPlainText()
        self.config.save_sign_off(sign_off)
        # add sign-off to read_only text field
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
        self.config.save_feat_file(self.feat_total)


def main():
    app = QtWidgets.QApplication(sys.argv)
    ui = UserInterface()
    ui.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
