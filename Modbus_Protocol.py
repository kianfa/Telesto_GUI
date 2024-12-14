import serial
import time
from PyQt5.QtCore import QThread, pyqtSignal
SLAVE_ADDRESS = 0x00;
from Received_data_handler import Received_data_handler_instance

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


def write_single_register(ser, address, value):
    buf = [SLAVE_ADDRESS, 0x06, (address >> 8) & 0xFF, address & 0xFF,
           (value >> 8) & 0xFF, value & 0xFF]

    crc = calc_crc(buf)
    buf.append(crc & 0xFF)  # CRC Low byte
    buf.append((crc >> 8) & 0xFF)  # CRC High byte

    ser.write(bytes(buf))


def write_multiple_registers(ser, start_address, values):
    count = len(values)
    buf = [SLAVE_ADDRESS, 0x10, (start_address >> 8) & 0xFF, start_address & 0xFF,
           (count >> 8) & 0xFF, count & 0xFF, count * 2]

    for value in values:
        buf.append((value >> 8) & 0xFF)
        buf.append(value & 0xFF)

    crc = calc_crc(buf)
    buf.append(crc & 0xFF)  # CRC Low byte
    buf.append((crc >> 8) & 0xFF)  # CRC High byte
    ser.write(bytes(buf))

def read_register(ser, address, count):
    """Read holding registers."""
    buf = [SLAVE_ADDRESS, 0x04, (address >> 8) & 0xFF, address & 0xFF,
           (count >> 8) & 0xFF, count & 0xFF]

    crc = calc_crc(buf)
    buf.append(crc & 0xFF)  # CRC Low byte
    buf.append((crc >> 8) & 0xFF)  # CRC High byte

    ser.write(bytes(buf))

    # Read response
    response = ser.read(5 + count * 2)  # 5 bytes header + 2 bytes per register

class WriteThread(QThread):
    """Thread for writing registers periodically."""
    update_signal = pyqtSignal(str)

    def __init__(self, ser, switches, numeric_up_downs, Assign_number_to_LCD_mode_FUNC):
        super().__init__()
        self.ser = ser
        self.switches = switches
        self.numeric_up_downs = numeric_up_downs
        self._running = True  # Control flag for the thread
        self.Assign_number_to_LCD_mode_FUNC = Assign_number_to_LCD_mode_FUNC;
    def run(self):

        try:

            while self._running:
                Reg_Values = collect_reg_vals_from_user_commands(self.switches, self.numeric_up_downs, self.Assign_number_to_LCD_mode_FUNC)
                write_multiple_registers(self.ser, 20, Reg_Values)
                self.update_signal.emit(f"Wrote registers: {Reg_Values}")
                time.sleep(0.4)  # Delay between writes
        except Exception as e:
            print(f"WriteThread error: {e}")

    def stop(self):
        """Stop the thread safely."""
        self._running = False


class ReadThread(QThread):
    """Thread for reading registers."""
    update_signal = pyqtSignal(str)

    def __init__(self, ser, switches, numeric_up_downs):
        super().__init__()
        self.ser = ser
        self.switches = switches
        self.numeric_up_downs = numeric_up_downs
        self._running = True  # Control flag for the thread
        self.Flag_Save_data_in_buffer = False

    def run(self):
        try:
            while self._running:
                available_bytes = self.ser.in_waiting
                if available_bytes > 0:
                    response = self.ser.read(available_bytes)
                    process_received_bytes(response)
                else:
                    print("No response received.")
                time.sleep(0.3)  # Delay between reads
        except Exception as e:
            print(f"ReadThread error: {e}")

    def stop(self):
        """Stop the thread safely."""
        self._running = False
    def process_received_bytes(self, response):
        calculated_crc = calc_crc(response[:-2])
        received_crc = response[-2] | (response[-1] << 8)

        if(calculated_crc == received_crc):
            if(response[1] == 0x10):
                Compare_with_acknowledge(response);
            elif(response[1] == 0x04):
                Translate_Received_response(response, self.Flag_Save_data_in_buffer);
        else:
            print("Wrong CRC")


    def Compare_with_acknowledge(self, response):
        # ?
        return 0;

    def Translate_Received_response(response, textboxes, Flag_Save_data_in_buffer):
        for i,key in textboxes.keys():
            textboxes[key] = response[i]<<8 | response[i+1]
        if Flag_Save_data_in_buffer:
            add_data_to_buffer(time, textboxes)




def collect_reg_vals_from_user_commands(switches, numeric_up_downs, Assign_number_to_LCD_mode_FUNC):
    values = []
    values.append(switches["Power Mode"].isChecked());
    values.append(switches["Relay"].isChecked());
    values.append(switches["Pump"].isChecked());
    values.append(switches["Output Valve"].isChecked());
    values.append(Assign_number_to_LCD_mode_FUNC());
    values.append(numeric_up_downs["Speed Reference"].value());
    return values;




