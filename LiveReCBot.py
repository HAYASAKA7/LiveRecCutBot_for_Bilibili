import sys
from logger_config import setup_logger
from PyQt5.QtWidgets import QApplication
from main_window import MainWindow
from flask_app import app
from log_manager import delete_old_logs

logger = setup_logger()

if __name__ == '__main__':
    try:
        delete_old_logs(log_dir='Logs', days_threshold=7)
        app_thread = None
        app = QApplication(sys.argv)
        window = MainWindow()
        # Implement the function of minimizing to the taskbar
        window.showMinimized = lambda: window.hide()
        logger.info("Application started.")
        sys.exit(app.exec_())
    except Exception as e:
        logger.error(f"Application failed to start: {e}")
    