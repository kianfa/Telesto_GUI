import serial.tools.list_ports
import time
from Automatic_test_handler import Automatic_test_handler
from Modbus_Protocol import WriteThread, ReadThread,Send_Read_Reg_Command_Thread
from Received_data_handler import Received_data_handler_instance

def Start_Automatic_Test():
    Automatic_test_handler_instance = Automatic_test_handler.get_instance()
    Automatic_test_handler_instance.Start_Automatic_Test_Functions()

def Stop_Automatic_Test():
    Automatic_test_handler_instance = Automatic_test_handler.get_instance()
    Automatic_test_handler_instance.Auto_Test_thread.Stop()


def On_Connect_Click(Gui):
    if(Gui.connect_btn.text() == "Disconnect"):
        Gui.connect_btn.setText("Connect")
        Gui.connect_btn.setStyleSheet("background-color: #FFD700; ")
        Gui.write_thread.stop()
        Gui.read_thread.stop()
        time.sleep(0.1)  # Small delay to ensure buffers are cleared
        Gui.ser.close()
        del Gui.ser  # Remove the serial object completely
    else: # (self.connect_bt.text() == "Connect")
        try:
            # Set up serial connection
            Gui.ser = serial.Serial(Gui.port_combo.currentText(),
                                Gui.baud_combo.currentText(),
                                timeout=1,
                                bytesize=serial.EIGHTBITS,
                                stopbits=serial.STOPBITS_ONE,
                                parity=serial.PARITY_NONE)
            Gui.ser.read_buffer_size = 4096
        except Exception as e :
            print("Failed")
            print(e)
            Gui.show_message("Connection failed. Check the Port number.", title="Connection Failed")
            return
        # write_thread includes Writing myltiple Regs command and Read_req command
        Start_read_write_threads(Gui)

        Gui.connect_btn.setText("Disconnect")
        Gui.connect_btn.setStyleSheet("background-color: Red; color: white;")
        time.sleep(1)  #If you delete this, UI will be closed.
def Stop_read_write_threads(Gui):
    Gui.read_thread.stop()
    Gui.write_thread.stop()
    Gui.Send_Read_Reg_Command.stop()

def Start_read_write_threads(Gui):
    Gui.write_thread = WriteThread(Gui.ser, Gui.switches, Gui.numeric_up_downs,
                                   Assign_number_to_LCD_mode_FUNC=Gui.Assign_number_to_LCD_mode)

    read_request_interval = Gui.Read_Intervals_Spin.value()
    Gui.Send_Read_Reg_Command = Send_Read_Reg_Command_Thread(Gui.ser, read_request_interval)

    Gui.read_thread = ReadThread(Gui.ser, Gui.switches, Gui.numeric_up_downs, Gui.textboxes,
                                 Assign_number_to_LCD_mode_FUNC=Gui.Assign_number_to_LCD_mode,
                                 update_textboxes_related_to_received_data_FUNC=Gui.update_textboxes_related_to_received_data)

    Gui.write_thread.start()
    time.sleep(0.1)
    Gui.read_thread.update_signal.connect(Gui.update_textboxes_related_to_received_data)
    Gui.read_thread.start()
    time.sleep(0.1)
    Gui.Send_Read_Reg_Command.start()
    time.sleep(0.1)

def start_log(Gui):

    current_state = Gui.start_log_btn.text()
    if(current_state == "Start Log"):
        print("Log started.")

        Stop_read_write_threads(Gui)

        Gui.Save_excel_path = Gui.open_file_dialog()

        Start_read_write_threads(Gui)

        if (Gui.Save_excel_path):
            situation = Gui.show_data_logger_timer()
            if situation == 404:
                return

            Finis_log_time = Gui.calc_finish_log_time()
            Gui.start_log_btn.setText("Stop Log")
            Gui.start_log_btn.setStyleSheet("background-color: red; color: white;")
            Received_data_handler_instance.Clear_buffer_of_data()
            Gui.read_thread.Flag_Save_data_in_buffer = True
        else:
            return
    else:
        Gui.save_log_data_as_excel__AND__set_UI(path = Gui.Save_excel_path)

