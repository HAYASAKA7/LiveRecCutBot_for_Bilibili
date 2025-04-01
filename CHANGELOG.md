# LRB Change Log

**********

## Version 1.x.x

**********

### 1.0.0 (2025-3-18)
- Initial release

### 1.0.1 (2025-3-19)
- Change the parameters' name in 'webhook_listener.py' to match the BiliLiveRecorder's interface.
- Add log function to 'curve_plotter.py'.

### 1.0.2 (2025-3-20)
- Fix the bug that log info will show 4 times.(Add 'logger.propagate = False' in 'logger_config.py')

### 1.0.3 (2025-3-21)
- Fix the bug that log file will always show 'Failed to show system tray icon' even if the system tray icon is shown successfully.

### 1.0.4 (2025-3-21)
- Fix window icon not showing bug.

### 1.0.5 (2025-3-21)
- Add multi-language support.(English, Japanese, Chinese)
- Multi-language still in progress. Now need to mannually drag 'translations' folder to the same directory as the executable.
- Allow user to change default language by clicking Switching Language button.

### 1.0.6 (2025-3-28)
- Add txt output to 'curve_plotter.py'.
- This helps to cut videos manually. No need to see the curve, but only by checking the time in the txt file.

### 1.0.7 (2025-3-28)
- Replace txt file by pdf file to avoid misoperation.
- Highlight the 5 highest danmaku density time points in the pdf file.

### 1.0.8 (2025-3-28)
- Add encoder support for Intel CPU/GPU, AMD CPU/GPU, NVIDIA GPU.
- Add tab switch for different settings.

### 1.0.9 (2025-4-1)
- Add log folders to save log files generated in different days.
