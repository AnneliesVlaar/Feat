import sys
import pkg_resources

from PyQt5 import QtWidgets, uic

from feat.models.configuration import configuration






class UserInterface(QtWidgets.QMainWindow):
    def __init__(self):
        # call __init__ of parent class
        super().__init__()

        # load feat gui design
        uic.loadUi(pkg_resources.resource_stream("feat.views", 'gui_feat.ui'), self)

        # load students names in toml file
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(self, filter="CSV files (*.csv *.txt)") 
        self.config = configuration(filename)        

        # load data from toml file
        self.config_dict = self.config.open_toml()

        
        # add student names to combobox
        for student in self.config_dict['students']:
            self.student_comboBox.addItem(student)
        
        # initialise text box
        self.text_add()

        #slots and signals
        self.student_comboBox.currentTextChanged.connect(self.text_add)

    
    def text_add(self):

        # clear text field
        self.read_only.clear()

        # index of current selected student
        current_student = self.student_comboBox.currentText()

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