import serial
import time
from PyQt5.QtCore import QThread, pyqtSignal
SLAVE_ADDRESS = 0x02;
from Received_data_handler import Received_data_handler_instance
from threading import Lock
from Error_Logger import save_error_to_file

def calc_crc(data):
    """Calculate CRC-16 for Modbus."""
    crc = 0xFFFF
    for pos in data:
        crc ^= pos
        for _ in range(8):
            if (crc & 0x0001):
                crc >>= 1
                crc ^= 0xA001
            else:
                crc >>= 1
    return crc


def write_single_register_command(ser, address, value):
    buf = [SLAVE_ADDRESS, 0x06, (address >> 8) & 0xFF, address & 0xFF,
           (value >> 8) & 0xFF, value & 0xFF]

    crc = calc_crc(buf)
    buf.append(crc & 0xFF)  # CRC Low byte
    buf.append((crc >> 8) & 0xFF)  # CRC High byte

    ser.write(bytes(buf))


def write_multiple_registers_command(ser, start_address, values):
    count = len(values)
    buf = [SLAVE_ADDRESS, 0x10, (start_address >> 8) & 0xFF, start_address & 0xFF,
           (count >> 8) & 0xFF, count & 0xFF, count * 2]

    for value in values:
        buf.append((value >> 8) & 0xFF)
        buf.append(value & 0xFF)

    crc = calc_crc(buf)
    buf.append(crc & 0xFF)  # CRC Low byte
    buf.append((crc >> 8) & 0xFF)  # CRC High byte
    # print("************************************************** :")
    # print("Write_Reg_Vals :")
    # print(values)
    # print("************************************************** :")
    ser.write(bytes(buf))

def read_registers_command(ser, address, count):
    """Read holding registers."""
    buf = [SLAVE_ADDRESS, 0x04, (address >> 8) & 0xFF, address & 0xFF,
           (count >> 8) & 0xFF, count & 0xFF]

    crc = calc_crc(buf)
    buf.append(crc & 0xFF)  # CRC Low byte
    buf.append((crc >> 8) & 0xFF)  # CRC High byte

    ser.write(bytes(buf))

    # # Read response
    # response = ser.read(5 + count * 2)  # 5 bytes header + 2 bytes per register


class WriteThread(QThread):
    update_signal = pyqtSignal(str)

    def __init__(self, ser, switches, numeric_up_downs, Assign_number_to_LCD_mode_FUNC):
        super().__init__()
        self.ser = ser
        self.switches = switches
        self.numeric_up_downs = numeric_up_downs
        self._running = True
        self.Assign_number_to_LCD_mode_FUNC = Assign_number_to_LCD_mode_FUNC
        self.serial_lock = Lock()  # Add lock for serial port access

    def run(self):
        try:
            while self._running:
                if not self.ser.is_open:
                    raise Exception("Serial port is closed")

                Reg_Values = self.collect_reg_vals_from_user_commands(
                    self.switches.copy(),  # Create copies to avoid concurrent modification
                    self.numeric_up_downs.copy(),
                    self.Assign_number_to_LCD_mode_FUNC
                )
                print("****** write reg values ******")
                print(Reg_Values)
                print("************")

                with self.serial_lock:  # Acquire lock before serial operations
                    write_multiple_registers_command(self.ser, 20, Reg_Values)
                    time.sleep(0.45)

        except Exception as e:
            print(f"WriteThread error: {e}")
            self.update_signal.emit(f"WriteThread error: {str(e)}")
            save_error_to_file("WriteThread error:" + str(e))
            self._running = False
            if str(e)!= "Serial port is closed":
                self.restart_thread()

    def stop(self):
        self._running = False
    def restart_thread(self):
        self.stop()  # Stop the current thread
        self._running = True
        print("Restarting WriteThread...")
        self.run();



    def collect_reg_vals_from_user_commands(self, switches, numeric_up_downs, Assign_number_to_LCD_mode_FUNC):
        values = []
        values.append(switches["Power Mode"].isChecked());
        values.append(switches["Relay"].isChecked());
        values.append(switches["Pump"].isChecked());
        values.append(switches["Output Valve"].isChecked());
        values.append(Assign_number_to_LCD_mode_FUNC());
        values.append(numeric_up_downs["Speed Reference"].value());
        return values;

class Send_Read_Reg_Command_Thread(QThread):
    update_signal = pyqtSignal(str)

    def __init__(self, ser, interval_time):
        super().__init__()
        self.ser = ser
        self._running = True
        self.serial_lock = Lock()  # Add lock for serial port access
        self.interval_time = interval_time

    def run(self):
        try:
            while self._running:
                if not self.ser.is_open:
                    raise Exception("Serial port is closed")

                with self.serial_lock:  # Acquire lock before serial operations
                    read_registers_command(self.ser, 50, 4)
                    time.sleep(self.interval_time)

        except Exception as e:
            print(f"Send_Read_Reg_Command_Thread error: {e}")
            self.update_signal.emit(f"Send_Read_Reg_Command_Thread error: {str(e)}")
            save_error_to_file("Send_Read_Reg_Command_Thread error:" + str(e))
            self._running = False

    def stop(self):
        self._running = False


class ReadThread(QThread):
    update_signal = pyqtSignal(dict)

    def __init__(self, ser, switches, numeric_up_downs, textboxes, Assign_number_to_LCD_mode_FUNC, update_textboxes_related_to_received_data_FUNC):
        super().__init__()
        self.ser = ser
        self.switches = switches
        self.numeric_up_downs = numeric_up_downs
        self._running = True
        self.Flag_Save_data_in_buffer = False
        self.textboxes = textboxes
        self.Assign_number_to_LCD_mode_FUNC = Assign_number_to_LCD_mode_FUNC
        self.serial_lock = Lock()  # Use the same lock type for serial port access
        self.update_textboxes_related_to_received_data_FUNC = update_textboxes_related_to_received_data_FUNC
    def run(self):
        try:
            while self._running:
                if not self.ser.is_open:
                    raise Exception("Serial port is closed")

                with self.serial_lock:  # Acquire lock before serial operations
                    available_bytes = self.ser.in_waiting
                    if available_bytes > 0:
                        try:
                            response = self.ser.read(available_bytes)
                            response = self.preprocess_received_bytes(response) # Check if Slave Address is 0x02 and seperates data
                            if(response is not None):
                                translated_data, commands = self.process_received_bytes(response)
                                self.update_signal.emit(translated_data) # running update_textboxes_related_to_received_data in UI_Main

                                if self.Flag_Save_data_in_buffer:

                                    Received_data_handler_instance.add_data_to_buffer(
                                        translated_data,
                                        commands,
                                        Assign_number_to_LCD_mode_FUNC=self.Assign_number_to_LCD_mode_FUNC
                                    )
                        except Exception as e:
                            print(f"ReadThread error1: {e}")
                            save_error_to_file("ReadThread error1:" + str(e))


                time.sleep(0.05)

        except Exception as e:
            print(f"ReadThread error2: {e}")
            self.update_signal.emit(f"ReadThread error: {str(e)}")
            save_error_to_file("ReadThread error2:" + str(e))
            self._running = False
            if str(e)!= "Serial port is closed":
                self.restart_thread()

    def preprocess_received_bytes(self, response):
        for i in range(len(response) - 3):
            if response[i] == 0x02 :
              try:
                   print(int(response[i+2]))
                   seperated_response = response[i: int(response[i+2])+5 ]
                   return seperated_response
              except Exception as e:
                  print(f"preprocess_received_bytes error: {e}")
                  save_error_to_file("preprocess_received_bytes error:" + str(e))
            else:
                # print("*******************")
                # print("preprocess_received_bytes returned NONE")
                # print(response)
                # print("*******************")
                return None

    def process_received_bytes(self, response):
        try:
            calculated_crc = calc_crc(response[:-2])
            received_crc = response[-2] | (response[-1] << 8)

            if calculated_crc == received_crc:
                print("Correct CRC")
                if response[1] == 0x10 and response[0] == SLAVE_ADDRESS:
                    self.Compare_with_acknowledge(response)
                elif response[1] == 0x04 and response[0] == SLAVE_ADDRESS:

                    commands = {}
                    commands.update(self.switches.copy())  # Create copies
                    commands.update(self.numeric_up_downs.copy())
                    translated_data = self.Translate_Received_response(
                        response,
                        self.textboxes.copy(),
                        commands,
                        self.Flag_Save_data_in_buffer
                    )

                    return translated_data, commands

            else:
                print("Wrong CRC")
        except Exception as e:
            print(f"process_received_bytes error: {e}")
            save_error_to_file("process_received_bytes error" + str(e))

    def Translate_Received_response(self, response, textboxes, commands, Flag_Save_data_in_buffer):
        try:
            values = {}
            for i, key in enumerate(textboxes.keys()):
                value = (response[i * 2 + 3] << 8) | response[i * 2 + 1 + 3]

                if key in ('Temperature', 'Drive Current'):
                    value /= 10

                values[key] = value;

                print(f"key: {key}, value: {value}")



            return values
        except Exception as e:
            print(f"Translate_Received_response error: {e}")
            save_error_to_file("Translate_Received_response error: " + str(e))

    def stop(self):
        self._running = False

    def restart_thread(self):
        self._running = True

        print("Restarting ReadThread...")
        self.run();






