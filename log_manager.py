import os
import time
from datetime import datetime, timedelta

def delete_old_logs(log_dir='.', days_threshold=30):
    """
    Delete old log files in the specified directory.
    :param log_dir: Log file directory, defaults to the current directory
    :param days_threshold: Threshold for deleting logs, defaults to 30 days
    """
    # Acquire the current time
    now = time.time()
    # Calculate the time threshold for deleting logs
    threshold_time = now - days_threshold * 24 * 60 * 60

    # Traverse the log file directory
    for root, dirs, files in os.walk(log_dir):
        for file in files:
            # Get the full path of the file
            file_path = os.path.join(root, file)
            try:
                # Get the modification time of the file
                file_mtime = os.path.getmtime(file_path)
                # Compare the modification time with the threshold time
                if file_mtime < threshold_time:
                    # Delete the file
                    os.remove(file_path)
                    print(f"Deleted old log file: {file_path}")
            except Exception as e:
                print(f"Error deleting file {file_path}: {e}")

if __name__ == "__main__":
    # Call the function to delete old log files
    delete_old_logs()