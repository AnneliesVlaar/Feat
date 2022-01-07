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

        # load student names to combobox
        df_students = pd.read_csv("students_A-test.csv", sep=",", header=0, encoding='latin-1')
        student_names = df_students['FirstName']+" "+df_students['MiddleName']+" "+df_students['LastName']

        self.student_comboBox.addItems(student_names)

        #slots and signals
        self.student_comboBox.currentTextChanged.connect(self.text_add)

        self.config = configuration()


        
    def text_add(self):
        test = self.student_comboBox.currentText()
        self.read_only.append('Hoi ' + test + ',')

    




def main():
    app = QtWidgets.QApplication(sys.argv)
    ui = UserInterface()
    ui.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()