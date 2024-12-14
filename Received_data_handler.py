import pandas as pd




class Received_data_handler():
    def __init__(self):
        self.buffer_of_received_data = {
            "Time": [],
            "Temperature": [],
            "Drive Current": [],
            "RPM": [],
            "Drive Voltage": []
        }

    def add_data_to_buffer(self, sample):
        """Add received data to the buffer based on the data type."""
        timestamp = datetime.datetime.now()
        self.buffer_of_received_data["Time"].append(timestamp)
        self.buffer_of_received_data["Temperature"].append(sample["Temperature"])
        self.buffer_of_received_data["Drive Current"].append(sample["Drive Current"])
        self.buffer_of_received_data["RPM"].append(sample["RPM"])
        self.buffer_of_received_data["Thermostat Current"].append(sample["Thermostat Current"])

    # def get_data(self, data_type):
    #     """Retrieve data associated with a specific data type."""
    #     return self.buffer_of_received_data.get(data_type, [])

    def clear_data(self):
        """Clear all data in the buffer."""
        self.buffer_of_received_data = {
            "Time": [],
            "Temperature": [],
            "Drive Current": [],
            "RPM": [],
            "Thermostat Current": []
        }
        print("All data has been cleared.")

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
        df = pd.DataFrame(self.buffer_of_received_data)
        if( not path.endswith(".xlsx")):
            path = path + '.xlsx'

        try:
            # Write the DataFrame to the specified Excel file
            df.to_excel(path, index=False)
            print(f"Data saved to {path}")
        except Exception as e:
            print(f"Saving to Excel failed: {e}")



Received_data_handler_instance = Received_data_handler()