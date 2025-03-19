import os
import threading
import time
from PyQt5.QtWidgets import QWidget, QGridLayout, QPushButton, QFileDialog, QLabel, QLineEdit, QMessageBox, QProgressBar, QSystemTrayIcon, QMenu, QApplication,QStackedWidget,QTextEdit
from PyQt5.QtGui import QIcon
from flask_app import app
from logger_config import setup_logger

logger = setup_logger()

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        import global_vars
        self.default_video_output = global_vars.OUTPUT_VIDEO_DIR
        self.default_image_output = global_vars.OUTPUT_IMAGE_DIR
        self.default_clips_output = global_vars.OUTPUT_CLIPS_DIR
        self.current_video_output = self.default_video_output
        self.current_image_output = self.default_image_output
        self.current_clips_output = self.default_clips_output
        self.initUI()
        self.flask_thread = None
        self.start_time = None
        self.total_size = 0
        self.processed_size = 0
        self.setup_tray_icon()

        logger.info("Main window initialized.")

    def initUI(self):
        layout = QGridLayout()

        # self.stacked_widget = QStackedWidget()

        # operation_page = QWidget()
        # operation_layout = QGridLayout()

        # Set font and font size style
        font_style = "font-family: Arial; font-size: 14px;"

        self.video_label = QLabel("No video file selected")
        self.video_label.setStyleSheet(font_style)
        layout.addWidget(self.video_label, 0, 0)

        self.danmaku_label = QLabel("No danmaku file selected")
        self.danmaku_label.setStyleSheet(font_style)
        layout.addWidget(self.danmaku_label, 1, 0)

        video_button = QPushButton("Select Video File")
        video_button.setStyleSheet(font_style)
        video_button.clicked.connect(self.select_video)
        layout.addWidget(video_button, 2, 0)

        danmaku_button = QPushButton("Select Danmaku File")
        danmaku_button.setStyleSheet(font_style)
        danmaku_button.clicked.connect(self.select_danmaku)
        layout.addWidget(danmaku_button, 3, 0)

        process_button = QPushButton("Process Video")
        process_button.setStyleSheet(font_style)
        process_button.clicked.connect(self.process_video)
        layout.addWidget(process_button, 4, 0)

        # Add a button to process only danmaku file
        process_danmaku_button = QPushButton("Process Danmaku Only")
        process_danmaku_button.setStyleSheet(font_style)
        process_danmaku_button.clicked.connect(self.process_danmaku_only)
        layout.addWidget(process_danmaku_button, 5, 0)

        # Add an input box for the Webhook interface
        self.webhook_input = QLineEdit()
        self.webhook_input.setStyleSheet(font_style)
        self.webhook_input.setPlaceholderText("Enter the Webhook interface address")
        layout.addWidget(self.webhook_input, 6, 0)

        start_listening_button = QPushButton("Start Listening")
        start_listening_button.setStyleSheet(font_style)
        start_listening_button.clicked.connect(self.start_listening)
        layout.addWidget(start_listening_button, 7, 0)

        # Add buttons to select output paths in the second column
        select_video_output_button = QPushButton("Select Video Output Path")
        select_video_output_button.setStyleSheet(font_style)
        select_video_output_button.clicked.connect(self.select_video_output_path)
        layout.addWidget(select_video_output_button, 0, 1)

        # Display the default path and selected path
        self.video_output_label = QLabel(f"Default: {self.default_video_output}\nCurrent: {self.current_video_output}")
        self.video_output_label.setStyleSheet(font_style)
        layout.addWidget(self.video_output_label, 1, 1)

        # Add buttons to select output paths in the second column
        select_image_output_button = QPushButton("Select Image Output Path")
        select_image_output_button.setStyleSheet(font_style)
        select_image_output_button.clicked.connect(self.select_image_output_path)
        layout.addWidget(select_image_output_button, 2, 1)

        # Display the default path and selected path
        self.image_output_label = QLabel(f"Default: {self.default_image_output}\nCurrent: {self.current_image_output}")
        self.image_output_label.setStyleSheet(font_style)
        layout.addWidget(self.image_output_label, 3, 1)

        # Add buttons to select output paths in the second column
        select_clips_output_button = QPushButton("Select Clips Output Path")
        select_clips_output_button.setStyleSheet(font_style)
        select_clips_output_button.clicked.connect(self.select_clips_output_path)
        layout.addWidget(select_clips_output_button, 4, 1)

        # Display the default path and selected path
        self.clips_output_label = QLabel(f"Default: {self.default_clips_output}\nCurrent: {self.current_clips_output}")
        self.clips_output_label.setStyleSheet(font_style)
        layout.addWidget(self.clips_output_label, 5, 1)

        # Progress bar
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setStyleSheet("QProgressBar::chunk { background-color: green; }")
        self.progress_bar.setRange(0, 100)
        layout.addWidget(self.progress_bar, 8, 0, 1, 2)

        # Time display label
        self.time_label = QLabel("Elapsed Time: 0s, Expected Time Left: N/A")
        self.time_label.setStyleSheet(font_style)
        layout.addWidget(self.time_label, 9, 0, 1, 2)

        self.setLayout(layout)
        self.setWindowTitle('LiveReCBot')
        self.setGeometry(300, 300, 600, 400)  # Increase the window height appropriately to accommodate the progress bar and time display
        self.show()
        logger.info("UI initialized.")

    def select_video(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Video File", "", "Video files (*.mp4)")
        if file_path:
            self.video_path = file_path
            self.video_label.setText(f"Selected Video File: {os.path.basename(file_path)}")
            logger.info(f"Video file selected: {file_path}")

    def select_danmaku(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Danmaku File", "", "XML files (*.xml)")
        if file_path:
            self.danmaku_path = file_path
            self.danmaku_label.setText(f"Selected Danmaku File: {os.path.basename(file_path)}")
            logger.info(f"Danmaku file selected: {file_path}")

    def process_video(self):
        if hasattr(self, 'video_path') and hasattr(self, 'danmaku_path'):
            self.total_size = os.path.getsize(self.video_path) + os.path.getsize(self.danmaku_path)
            self.processed_size = 0
            self.start_time = time.time()
            threading.Thread(target=self._process_video_thread).start()
            logger.info("Video processing started.")

    def _process_video_thread(self):
        from xml_parser import parse_xml
        from density_calculator import calculate_density, calculate_minute_density
        from curve_plotter import plot_density_curve
        import global_vars
        timestamps, video_duration = parse_xml(self.danmaku_path)
        bins, density = calculate_density(timestamps)
        minute_bins, minute_density = calculate_minute_density(timestamps, video_duration)
        output_video_name = os.path.basename(self.video_path).replace('.mp4', '')
        image_path = os.path.join(global_vars.OUTPUT_IMAGE_DIR, f"{output_video_name}_danmaku_density.png")
        output_clips_dir = os.path.join(global_vars.OUTPUT_CLIPS_DIR, f"{output_video_name}_clips")
        output_video = os.path.join(global_vars.OUTPUT_VIDEO_DIR, f"{output_video_name}.mp4")

        steps = 100  # Assume divided into 100 steps
        step_size = self.total_size / steps
        for i in range(steps):
            # Simulate the processing progress
            time.sleep(0.1)  # Simulate the processing time
            self.processed_size += step_size
            elapsed_time = time.time() - self.start_time
            speed = self.processed_size / elapsed_time if elapsed_time > 0 else 0
            remaining_size = self.total_size - self.processed_size
            expected_time = remaining_size / speed if speed > 0 else 0

            self.progress_bar.setValue(i + 1)
            self.time_label.setText(f"Elapsed Time: {elapsed_time:.2f}s, Expected Time Left: {expected_time:.2f}s")
            logger.debug(f"Video processing progress: {i + 1}%")

        plot_density_curve(bins, density, minute_bins, minute_density, image_path, video_duration, output_video,
                           output_clips_dir)
        logger.info("Video processing completed.")

    def process_danmaku_only(self):
        if hasattr(self, 'danmaku_path'):
            self.total_size = os.path.getsize(self.danmaku_path)
            self.processed_size = 0
            self.start_time = time.time()
            threading.Thread(target=self._process_danmaku_only_thread).start()
            logger.info("Danmaku processing started.")

    def _process_danmaku_only_thread(self):
        from xml_parser import parse_xml
        from density_calculator import calculate_density, calculate_minute_density
        from curve_plotter import plot_density_curve
        import global_vars
        timestamps, video_duration = parse_xml(self.danmaku_path)
        bins, density = calculate_density(timestamps)
        minute_bins, minute_density = calculate_minute_density(timestamps, video_duration)
        output_danmaku_name = os.path.basename(self.danmaku_path).replace('.xml', '')
        image_path = os.path.join(global_vars.OUTPUT_IMAGE_DIR, f"{output_danmaku_name}_danmaku_density.png")

        steps = 100  # Assume divided into 100 steps
        step_size = self.total_size / steps
        for i in range(steps):
            # Simulate the processing progress
            time.sleep(0.1)  # Simulate the processing time
            self.processed_size += step_size
            elapsed_time = time.time() - self.start_time
            speed = self.processed_size / elapsed_time if elapsed_time > 0 else 0
            remaining_size = self.total_size - self.processed_size
            expected_time = remaining_size / speed if speed > 0 else 0

            self.progress_bar.setValue(i + 1)
            self.time_label.setText(f"Elapsed Time: {elapsed_time:.2f}s, Expected Time left: {expected_time:.2f}s")
            logger.debug(f"Danmaku processing progress: {i + 1}%")

        plot_density_curve(bins, density, minute_bins, minute_density, image_path, video_duration, None, None)
        logger.info("Danmaku processing completed.")

    def select_video_output_path(self):
        path = QFileDialog.getExistingDirectory(self, "Select Video Output Path")
        if path:
            import global_vars
            global_vars.OUTPUT_VIDEO_DIR = path
            logger.info(f"Video Output Path Selected: {path}")

    def select_image_output_path(self):
        path = QFileDialog.getExistingDirectory(self, "Select Image Output Path")
        if path:
            import global_vars
            global_vars.OUTPUT_IMAGE_DIR = path
            logger.info(f"Image )utput Path Selected: {path}")

    def select_clips_output_path(self):
        path = QFileDialog.getExistingDirectory(self, "Select Clips Output Path")
        if path:
            import global_vars
            global_vars.OUTPUT_CLIPS_DIR = path
            logger.info(f"Clips Output Path Selected: {path}")

    def start_listening(self):
        webhook_url = self.webhook_input.text()
        if not webhook_url:
            QMessageBox.warning(self, "Input Error", "Please enter the Webhook interface address")
            logger.warning("Webhook interface address not provided.")
            return

        if self.flask_thread is None or not self.flask_thread.is_alive():
            # Simplified processing here, only printing information. In reality, the Flask route needs to be modified according to the input address.
            self.flask_thread = threading.Thread(target=app.run, kwargs={'host': '0.0.0.0', 'port': 5000})
            self.flask_thread.start()
            logger.info(f"Started listening on Webhook interface: {webhook_url}")

    def setup_tray_icon(self):
        try:
            icon_path = 'D:/Projects/Python/RecBot+AutoCut/LRB.png'
            if not os.path.exists(icon_path):
                logger.error(f"Icon file not found at {icon_path}")
                return
            self.tray_icon = QSystemTrayIcon(self)
            icon = QIcon(icon_path)
            if icon.isNull():
                logger.error(f"Failed to load icon from {icon_path}")
                return
            self.tray_icon.setIcon(icon)
            self.tray_icon.setToolTip('LiveReCBot')
            self.tray_icon.activated.connect(self.tray_icon_activated)

            menu = QMenu(self)
            exit_action = menu.addAction("Exit")
            exit_action.triggered.connect(self.close_app)

            self.tray_icon.setContextMenu(menu)
            if not self.tray_icon.show():
                logger.error("Failed to show system tray icon")
            else:
                logger.info("System tray icon setup and shown.")
        except Exception as e:
            logger.error(f"Error setting up system tray icon: {e}")

    def tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            if self.isHidden():
                self.showNormal()
                logger.info("Window shown from system tray.")
            else:
                self.hide()
                logger.info("Window hidden to system tray.")

    def closeEvent(self, event):
        print("Close event triggered")
        event.ignore()
        self.hide()
        if self.tray_icon.isVisible():
            print("Tray icon is visible")
            logger.info("Window closed, minimized to system tray.")
        else:
            print("Tray icon is not visible")
            logger.warning("System tray icon not visible on window close.")

    def close_app(self):
        QApplication.quit()
        logger.info("Application closed.")
        logger.info("")