import os
import sys
import threading
import time
import json
import global_vars
from PyQt5.QtWidgets import QWidget, QComboBox,QGridLayout, QPushButton, QFileDialog, QLabel, QLineEdit, QMessageBox, QSystemTrayIcon, QMenu, QApplication, QVBoxLayout, QMainWindow, QTabWidget, QProgressBar
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, Q_ARG,QEvent, QMetaObject
from flask_app import app
from logger_config import setup_logger
from xml_parser import parse_xml
from density_calculator import calculate_density, calculate_minute_density
from curve_plotter import plot_density_curve
import global_vars
import webhook_listener

logger = setup_logger()

CONFIG_FILE = "config.json"

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LiveRecBot")
        self.tabs = QTabWidget(self)
        self.setGeometry(0, 0, 800, 600)

        self.default_video_output = global_vars.OUTPUT_VIDEO_DIR
        self.default_image_output = global_vars.OUTPUT_IMAGE_DIR
        self.default_clips_output = global_vars.OUTPUT_CLIPS_DIR
        self.current_video_output = self.default_video_output
        self.current_image_output = self.default_image_output
        self.current_clips_output = self.default_clips_output
        
        self.translations = {}
        self.language = self.load_language_preference()
        self.load_translations(self.language)

        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tab3 = QWidget()

        self.tabs.addTab(self.tab1, "Main Functions")
        self.tabs.addTab(self.tab2, "File Paths")
        self.tabs.addTab(self.tab3, "Settings")

        self.init_tab1()
        self.init_tab2()
        self.init_tab3()

        self.tabs.setGeometry(10, 10, 780, 580)

        self.initUI()

        self.flask_thread = None
        self.start_time = None
        self.total_size = 0
        self.processed_size = 0
        self.setup_tray_icon()

        logger.info("Main window initialized.")

    def save_encoder_settings(self):
        selected_option = self.encoder_combo_box.currentText()
        if "Intel" in selected_option:
            self.selected_encoder = "h264_qsv"
        elif "AMD" in selected_option:
            self.selected_encoder = "libx264"
        elif "NVIDIA" in selected_option:
            self.selected_encoder = "h264_nvenc"
        logger.info(f"Encode mode has been set to {self.selected_encoder}")

    def select_base_path(self):
        path = QFileDialog.getExistingDirectory(self, "Select Base Path")
        if path:
            self.base_path = path
            global_vars.BASE_PATH = self.base_path
            logger.info(f"Base Path Selected: {path}")

    def load_language_preference(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r", encoding="utf-8") as file:
                config = json.load(file)
                return config.get("language", "en")
        return "en"

    def save_language_preference(self, language):
        config = {"language": language}
        with open(CONFIG_FILE, "w", encoding="utf-8") as file:
            json.dump(config, file)

    def load_translations(self, language):
        try:
            base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
            translation_file = os.path.join(base_path, f"translations/LRB_{language}.json")
            with open(f"translations/LRB_{language}.json", "r", encoding="utf-8") as file:
                self.translations = json.load(file)
            logger.info(f"Loaded translation file: LRB_{language}.json")
        except FileNotFoundError:
            logger.warning(f"Translation file not found: LRB_{language}.json")
            self.translations = {}
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON from translation file: {e}")
            self.translations = {}

    def tr(self, text):
        return self.translations.get(text, text)
    def switch_language(self, language):
        try:
            self.language = language
            self.save_language_preference(language)
            self.load_translations(language)
            self.update_ui_texts()
        except Exception as e:
            logger.error(f"Error switching language: {e}")
            QMessageBox.critical(self, "Error", self.tr(f"Failed to switch language: {e}"))

    def update_ui_texts(self):
        try:
            self.video_label.setText(self.tr("No video file selected"))
            self.danmaku_label.setText(self.tr("No danmaku file selected"))
            self.video_button.setText(self.tr("Select Video File"))
            self.danmaku_button.setText(self.tr("Select Danmaku File"))
            self.process_button.setText(self.tr("Process Video"))
            self.process_danmaku_button.setText(self.tr("Process Danmaku Only"))
            self.webhook_input.setPlaceholderText(self.tr("Enter the Webhook interface address"))
            self.start_listening_button.setText(self.tr("Start Listening"))
            self.select_video_output_button.setText(self.tr("Select Video Output Path"))
            self.select_image_output_button.setText(self.tr("Select Image Output Path"))
            self.video_output_label.setText(f"{self.tr('Default')}: {self.default_video_output}\n{self.tr('Current')}: {self.current_video_output}")
            self.image_output_label.setText(f"{self.tr('Default')}: {self.default_image_output}\n{self.tr('Current')}: {self.current_image_output}")
            self.clips_output_label.setText(f"{self.tr('Default')}: {self.default_clips_output}\n{self.tr('Current')}: {self.current_clips_output}")
            self.select_clips_output_button.setText(self.tr("Select Clips Output Path"))
            self.elapsed_time_label.setText(self.tr("Elapsed Time: 0.00s"))
            self.remaining_time_label.setText(self.tr("Expected Time Left: 0.00s"))
            self.encoder_label.setText(self.tr("Select encode mode:"))
            self.save_button.setText(self.tr("Save Settings"))
            self.tabs.setTabText(0, self.tr("Main Functions"))
            self.tabs.setTabText(1, self.tr("File Paths"))
            self.tabs.setTabText(2, self.tr("Settings"))
            self.language_button.setText(self.tr("Switch Language"))
            self.language_buttons.clear()
            self.language_buttons.addAction(self.tr("English"), lambda: self.switch_language("en"))
            self.language_buttons.addAction(self.tr("Chinese"), lambda: self.switch_language("zh"))
            self.language_buttons.addAction(self.tr("Japanese"), lambda: self.switch_language("ja"))
        except Exception as e:
            logger.error(f"Error updating UI texts: {e}")
            QMessageBox.critical(self, "Error", self.tr(f"Failed to update UI texts: {e}"))

    def initUI(self):
        icon_path = 'D:/Projects/Python/RecBot+AutoCut/LRB.png'
        if not os.path.exists(icon_path):
            logger.error(f"Icon file not found at {icon_path}")
        else:
            self.setWindowIcon(QIcon(icon_path))
            logger.info("Window icon set.")

        logger.info("UI initialized.")

    def init_tab1(self):
        layout = QGridLayout()

        font_style = "font-family: Arial; font-size: 14px;"

        self.video_label = QLabel("No video file selected")
        self.video_label.setStyleSheet(font_style)
        layout.addWidget(self.video_label, 0, 0)

        self.video_button = QPushButton("Select Video File")
        self.video_button.setStyleSheet(font_style)
        self.video_button.clicked.connect(self.select_video)
        layout.addWidget(self.video_button, 1, 0)

        self.danmaku_label = QLabel("No danmaku file selected")
        self.danmaku_label.setStyleSheet(font_style)
        layout.addWidget(self.danmaku_label, 2, 0)

        self.danmaku_button = QPushButton("Select Danmaku File")
        self.danmaku_button.setStyleSheet(font_style)
        self.danmaku_button.clicked.connect(self.select_danmaku)
        layout.addWidget(self.danmaku_button, 3, 0)

        self.process_button = QPushButton("Process Video")
        self.process_button.setStyleSheet(font_style)
        self.process_button.clicked.connect(self.process_video)
        layout.addWidget(self.process_button, 4, 0)

        self.process_danmaku_button = QPushButton("Process Danmaku Only")
        self.process_danmaku_button.setStyleSheet(font_style)
        self.process_danmaku_button.clicked.connect(self.process_danmaku_only)
        layout.addWidget(self.process_danmaku_button, 5, 0)
        
        self.webhook_input = QLineEdit()
        self.webhook_input.setStyleSheet(font_style)
        self.webhook_input.setPlaceholderText("Enter the Webhook interface address")
        layout.addWidget(self.webhook_input, 6, 0)

        self.start_listening_button = QPushButton("Start Listening")
        self.start_listening_button.setStyleSheet(font_style)
        self.start_listening_button.clicked.connect(self.start_listening)
        layout.addWidget(self.start_listening_button, 7, 0)

        self.elapsed_time_label = QLabel("Elapsed Time: 0.00s")
        self.elapsed_time_label.setStyleSheet(font_style)
        layout.addWidget(self.elapsed_time_label, 8, 0)

        self.remaining_time_label = QLabel("Expected Time Left: 0.00s")
        self.remaining_time_label.setStyleSheet(font_style)
        layout.addWidget(self.remaining_time_label, 9, 0)

        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet(font_style)
        self.progress_bar.setValue(0)  # Initialize progress bar to 0%
        self.progress_bar.setMaximum(100)  # Set maximum value to 100
        layout.addWidget(self.progress_bar, 10, 0)

        self.tab1.setLayout(layout)

    def init_tab2(self):
        layout = QGridLayout()

        font_style = "font-family: Arial; font-size: 14px;"

        self.select_video_output_button = QPushButton("Select Video Output Path")
        self.select_video_output_button.setStyleSheet(font_style)
        self.select_video_output_button.clicked.connect(self.select_video_output_path)
        layout.addWidget(self.select_video_output_button, 0, 0)

        self.video_output_label = QLabel(f"Default: {self.default_video_output}\nCurrent: {self.current_video_output}")
        self.video_output_label.setStyleSheet(font_style)
        layout.addWidget(self.video_output_label, 1, 0)

        self.select_image_output_button = QPushButton("Select Image Output Path")
        self.select_image_output_button.setStyleSheet(font_style)
        self.select_image_output_button.clicked.connect(self.select_image_output_path)
        layout.addWidget(self.select_image_output_button, 2, 0)

        self.image_output_label = QLabel(f"Default: {self.default_image_output}\nCurrent: {self.current_image_output}")
        self.image_output_label.setStyleSheet(font_style)
        layout.addWidget(self.image_output_label, 3, 0)

        self.select_clips_output_button = QPushButton("Select Clips Output Path")
        self.select_clips_output_button.setStyleSheet(font_style)
        self.select_clips_output_button.clicked.connect(self.select_clips_output_path)
        layout.addWidget(self.select_clips_output_button, 4, 0)

        self.clips_output_label = QLabel(f"Default: {self.default_clips_output}\nCurrent: {self.current_clips_output}")
        self.clips_output_label.setStyleSheet(font_style)
        layout.addWidget(self.clips_output_label, 5, 0)

        self.base_path_button = QPushButton("Select Base Path")
        self.base_path_button.setStyleSheet(font_style)
        self.base_path_button.clicked.connect(self.select_base_path)
        layout.addWidget(self.base_path_button, 6, 0)

        self.tab2.setLayout(layout)

    def init_tab3(self):
        layout = QVBoxLayout()

        font_style = "font-family: Arial; font-size: 14px;"

        self.encoder_label = QLabel("Select encode mode:")
        self.encoder_label.setStyleSheet(font_style)
        layout.addWidget(self.encoder_label)

        self.encoder_combo_box = QComboBox()
        self.encoder_combo_box.addItems(["Intel (h264_qsv)", "AMD (libx264)", "NVIDIA (h264_nvenc)"])
        self.encoder_combo_box.setStyleSheet(font_style)
        layout.addWidget(self.encoder_combo_box)

        self.save_button = QPushButton("Save Settings")
        self.save_button.setStyleSheet(font_style)
        self.save_button.clicked.connect(self.save_encoder_settings)
        layout.addWidget(self.save_button)

        # Add language switch buttons
        self.language_buttons = QMenu(self.tr("Switch Language"))
        self.language_buttons.addAction(self.tr("English"), lambda: self.switch_language("en"))
        self.language_buttons.addAction(self.tr("Chinese"), lambda: self.switch_language("zh"))
        self.language_buttons.addAction(self.tr("Japanese"), lambda: self.switch_language("ja"))
        self.language_button = QPushButton(self.tr("Switch Language"))
        self.language_button.setMenu(self.language_buttons)
        layout.addWidget(self.language_button, alignment=Qt.AlignCenter)
        
        self.tab3.setLayout(layout)

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
        try:
            logger.info("Processing video...")
            if hasattr(self, 'video_path') and hasattr(self, 'danmaku_path'):
                self.total_size = os.path.getsize(self.video_path) + os.path.getsize(self.danmaku_path)
                self.processed_size = 0
                self.start_time = time.time()
                threading.Thread(target=self._process_video_thread).start()
                logger.info("Video processing started.")
            else:
                logger.warning("Video or danmaku file not selected.")
                QMessageBox.warning(self, "Input Error", self.tr("Please select both video and danmaku files"))
        except Exception as e:
            logger.error(f"Error processing video: {e}")
            QMessageBox.critical(self, "Error", self.tr(f"Failed to process video: {e}"))

    def _process_video_thread(self):
        try:
            logger.info("Video processing thread started.")
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
                time.sleep(0.1)  # Simulate the processing time
                self.processed_size += step_size
                elapsed_time = time.time() - self.start_time
                speed = self.processed_size / elapsed_time if elapsed_time > 0 else 0
                remaining_size = self.total_size - self.processed_size
                expected_time = remaining_size / speed if speed > 0 else 0

                QMetaObject.invokeMethod(self.progress_bar, "setValue", Qt.ConnectionType(Qt.QueuedConnection), Q_ARG(int, i + 1))
                QMetaObject.invokeMethod(self.elapsed_time_label, "setText", Qt.ConnectionType(Qt.QueuedConnection),
                             Q_ARG(str, f"Elapsed Time: {elapsed_time:.2f}s"))
                QMetaObject.invokeMethod(self.remaining_time_label, "setText", Qt.ConnectionType(Qt.QueuedConnection),
                             Q_ARG(str, f"Expected Time Left: {expected_time:.2f}s"))

                # self.progress_bar.setValue(i + 1)
                # self.elapsed_time_label.setText(f"Elapsed Time: {elapsed_time:.2f}s")
                # self.remaining_time_label.setText(f"Expected Time Left: {expected_time:.2f}s")

            plot_density_curve(bins, density, minute_bins, minute_density, image_path, video_duration, output_video,
                            output_clips_dir)
            logger.info("Video processing completed.")
        except Exception as e:
            logger.error(f"Error processing video: {e}")
            QMessageBox.critical(self, "Error", self.tr(f"Failed to process video: {e}"))

    def process_danmaku_only(self):
        try:
            logger.info("Processing danmaku only...")
            if hasattr(self, 'danmaku_path'):
                self.total_size = os.path.getsize(self.danmaku_path)
                self.processed_size = 0
                self.start_time = time.time()
                threading.Thread(target=self._process_danmaku_only_thread).start()
                logger.info("Danmaku processing started.")
            else:
                logger.warning("Danmaku file not selected.")
                QMessageBox.warning(self, "Input Error", self.tr("Please select a danmaku file"))
        except Exception as e:
            logger.error(f"Error processing danmaku: {e}")
            QMessageBox.critical(self, "Error", self.tr(f"Failed to process danmaku: {e}"))

    def _process_danmaku_only_thread(self):
        try:
            logger.info("Danmaku processing thread started")
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

                QMetaObject.invokeMethod(self.progress_bar, "setValue", Qt.ConnectionType(Qt.QueuedConnection), Q_ARG(int, i + 1))
                QMetaObject.invokeMethod(self.elapsed_time_label, "setText", Qt.ConnectionType(Qt.QueuedConnection),
                             Q_ARG(str, f"Elapsed Time: {elapsed_time:.2f}s"))
                QMetaObject.invokeMethod(self.remaining_time_label, "setText", Qt.ConnectionType(Qt.QueuedConnection),
                             Q_ARG(str, f"Expected Time Left: {expected_time:.2f}s"))
                # self.progress_bar.setValue(i + 1)
                # self.elapsed_time_label.setText(f"Elapsed Time: {elapsed_time:.2f}s")
                # self.remaining_time_label.setText(f"Expected Time Left: {expected_time:.2f}s")

            plot_density_curve(bins, density, minute_bins, minute_density, image_path, video_duration, None, None)
            logger.info("Danmaku processing completed.")
            QMetaObject.invokeMethod(self.progress_bar, "set_value", Qt.ConnectionType(Qt.QueuedConnection), Q_ARG(int, 100))
        except Exception as e:
            logger.error(f"Error processing danmaku: {e}")
            QMessageBox.critical(self, "Error", self.tr(f"Failed to process danmaku: {e}"))

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
            QMessageBox.warning(self, "Input Error", self.tr("Please enter the Webhook interface address"))
            logger.warning("Webhook interface address not provided.")
            return

        if self.flask_thread is None or not self.flask_thread.is_alive():
            # Simplified processing here, only printing information. In reality, the Flask route needs to be modified according to the input address.
            self.flask_thread = threading.Thread(target=app.run, kwargs={'host': '0.0.0.0', 'port': 5000})
            self.flask_thread.start()
            logger.info(f"Started listening on Webhook interface: {webhook_url}")
        try:
            selected_option = self.encoder_combo_box.currentText()
            if "Intel" in selected_option:
                selected_encoder = "h264_qsv"
            elif "AMD" in selected_option:
                selected_encoder = "libx264"
            elif "NVIDIA" in selected_option:
                selected_encoder = "h264_nvenc"
            else:
                selected_encoder = "h264_qsv" 

            webhook_listener.selected_encoder = selected_encoder
            logger.info(f"Webhook listener started with encoder: {selected_encoder}")

            threading.Thread(target=app.run, kwargs={"host": "0.0.0.0", "port": 5000}).start()
            logger.info("Webhook listener started.")
        except Exception as e:
            logger.error(f"Error starting webhook listener: {e}")

    def setup_tray_icon(self):
        try:
            icon_path = 'D:/Projects/Python/RecBot+AutoCut/LRB.png'
            if not os.path.exists(icon_path):
                logger.error(f"Icon file not found at {icon_path}")
                return
            self.tray_icon = QSystemTrayIcon(self)
            icon = QIcon(icon_path)
            self.tray_icon.setIcon(icon)
            self.tray_icon.setToolTip('LiveReCBot')
            self.tray_icon.activated.connect(self.tray_icon_activated)

            menu = QMenu(self)
            restore_action = menu.addAction("Restore")
            restore_action.triggered.connect(self.restore_window)
            exit_action = menu.addAction("Exit")
            exit_action.triggered.connect(self.close_app)

            self.tray_icon.setContextMenu(menu)
            self.tray_icon.show()
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
        message_box = QMessageBox(self)
        message_box.setWindowTitle(self.tr("Exit Application"))
        message_box.setText(self.tr("Are you sure you want to exit?"))
        message_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        
        yes_button = message_box.button(QMessageBox.Yes)
        yes_button.setText(self.tr("Yes"))
        no_button = message_box.button(QMessageBox.No)
        no_button.setText(self.tr("No"))
        
        reply = message_box.exec_()
        if reply == QMessageBox.Yes:
            logger.info("Application exited by user.")
            logger.info("")
            event.accept()
        else:
            event.ignore()

    def changeEvent(self, event):
        if event.type() == QEvent.WindowStateChange and self.isMinimized():
            self.hide()
            self.tray_icon.showMessage(
                "LiveRecBot",
                self.tr("The application is minimized to the system tray"),
                QSystemTrayIcon.Information,
                3000
            )
            logger.info("Window minimized to system tray.")
        super().changeEvent(event)

    def restore_window(self):
        self.showNormal()
        self.activateWindow()
        logger.info("Window restored from system tray.")

    def close_app(self):
        QApplication.quit()
        logger.info("Application closed.")
        logger.info("")