from PyQt5.QtWidgets import QMessageBox
class MessageBox:
    def __init__(self):
        pass
    def OK_Cancell_message(self, text, title=None):
        """Display a message box."""
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)  # Set icon
        msg_box.setText(text)  # Set message text
        msg_box.setWindowTitle(title)  # Set window title
        msg_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)  # Add buttons

        # Show the message box and wait for user response
        response = msg_box.exec_()

        # Handle user response
        if response == QMessageBox.Ok:
            print("User clicked OK.")
        else:
            print("User clicked Cancel.")




MessageBoxes_instance = MessageBox()

