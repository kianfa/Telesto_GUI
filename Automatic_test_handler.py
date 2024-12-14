import os, shutil
import subprocess
import time
from PyQt5.QtCore import  QThread, pyqtSignal, QPoint, QTimer
import pandas as pd
class Automatic_test_handler():
    def __init__(self):
        pass



    def start_Automatic_test_functions(self):
        self.Open_automatic_test_excel()
        self.Read_commands_from_automatic_test_excel()
        self.Start_implementing_test_commands_thread()

    def Start_implementing_test_commands_thread(self):  # To be completed
        pass

    def Read_commands_from_automatic_test_excel(self):
        # Read the Excel file into a DataFrame
        Commands_df = pd.read_excel(self.excel_of_commands_path,  header=0)
        self.Times_Commands_df = commands_df['Time']
        self.PowerModel_Commands_df = commands_df['Power Mode']
        self.Relay_Commands_df = commands_df['Relay']
        self.Pump_Commands_df = commands_df['Pump']
        self.Outputs_Commands_df = commands_df['Outputs']
        print(commands_df.head())
    def create_a_copy_of_excel(self):
        try:
            original_file_path = os.path.join(self.current_project_dir, "commands.xlsx")
            self.excel_of_commands_path = os.path.join(self.current_project_dir, "commands_copy.xlsx")

            shutil.copy(original_file_path, self.excel_of_commands_path)
            print(f"Copied '{original_file_path}' to '{self.excel_of_commands_path}'")
            return self.excel_of_commands_path
        except Exception as e:
            print(f"Error copying file: {e}")
            return Null

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
            return False


class Start_automatic_test_commands_thread(QThread):
    """Thread for writing registers periodically."""
    update_signal = pyqtSignal(str)

    def __init__(self, pandas_data_frame):
        super().__init__()
        self.pandas_data_frame


    def run(self):
        try:
            while self._running:
                # Reg_Values = collect_reg_vals_from_user_commands(self.switches, self.numeric_up_downs,
                #                                                  self.Assign_number_to_LCD_mode_FUNC)
                # write_multiple_registers(self.ser, 20, Reg_Values)
                # self.update_signal.emit(f"Wrote registers: {Reg_Values}")
                time.sleep(0.5)  # Delay between writes
        except Exception as e:
            print(f"WriteThread error: {e}")

    def stop(self):
        """Stop the thread safely."""
        self._running = False

    def Do_commands_of_excel(self):
        print("?")
Automatic_test_handler_instance = Automatic_test_handler()