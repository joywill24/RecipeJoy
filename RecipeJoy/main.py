# main.py
import sys
from PyQt5.QtWidgets import QApplication
from ui_operations import MainWindow
import logging

def main():
    logging.basicConfig(level=logging.INFO)
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()