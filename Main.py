from UI_main import ControlPanel, QApplication, sys
from Modbus_Protocol import *
import threading


if __name__ == '__main__':

    app = QApplication(sys.argv)
    Main_window = ControlPanel()
    Main_window.show()
    sys.exit(app.exec_())