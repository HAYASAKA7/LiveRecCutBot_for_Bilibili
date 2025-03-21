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