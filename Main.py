import sys
import threading
from UI_main import UI
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout)
from Automatic_test_handler import Automatic_test_handler




if __name__ == '__main__':
    print("__main__")

    app = QApplication(sys.argv);
    Main_window = UI()
    print(Main_window)
    Automatic_test_handler_instance = Automatic_test_handler.get_instance()
    Automatic_test_handler_instance.SetGui(Main_window);


    Main_window.show()
    sys.exit(app.exec_())


