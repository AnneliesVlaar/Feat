import re
import sys
import pkg_resources

from PyQt5 import QtWidgets, uic

from feat.models.configuration import configuration


import toml





class UserInterface(QtWidgets.QMainWindow):
    def __init__(self):
        # call __init__ of parent class
        super().__init__()

        # configure toml file
        self.config = configuration()

        # load feat gui design
        uic.loadUi(pkg_resources.resource_stream("feat.views", 'gui_feat.ui'), self)

        # add feedbacklines to interface
        self.fblines = self.config.open_toml('feedbackpunten.toml')
        self.button = {'head': {}, 'check': {}}
        for head in self.fblines:
            self.button['head'][head] = QtWidgets.QLabel(head)
            self.vbox.addWidget(self.button['head'][head])
            for line in self.fblines[head]:
                self.button['check'][line] = QtWidgets.QCheckBox(self.fblines[head][line])
                self.vbox.addWidget(self.button['check'][line])

        # load students names in toml file
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(self, filter="CSV files (*.csv *.txt)") 
        self.config.add_students(filename)        

        # load data from toml file
        self.config_dict = self.config.open_toml()

        
        # add student names to combobox
        for student in self.config_dict['students']:
            self.student_comboBox.addItem(student)
        
        # initialise text box
        self.text_add()

        #slots and signals
        self.student_comboBox.currentTextChanged.connect(self.change_student)
        for box in self.button['check']:
            self.button['check'][box].stateChanged.connect(self.check_box)

    def current_student(self):
        # index of current selected student
        current_student = self.student_comboBox.currentText()
        return current_student

    def change_student(self):
        feedback = self.config.get_feedback()
        current_student = self.current_student()
        
        # uncheck all checkboxes, check when checkbox name is in toml file
        for box in self.button['check']:
            self.button['check'][box].setChecked(False)
            if box in feedback[current_student]:
                self.button['check'][box].setChecked(True)
        
        # update read_only text field
        self.text_add()

    
    def text_add(self):

        # clear text field
        self.read_only.clear()

        # index of current selected student
        current_student = self.current_student()

        # add salutation text to text field
        first_line = 'Hoi ' + self.config_dict["students"][current_student]["FirstName"] + ','
        self.read_only.append(first_line + "\r")

        # add feedback lines to text field
        for line in self.button['check']:
            if self.button['check'][line].isChecked():
                self.read_only.append(self.button['check'][line].text() + "\r")

    def check_box(self):
        current_student = self.current_student()

        feedback = []
        for box in self.button['check']:
            if self.button['check'][box].isChecked():
                feedback.append(box)

        # save checked feedback lines in toml
        self.config.update_feedback(current_student, feedback)

        # update read_only text field
        self.text_add()



def main():
    app = QtWidgets.QApplication(sys.argv)
    ui = UserInterface()
    ui.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()