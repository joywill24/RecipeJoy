# main.py
import sys
import logging

from PyQt5.QtWidgets import QApplication
from ui_operations import MainWindow


def main():
    logging.basicConfig(level=logging.DEBUG)
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
