import os, shutil
import subprocess
import time
from PyQt5.QtCore import  QThread, pyqtSignal, QPoint, QTimer
from PyQt5.QtWidgets import QPushButton
import pandas as pd
from MessageBoxes_UI import MessageBoxes_instance
from dataclasses import dataclass
from Error_Logger import save_error_to_file
@dataclass
class CommandsStruct:
    Times: pd.Series
    PowerMode: pd.Series
    Relay: pd.Series
    Pump: pd.Series
    Output_valve: pd.Series
    LCDMode: pd.Series
    SpeedReference: pd.Series

class Automatic_test_handler():
    __shared_instance = None

    @staticmethod
    def get_instance():
        """Static Access Method"""
        if Automatic_test_handler.__shared_instance == None:
            Automatic_test_handler()
        return Automatic_test_handler.__shared_instance

    def __init__(self):
        self.Gui = None
        if Automatic_test_handler.__shared_instance is not None:
            raise Exception("This class is a singleton class!")
        else:
            Automatic_test_handler.__shared_instance = self
        self.MessageBoxes = MessageBoxes_instance

    def SetGui(self, gui):
        self.Gui = gui

    def Start_Automatic_Test_Functions(self):
        self.Open_automatic_test_excel()
        time.sleep(0.5) # Code will try reading the excel file before its completely closed if you delete this.

        has_null = self.Check_if_df_has_null()
        if has_null:
            self.MessageBoxes.OK_Cancell_message("One or more items are null", title="Refill the excel")
            return


        self.Read_commands_from_automatic_test_excel()
        self.Start_implementing_test_commands_thread()

    def Start_implementing_test_commands_thread(self):
        self.Auto_Test_thread = Automatic_test_thread(self.commands, self.Gui)

        self.Auto_Test_thread.start()
    def Check_if_df_has_null(self):
        self.Commands_df = pd.read_excel(self.excel_of_commands_path, header=0)
        has_null = self.Commands_df .isnull().values.any()
        if self.Commands_df["Time"].isnull().values.all():
            has_null = True;
        return has_null
    def Read_commands_from_automatic_test_excel(self):
        self.commands = CommandsStruct(
            Times=self.Commands_df['Time'],
            PowerMode=self.Commands_df['Power Mode'].astype(bool),
            Relay=self.Commands_df['Relay'].astype(bool),
            Pump=self.Commands_df['Pump'].astype(bool),
            Output_valve=self.Commands_df['Output Valve'].astype(bool),
            LCDMode=self.Commands_df['Lcd Mode (0:off,1:Dim,2:Bright)'],
            SpeedReference = self.Commands_df['Speed Reference']
        )
        print( self.commands.Times)
        print(self.commands.PowerMode)
        print(self.commands.Relay)
        print(self.commands.Pump)
        print(self.commands.Output_valve)
        print(self.commands.LCDMode)
        print(self.commands.SpeedReference);

        print(self.commands)
    def create_a_copy_of_excel(self):
        try:
            original_file_path = os.path.join(self.current_project_dir, "commands.xlsx")
            self.excel_of_commands_path = os.path.join(self.current_project_dir, "commands_copy.xlsx")

            shutil.copy(original_file_path, self.excel_of_commands_path)
            print(f"Copied '{original_file_path}' to '{self.excel_of_commands_path}'")
            return self.excel_of_commands_path
        except Exception as e:
            print(f"Error copying file: {e}")
            save_error_to_file("Error copying file:" + str(e))
            return e

    def Open_automatic_test_excel(self):
        self.current_project_dir = os.path.dirname(os.path.abspath(__file__))

        copy_file_path = self.create_a_copy_of_excel()
        # Open the Excel file
        if os.path.exists(copy_file_path):
            # Open the Excel file using the default program (Excel)
            subprocess.Popen(['start', 'excel', copy_file_path], shell=True)

            # Wait for the user to close the Excel file
            while True:
                time.sleep(0.5)  # Check every second
                if not self.is_excel_running():
                    print("Excel closed. Continuing with the process...")
                    break
        else:
            print("The specified file does not exist.")


    def is_excel_running(self):
        # Check if the Excel process is running
        try:
            # Check for the filename in the list of running processes
            output = subprocess.check_output('tasklist', shell=True).decode()
            return 'EXCEL.EXE' in output
        except Exception as e:
            print(f"Error checking Excel process: {e}")
            save_error_to_file("Error checking Excel process:" + str(e))
            return False

class Automatic_test_thread(QThread):
    """Thread for writing registers periodically."""
    update_signal = pyqtSignal(str)
    update_power_mode_signal = pyqtSignal(bool)
    update_relay_signal = pyqtSignal(bool)
    update_pump_signal = pyqtSignal(bool)
    update_output_valve_signal = pyqtSignal(bool)
    update_lcd_mode_signal = pyqtSignal(int)  # Assuming LCDMode is an int
    update_speed_reference_signal = pyqtSignal(int)  # Assuming SpeedReference is a float

    update_Btn_Color_signal = pyqtSignal(QPushButton, str)  # Signal for changing button color (button, color)
    update_Btn_Text_signal = pyqtSignal(QPushButton, str)   # Signal for changing button text (button, text)

    def __init__(self,commands, Gui):
        super().__init__()
        self.Gui = Gui
        self.commands = commands
        self._running = True  # Control flag for the thread

        # Connect signals to GUI methods
        self.update_power_mode_signal.connect(self.Gui.switches["Power Mode"].setChecked)
        self.update_relay_signal.connect(self.Gui.switches["Relay"].setChecked)
        self.update_pump_signal.connect(self.Gui.switches["Pump"].setChecked)
        self.update_output_valve_signal.connect(self.Gui.switches["Output Valve"].setChecked)
        self.update_lcd_mode_signal.connect(self.Gui.Set_LCD_Radio_Buttons)
        self.update_speed_reference_signal.connect(self.Gui.Set_Speed_reference_textbox)
        self.update_Btn_Color_signal.connect(self.Gui.Change_Btn_Color)
        self.update_Btn_Text_signal.connect(self.Gui.Change_Btn_Text)

    def run(self):
        try:
            self.update_Btn_Color_signal.emit(self.Gui.Start_Automatic_Test_Btn, "Red")
            self.update_Btn_Text_signal.emit(self.Gui.Start_Automatic_Test_Btn, "Stop Automatic Test")
            while self._running:
                for r in range(len(self.commands.Times)):
                    if r > 0:
                        time.sleep(self.commands.Times[r] - self.commands.Times[r-1] )  # Delay between commands
                    elif(r == 0):
                        time.sleep(self.commands.Times[0])  # Delay between commands

                    if self._running:
                        # Emit signals instead of direct access
                        self.update_power_mode_signal.emit(self.commands.PowerMode[r])
                        self.update_relay_signal.emit(self.commands.Relay[r])
                        self.update_pump_signal.emit(self.commands.Pump[r])
                        self.update_output_valve_signal.emit(self.commands.Output_valve[r])
                        self.update_lcd_mode_signal.emit(self.commands.LCDMode[r])
                        self.update_speed_reference_signal.emit(self.commands.SpeedReference[r])

                time.sleep(0.5)
                self.Stop()

        except Exception as e:
            self._running = False
            print(f"Automatic Test Thread error: {e}")
            save_error_to_file("Automatic Test Thread error:" + str(e))

    def Stop(self):
        """Stop the thread safely."""
        self._running = False
        self.update_Btn_Color_signal.emit(self.Gui.Start_Automatic_Test_Btn, self.Gui.Btns_Normal_Color)
        self.update_Btn_Text_signal.emit(self.Gui.Start_Automatic_Test_Btn, "Start Automatic Test")


