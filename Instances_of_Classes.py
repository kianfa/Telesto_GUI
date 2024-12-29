from Automatic_test_handler import Automatic_test_handler
from Main import UI

def Reurn_MainWindow_instance():
    return UI.get_instance()

def Reurn_Automatic_test_handler_instance():
    return Automatic_test_handler.get_instance()