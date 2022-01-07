import sys
# import pkg_resources

from PyQt5 import QtWidgets, uic


class UserInterface(QtWidgets.QMainWindow):
    def __init__(self):
        # call __init__ of parent class
        super().__init__()

        uic.loadUi(open("src/feat/views/gui_feat.ui"), self)

def main():
    app = QtWidgets.QApplication(sys.argv)
    ui = UserInterface()
    ui.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()