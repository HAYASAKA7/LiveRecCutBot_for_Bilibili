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
- Fix the bug that log file will always shoe 'Failed to show system tray icon' even if the system tray icon is shown successfully.