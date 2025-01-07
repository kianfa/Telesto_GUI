import pandas as pd
import datetime

class Received_data_handler():
    def __init__(self):

        self.Clear_buffer_of_data()

    def add_data_to_buffer(self, sample, Commands, Assign_number_to_LCD_mode_FUNC):
        """Add received data to the buffer based on the data type."""
        timestamp = datetime.datetime.now()
        self.buffer_of_received_data_and_commands["Time"].append(timestamp)
        self.buffer_of_received_data_and_commands["Temperature"].append(sample["Temperature"])
        self.buffer_of_received_data_and_commands["Drive Current"].append(sample["Drive Current"])
        self.buffer_of_received_data_and_commands["RPM"].append(sample["RPM"])
        self.buffer_of_received_data_and_commands["Drive Voltage"].append(sample["Drive Voltage"])
        self.buffer_of_received_data_and_commands["Power Mode"].append(Commands["Power Mode"].isChecked())
        self.buffer_of_received_data_and_commands["Relay"].append(Commands["Relay"].isChecked())
        self.buffer_of_received_data_and_commands["Pump"].append(Commands["Pump"].isChecked())
        self.buffer_of_received_data_and_commands["Output Valve"].append(Commands["Output Valve"].isChecked())
        self.buffer_of_received_data_and_commands["LCD Mode (0:off,1:Dim,2:Bright)"].append(Assign_number_to_LCD_mode_FUNC())
        self.buffer_of_received_data_and_commands["Speed Reference"].append(Commands["Speed Reference"].value())

    # def get_data(self, data_type):
    #     """Retrieve data associated with a specific data type."""
    #     return self.buffer_of_received_data.get(data_type, [])
    def Clear_buffer_of_data(self):
        self.buffer_of_received_data_and_commands = self.Empty_buffer_of_data()

    def Empty_buffer_of_data(self):
        """Clear all data in the buffer."""
        init_buffer_of_received_data_and_commands = {
            "Time": [],
            "Temperature": [],
            "Drive Current": [],
            "RPM": [],
            "Drive Voltage": [],
            "Power Mode": [],
            "Relay": [],
            "Pump": [],
            "Output Valve": [],
            "LCD Mode (0:off,1:Dim,2:Bright)": [],
            "Speed Reference": []
        }
        # self.buffer_of_received_data_and_commands = self.init_buffer_of_received_data_and_commands.copy()
        return init_buffer_of_received_data_and_commands

    # def process_data(self, response):
    #     """Process the received data for a specific data type."""
    #     data = self.get_data(data_type)
    #     if data:
    #         # Example processing: just print the data
    #         print(f"Processing {data_type}: {data}")
    #     else:
    #         print(f"No data found for {data_type}.")
    #
    # def display_all_data(self):
    #     """Display all received data in the buffer."""
    #     for key, data in self.buffer_of_received_data.items():
    #         print(f"{key}: {data}")

    def save_to_excel(self, path):
        """Save the received data to an Excel file at the specified path."""
        # Create a DataFrame from the buffer
        df = pd.DataFrame(self.buffer_of_received_data_and_commands)
        if(not path.endswith(".xlsx")):
            path = path + '.xlsx'

        try:
            # Write the DataFrame to the specified Excel file
            df.to_excel(path, index=False)
            print(f"Data saved to {path}")
        except Exception as e:
            print(f"Saving to Excel failed: {e}")
            save_error_to_file("Saving to Excel failed:" + str(e))



# Received_data_handler_instance = Received_data_handler()


class Received_data_handlerInitializer:
    _instance = None

    @classmethod
    def initialize(cls):
        if cls._instance is None:
            cls._instance = Received_data_handler()
        return cls._instance

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            return cls.initialize()
        return cls._instance

Received_data_handler_instance = Received_data_handlerInitializer.initialize()
