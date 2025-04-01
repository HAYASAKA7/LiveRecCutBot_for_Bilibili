import logging
import os
from datetime import datetime

def setup_logger():
    log_dir = "Logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    current_date = datetime.now().strftime("%Y-%m-%d")
    log_file = os.path.join(log_dir, f"{current_date}.log")

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    logger.propagate = False

    if not logger.hasHandlers():
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger
    