import sys
import pkg_resources

from PyQt5 import QtWidgets, uic

from feat.models.configuration import configuration

import pandas as pd




class UserInterface(QtWidgets.QMainWindow):
    def __init__(self):
        # call __init__ of parent class
        super().__init__()

        # load feat gui design
        uic.loadUi(pkg_resources.resource_stream("feat.views", 'gui_feat.ui'), self)

        self.config = configuration()

        # # load student names to combobox
        # TODO: Een open deze file met studenten dingetje
        # df_students = pd.read_csv("students_A-test.csv", sep=",", header=0, encoding='latin-1')

        # load data from toml file
        self.config_dict = self.config.open_toml()
        
        # add student names to combobox
        for i,student in enumerate(self.config_dict['students']):

            first = self.config_dict["students"][student]["FirstName"]
            middle = self.config_dict["students"][student]["MiddleName"]
            last = self.config_dict["students"][student]["LastName"]
            
            # TODO: dit misschien via fileio? veilig wegschrijven van dingen?
            # add index to toml data 
            self.config_dict["students"][student]["idx"] = i
            
            self.student_comboBox.addItem(first+" "+middle+" "+last)



        #slots and signals
        self.student_comboBox.currentTextChanged.connect(self.text_add)

    
    def text_add(self):
        
        # index of current selected student
        idx = self.student_comboBox.currentIndex()

        # Find out which student is selected
        current_student = None
        for student in self.config_dict['students']:
            if idx == self.config_dict["students"][student]["idx"]:
                current_student = student

        # clear text field
        self.read_only.clear()

        # add text to text field
        first_line = 'Hoi ' + self.config_dict["students"][current_student]["FirstName"] + ','
        self.read_only.append(first_line)




def main():
    app = QtWidgets.QApplication(sys.argv)
    ui = UserInterface()
    ui.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()