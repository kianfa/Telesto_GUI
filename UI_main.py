import time
from datetime import datetime, timedelta
import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QComboBox, QPushButton,
                             QSpinBox, QRadioButton, QLineEdit, QFrame, QMessageBox,
                             QTextEdit, QSizePolicy, QFileDialog, QSpacerItem, QDoubleSpinBox)
from PyQt5.QtCore import Qt, QPropertyAnimation, QRectF, QSize, pyqtProperty, QThread, pyqtSignal, QPoint, QTimer
from PyQt5.QtGui import QPalette, QColor, QPainter, QPen, QBrush
import serial.tools.list_ports
# from Modbus_Protocol import WriteThread, ReadThread
import threading


from openpyxl.worksheet.print_settings import PRINT_AREA_RE
from openpyxl.writer.theme import write_theme
from On_Click_Buttons import *
from Automatic_test_handler import Automatic_test_handler


class Switch(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(50, 25)
        self._checked = False
        self.animation = QPropertyAnimation(self, b"pos")
        self.animation.setDuration(100)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw background
        brush = QBrush(QColor("#333333") if not self._checked else QColor("#FFD700"))
        painter.setBrush(brush)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(0, 0, self.width(), self.height(), 12, 12)

        # Draw knob
        painter.setBrush(QBrush(QColor("white")))
        if self._checked:
            painter.drawEllipse(25, 2, 21, 21)
        else:
            painter.drawEllipse(4, 2, 21, 21)

    def mouseReleaseEvent(self, event):
        self._checked = not self._checked
        self.animate_knob()  # Call the new method for animation
        self.update()

    def animate_knob(self):
        # Set the start and end positions based on the current state
        if self._checked:
            self.animation.setStartValue(self.pos())
            self.animation.setEndValue(self.pos() + QPoint(3, 0))  # Move right by 3 pixels
        else:
            self.animation.setStartValue(self.pos())
            self.animation.setEndValue(self.pos() - QPoint(3, 0))  # Move left by 3 pixels
        self.animation.start()



    def isChecked(self):
        return 1 if self._checked else 0

    def setChecked(self, checked):
        self._checked = checked
        self.animate_knob()  # Call the new method for animation
        self.update()

class UI(QMainWindow):
    update_message_signal = pyqtSignal(str)

    def __init__(self):
        super(UI, self).__init__()  # Properly initialize the parent class
        # self.automatic_test_handler = Automatic_test_handler_instance
        self.Btns_Normal_Color = "#FFD700"
        self.setWindowTitle('Control Panel')
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1E1E1E;
            }
            QLabel {
                color: white;
                font-size: 12px;
            }
            QPushButton {
                background-color: #FFD700;
                border: none;
                padding: 8px;
                border-radius: 4px;
            }
            QLineEdit {
                border: 1px solid #FFD700;
                background-color: transparent;
                color: white;
                padding: 4px;
            }
            QComboBox {
                background-color: white;
                padding: 4px;
            }
            QSpinBox {
                background-color: transparent;
                color: white;
                border: 1px solid #FFD700;
            }
            QDoubleSpinBox {
                background-color: transparent;
                color: white;
                border: 1px solid #FFD700;
            }
            QRadioButton {
                color: white;
            }
        """)
        self.switches = {}
        self.numeric_up_downs = {}
        self.textboxes = {}
        # Connect the signal to the update method
        self.update_message_signal.connect(self.update_message_box)
        self.Datalogger_countdown_flag = False
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)

        # Top section
        top_layout = QHBoxLayout()

        # Left side controls
        left_controls = QVBoxLayout()

        # Baud Rate and Port controls
        conn_layout = QHBoxLayout()

        baud_layout = QVBoxLayout()
        baud_label = QLabel("Baud Rate")
        self.baud_combo = QComboBox()
        self.populate_baudrate_combo()
        default_baudrate = "9600"
        self.baud_combo.setCurrentText(default_baudrate)

        baud_layout.addWidget(baud_label)
        baud_layout.addWidget(self.baud_combo)

        port_layout = QVBoxLayout()
        port_label = QLabel("Port")
        self.port_combo = QComboBox()
        self.populate_ports_combo_box()
        port_layout.addWidget(port_label)
        port_layout.addWidget(self.port_combo)

        conn_layout.addLayout(baud_layout)
        conn_layout.addLayout(port_layout)

        # Buttons
        button_layout = QHBoxLayout()
        self.connect_btn = QPushButton("Connect")
        self.refresh_btn = QPushButton("Refresh Ports")
        button_layout.addWidget(self.connect_btn)
        button_layout.addWidget(self.refresh_btn)

        self.refresh_btn.clicked.connect(self.on_refresh_click)
        self.connect_btn.clicked.connect(self.on_connect_click)

        left_controls.addLayout(conn_layout)
        left_controls.addLayout(button_layout)

        line_layout = QHBoxLayout()
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)  # Make the line expand horizontally
        line_layout.addWidget(line)
        left_controls.addLayout(line_layout)



        interval_settings_layout = QHBoxLayout()
        Read_intervals = QLabel("Read Intervals:")
        self.Read_Intervals_Spin = QDoubleSpinBox()
        self.Read_Intervals_Spin.setValue(10)
        self.Read_Intervals_Spin.setRange(0.1, 100)
        interval_settings_layout.addWidget(Read_intervals)
        interval_settings_layout.addWidget(self.Read_Intervals_Spin)


        Save_Log_Intervals = QLabel("Save Log Intervals:")
        self.Save_Log_Intervals_Spin = QDoubleSpinBox()
        self.Save_Log_Intervals_Spin.setValue(50)
        self.Save_Log_Intervals_Spin.setRange(1,1000)
        interval_settings_layout.addWidget(Save_Log_Intervals)
        interval_settings_layout.addWidget(self.Save_Log_Intervals_Spin)

        left_controls.addLayout(interval_settings_layout)


        line_layout = QHBoxLayout()
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)  # Make the line expand horizontally
        line_layout.addWidget(line)
        left_controls.addLayout(line_layout)

        # Time controls
        time_layout = QHBoxLayout()
        time_label = QLabel("Time:")
        self.day_spin = QSpinBox()
        self.hour_spin = QSpinBox()
        self.min_spin = QSpinBox()
        self.sec_spin = QSpinBox()

        day_label = QLabel("Day")
        hour_label = QLabel("Hour")
        min_label = QLabel("Min")
        sec_label = QLabel("Sec")

        time_layout.addWidget(time_label)
        time_layout.addWidget(self.day_spin)
        time_layout.addWidget(day_label)
        time_layout.addWidget(self.hour_spin)
        time_layout.addWidget(hour_label)
        time_layout.addWidget(self.min_spin)
        time_layout.addWidget(min_label)
        time_layout.addWidget(self.sec_spin)
        time_layout.addWidget(sec_label)

        left_controls.addLayout(time_layout)

        # Create a small panel layout
        panel_layout = QVBoxLayout()  # Use QVBoxLayout to stack messages vertically

        # Create a QTextEdit for displaying messages
        self.Data_logger_message_box = QTextEdit()
        self.Data_logger_message_box.setReadOnly(True)  # Make it read-only
        self.Data_logger_message_box.setStyleSheet("background-color: #2E2E2E; color: white;")
        self.Data_logger_message_box.setFixedHeight(30)  # Set a fixed height
        self.Data_logger_message_box.setMaximumHeight(30)  # Optional: limit the maximum height
        self.Data_logger_message_box.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # Hide the vertical scrollbar
        self.Data_logger_message_box.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # Hide the horizontal scrollbar

        self.placeholder = QWidget()
        self.placeholder.setFixedHeight(30)  # Match the height of the message box
        self.placeholder.setMaximumHeight(30)
        self.Data_logger_message_box.hide()
        panel_layout.addWidget(self.placeholder)  # Add placeholder first
        panel_layout.addWidget(self.Data_logger_message_box)

        # Add the panel layout above the Start Log button


        # Start Log button
        self.start_log_btn = QPushButton("Start Log")

        panel_layout.addWidget(self.start_log_btn)
        panel_layout.addStretch()
        left_controls.addLayout(panel_layout)

        self.start_log_btn.clicked.connect(self.on_start_log_click)


        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)  # Make the line expand horizontally

        Lower_panel_layout = QVBoxLayout()



        left_controls.addLayout(Lower_panel_layout)
        self.Start_Automatic_Test_Btn = QPushButton("Start Automatic Test")
        self.Start_Automatic_Test_Btn.clicked.connect(self.on_Start_Automatic_Test_click)
        Lower_panel_layout.addWidget(line)
        Lower_panel_layout.addWidget(self.Start_Automatic_Test_Btn)
        Lower_panel_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Right side controls
        right_controls = QVBoxLayout()

        # Mode controls with switches
        mode_layouts = []
        for label_text in ["Power Mode", "Relay", "Pump", "Output Valve"]:
            layout = QHBoxLayout()
            label = QLabel(label_text)
            switch = Switch()
            layout.addWidget(label)
            layout.addWidget(switch)
            layout.addStretch()
            mode_layouts.append(layout)
            self.switches[label_text] = switch  # Store the switch reference with its name
            right_controls.addLayout(layout)


        # LCD Mode radio buttons
        lcd_mode_label = QLabel("LCD Mode")
        self.off_radio = QRadioButton("Off")
        self.off_radio.setChecked(True)
        self.bright_radio = QRadioButton("Dim")
        self.dim_radio = QRadioButton("Bright")

        right_controls.addWidget(lcd_mode_label)
        right_controls.addWidget(self.off_radio)
        right_controls.addWidget(self.bright_radio)
        right_controls.addWidget(self.dim_radio)

        # Speed Reference
        speed_label_text = "Speed Reference"
        speed_label = QLabel(speed_label_text)
        speed_spin = QSpinBox()
        speed_spin.setRange(0, 20)  # Set range for the spin box
        self.numeric_up_downs[speed_label_text] = speed_spin;
        right_controls.addWidget(speed_label)
        right_controls.addWidget(speed_spin)

        top_layout.addLayout(left_controls)
        top_layout.addLayout(right_controls)

        # Bottom section
        Seperator_Line_Layout = QHBoxLayout()

        # Create the horizontal line
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)  # Make the line expand horizontally

        Seperator_Line_Layout.addWidget(line)  # Add the line to the layout

        bottom_layout = QHBoxLayout()
        # Temperature and RPM
        temp_layout = QVBoxLayout()
        temp_label_text = "Temperature";
        temp_label = QLabel(temp_label_text)
        temp_textbox = QLineEdit()
        temp_textbox.setPlaceholderText("0")
        self.textboxes[temp_label_text] = temp_textbox;
        temp_textbox.setReadOnly(True)

        rpm_label_text = "RPM"
        rpm_label = QLabel(rpm_label_text)
        rpm_textbox = QLineEdit()
        rpm_textbox.setPlaceholderText("0")
        self.textboxes[rpm_label_text] = rpm_textbox;
        rpm_textbox.setReadOnly(True)

        temp_layout.addWidget(temp_label)
        temp_layout.addWidget(temp_textbox)
        temp_layout.addWidget(rpm_label)
        temp_layout.addWidget(rpm_textbox)

        # Drive Current and Thermostat Current
        current_layout = QVBoxLayout()
        drive_label_text = "Drive Current"
        drive_label = QLabel(drive_label_text)
        drive_textbox = QLineEdit()
        drive_textbox.setPlaceholderText("0")
        self.textboxes[drive_label_text] = drive_textbox;
        drive_textbox.setReadOnly(True)

        Drive_Voltage_label_text = "Drive Voltage"
        Drive_Voltage_label = QLabel(Drive_Voltage_label_text)
        Drive_Voltage_textbox = QLineEdit()
        Drive_Voltage_textbox.setPlaceholderText("0")
        self.textboxes[Drive_Voltage_label_text] = Drive_Voltage_textbox;
        Drive_Voltage_textbox.setReadOnly(True)

        current_layout.addWidget(drive_label)
        current_layout.addWidget(drive_textbox)
        current_layout.addWidget(Drive_Voltage_label)
        current_layout.addWidget(Drive_Voltage_textbox)

        bottom_layout.addLayout(temp_layout)
        bottom_layout.addLayout(current_layout)

        # Add layouts to main layout
        main_layout.addLayout(top_layout)
        main_layout.addLayout(Seperator_Line_Layout)
        main_layout.addLayout(bottom_layout)

        # Set window size
        self.setMinimumSize(800, 500)

    def Change_Btn_Color(self, Btn, Btn_Color):
        Btn.setStyleSheet(f"background-color: {Btn_Color};")  # Using an f-string
    def Change_Btn_Text(self, Btn, Btn_Text):
        Btn.setText(Btn_Text)
    def SetTextBoxText(self, TextBox, Text):
        TextBox.setText(Text)

    def Assign_number_to_LCD_mode(self):
        # Check which radio button is selected
        if self.off_radio.isChecked():
            return 0;
        elif self.bright_radio.isChecked():
            return 1;
        elif self.dim_radio.isChecked():
            return 2;

    def Set_LCD_Radio_Buttons(self, command):
        if command == 0 :
            self.off_radio.setChecked(True);
        elif command == 1:
            self.bright_radio.setChecked(True);
        elif command == 2 :
            self.dim_radio.setChecked(True)
    def Set_Speed_reference_textbox(self, command):
        self.numeric_up_downs["Speed Reference"].setValue(command)

    def get_available_ports(self):
        """Return a list of available serial ports."""
        ports = serial.tools.list_ports.comports()
        available_ports = [port.device for port in ports]
        return available_ports

    def populate_ports_combo_box(self):
        """Populate the QComboBox with available serial ports."""
        self.port_combo.clear()
        available_ports = self.get_available_ports()
        self.port_combo.addItems(available_ports)  # Add ports to the combo box

    def populate_baudrate_combo(self):
        """Populate the given QComboBox with popular baud rates."""
        baud_rates = [
            300,
            600,
            1200,
            2400,
            4800,
            9600,
            14400,
            19200,
            38400,
            57600,
            115200,
            230400,
            250000,
            500000,
            1000000
        ]
        self.baud_combo.addItems([str(rate) for rate in baud_rates])  # Add baud rates as strings

    def on_refresh_click(self):
        self.populate_ports_combo_box()
        print("Refresh ports is clicked")
    def on_connect_click(self):
        On_Connect_Click(self)

    def on_start_log_click(self):
        start_log(self)

    def on_Start_Automatic_Test_click(self):
        if(self.Start_Automatic_Test_Btn.text() == "Start Automatic Test"):
            Start_Automatic_Test()
        else:
            Stop_Automatic_Test()



    def open_file_dialog(self):
        # Open a file dialog and get the selected path
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "Select Save Path", "", "All Files (*)", options=options)

        # Check if the user selected a file or canceled the dialog
        if file_path:
            print("Selected path:", file_path)  # You can store this path for later use
            path = file_path  # Store the selected path
            # Optionally, update the UI or provide feedback to the user
            # self.path_label.setText(f"Selected Path: {file_path}")
            return path
        else:
            print("No file selected.")  # Handle the cancel action if needed
            return

    def save_log_data_as_excel__AND__set_UI(self, path = "D:\\test_data.xlsx"):
        Received_data_handler_instance.save_to_excel(path)
        Received_data_handler_instance.Clear_buffer_of_data()
        self.Datalogger_countdown_flag = False  # This will stop the thread of datalogging countdown(if there would be any)
        self.read_thread.Flag_Save_data_in_buffer = False
        self.Set_Start_log_button_to_default()

    def Set_Start_log_button_to_default(self):
        self.start_log_btn.setText("Start Log")
        self.start_log_btn.setStyleSheet("background-color: #FFD700; color: black;")
        self.Data_logger_message_box.hide()

    def calc_finish_log_time(self):
        Days = self.day_spin.value()
        Hours = self.hour_spin.value()
        Mins = self.min_spin.value()
        Secs = self.sec_spin.value()
        # Get the current date and time
        current_time = datetime.now()

        # Create a timedelta object
        time_to_add = timedelta(days=Days, hours=Hours, minutes=Mins, seconds=Secs)

        # Calculate the finish time
        finish_time = current_time + time_to_add

        # Return or print the finish time
        print(f"Finish time for log: {finish_time}")
        return finish_time
    def show_message(self, text, title=None):
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




    def show_data_logger_timer(self):
        """Display the data logger timer."""
        # Start the countdown in a new thread
        # self.placeholder.hide()

        self.finish_time = self.calc_finish_log_time()
        delta_time = self.calculate_delta_time()
        if delta_time.total_seconds() <= 0 :
            self.show_message("Please select an appropriate time for Log.", title="Log can not Start")
            return 404;

        self.Data_logger_message_box.show()
        self.Datalogger_countdown_flag = True
        Save_As_Excel_Intervals = self.Save_Log_Intervals_Spin.value()
        self.countdown_thread = threading.Thread(target=self.run_countdown, args=(self.finish_time,Save_As_Excel_Intervals))
        self.countdown_thread.start()



    def calculate_delta_time(self):
        current_time = datetime.now()
        delta_time = self.finish_time - current_time
        return delta_time
    def run_countdown(self, finish_time, saiving_as_excel_intervals ):
        while self.Datalogger_countdown_flag  :

            delta_time = self.calculate_delta_time()
            # If time is up, break the loop
            if (int(delta_time.total_seconds()) % saiving_as_excel_intervals == 0):
                Received_data_handler_instance.save_to_excel(path = self.Save_excel_path)
                print(delta_time.total_seconds())
                print("Autosave Is Done")

            elif delta_time.total_seconds() <= 0:
                # Save excel
                self.save_log_data_as_excel__AND__set_UI(path = self.Save_excel_path)
                break



            days = delta_time.days
            hours, remainder = divmod(delta_time.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)

            time_format = f"{days} days/ {hours:02}:{minutes:02}:{seconds:02} remained"
            self.update_message_signal.emit(time_format)
            time.sleep(1)  # Wait for 1 second before updating again


    def update_message_box(self, message):
        self.Data_logger_message_box.setPlainText(message)

    def update_textboxes_related_to_received_data(self, received_data):
        try:
            for key in self.textboxes:
                try:
                    print(str(received_data[key]))

                    self.textboxes[key].setText(str(received_data[key]))
                except Exception as e:
                    print(f"update textboxes _inner: {e}")
        except Exception as e:
                print(f"update textboxes error: {e}")
