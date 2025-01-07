
import os
from datetime import datetime


def save_error_to_file(error_message, filename='error_log.txt'):
    # Get the current date and time
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # Create a formatted error message with the timestamp
    formatted_message = f"{timestamp} - {error_message}"

    try:
        # Check if the file exists
        if not os.path.isfile(filename):
            print(f"{filename} does not exist. Creating a new file.")

        # Open the file and append the error message
        with open(filename, 'a') as file:
            file.write(formatted_message + '\n')
            print("Error has been logged.")

        print("Current Working Directory:", os.getcwd())

    except Exception as error:
        print(f"Error while writing to the log file: {error}")



