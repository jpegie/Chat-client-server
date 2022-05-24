from PyQt5 import QtWidgets
from DataClasses.ChatClientAppClass import ChatClientApp
import sys


def main():

    app = QtWidgets.QApplication(sys.argv)
    window = ChatClientApp()

    window.show()
    window.setup_bindings()

    app.exec_()


if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
