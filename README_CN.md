# LiveReCBot
#### Bilibili直播录播剪辑机器人

**********

[英文README | English](README.md)
<br>[日本語README | Japanese](README_JP.md)

## 介绍

**********

* 本工具主要实现录播自动压制弹幕，绘制弹幕密度曲线以及自动切片的功能。
* 本工具由我一人开发并用于我日常使用，主要用于CS2比赛录播切片。
* 本工具仍然__无法达到全自动化__，但是在制作切片时可以节省大量时间。
* 更多功能正在持续开发中，如果你对本工具的进展感兴趣，欢迎联系我。
* __*<u>[TOKO的小嘴巴](https://space.bilibili.com/202371545?spm_id_from=333.337.0.0)</u>*__是我的B站账号，最近上传的大部分视频都是基于这个项目的。
* 如果你想在B站上观看CS2赛事解说，欢迎灌注__*<u>[老懂哥0ff1c1aL](https://space.bilibili.com/475083446?spm_id_from=333.337.0.0)</u>*__喵。

## 依赖项

**********

* Python (__最好使用Python 3.6或更高版本，低版本未经测试__)
* numpy (新版Python应该默认安装了，但最好检查一下你的电脑是否有)
```
    pip install numpy
```
* <u>[FFmpeg](https://www.gyan.dev/ffmpeg/builds/)</u> ==(__确保FFmpeg在系统环境变量中，否则视频处理功能将无法使用__)==
*你也可以通过git安装ffmpeg*
```
    git clone https://git.ffmpeg.org/ffmpeg.git ffmpeg

    cd ffmpeg

    ./configure --enable-shared

    make

    sudo make install
```
* matplotlib
```
    pip install matplotlib
```
* PyQt5
```
    pip install PyQt5
```
* PyInstaller
```
    pip install pyinstaller
```
* flask
```
    pip install flask
```
* <u>[录播姬 (or BiliLiveRecorder)]( https://github.com/BililiveRecorder/BililiveRecorder/releases)</u>

## 使用方法

**********

### 直接安装

直接从Release下载exe文件，所有依赖都已经打包，无需额外安装其他库。

### 从源码安装

* 克隆本仓库
* 安装所有依赖
* 安装LiveRecBot
```
    pyinstaller --onefile --windowed --dist LiveRecBot -i LRB.ico LiveRecBot.py
```
* 进入LiveRecBot目录，运行__LiveRecBot.exe__
* 首次运行时会在该目录下新建默认文件夹以及app.log文件。
* 选择需要使用的功能。

## 功能

**********

### 手动压制弹幕
* 点击 __Select Video File__ 和 __Select Danmaku File__ 选择需要压制弹幕的视频。
* 点击 __Select Video Output Path__ 和 __Select Image Output Path__ 设置输出文件路径。
* 点击 __Process Video__ 开始处理。

### 生成弹幕密度曲线
* 点击 __Select Danmaku File__ 选择需要处理的弹幕文件。
* 点击 __Select Image Output Path__ 设置输出文件路径。
* 点击 __Process Danmaku Only__ 开始处理。

### 自动压制弹幕及切片
* 点击 __Select Video Output Path__ 和 __Select Image Output Path__ 设置输出文件路径。
* 在录播姬内设置Webhook接口：https://host:port//webhook （__默认port为5000__）
* 点击 __Select Base Path__ 选择录播姬自动录播存储地址。
* 在本工具文本框输入录播姬相同的Webhook地址。
* 点击 __Start Listening__ 开始监听录播姬的Webhook。点击关闭窗口，应用将在后台运行。

## 目录结构

**********

| 文件名 | 说明 |
| --- | --- |
| LiveRecBot.py | 主程序 |
| curve_plotter.py | 弹幕密度曲线绘制 <br>发送ffmpeg命令进行切片 |
| density_calculator.py | 弹幕密度计算 |
| flask_app.py | Flask服务端 |
| global_vars.py | 全局变量存储 |
| log_manager.py | 删除过期日志 |
| logger_config.py | 日志函数定义 |
| main_window.py | 主窗口GUI |
| video_processor.py | 压制弹幕 |
| webhook_listener.py | 监听Webhook <br>读取录播姬发送的json数据 |
| xml_parser.py | 解析xml弹幕 |
| LRB.ico | 可选的应用图标 |
| LRB.png | 可选的任务栏图标 |

你可以根据自己喜好变更图标。~~默认图标是AI生成的~~。
请注意==__使用.ico文件作为应用图标，使用.png文件作为任务栏图标__==。

## Tips

**********

* 自动切片功能并不是 __完全版__,它是根据弹幕密度 __超过均值1.5倍__ 的时间段，取中间一分钟及前后各两分钟共5分钟切片的。
* 设置的切片时间5分钟是根据CS2比赛单局时长及导播回放时间，加上一定容错时间设定的。
* 弹幕阈值（1.5倍均值）根据 __*<u>[老懂哥](https://live.bilibili.com/21674333?broadcast_type=0&is_room_feed=1&spm_id_from=333.999.to_liveroom.0.click&live_from=86002)</u>*__ 录播计算得出，可能不适用于其他主播或其他类型的直播录播。
* 目前你可以在代码中（__line 53, cureve_plotter.py__）修改阈值达到想要的效果。
* 可以根据生成的弹幕密度曲线调整阈值或者进行手动切片。
* 弹幕密度曲线图的 __dpi默认设置为300__，长录播曲线图请放大查看细节。
* 日志文件过期时间为 __30天__。如果程序在运行中将自动删除过期日志。如果程序未在运行，再次运行时将删除过期日志。

## 已知问题

**********

* __目前只支持单线程工作，同时只能处理一个视频和弹幕文件__。同一录播来源的压制和切片不受影响，请避免在自动处理过程中手动处理其他视频。__多视频并行处理功能正在开发中__。
* __弹幕格式仅支持xml格式__。（其实影响不大）录播姬自动存储弹幕格式为xml，无需转码可直接使用。
* __任务栏图标仅支持png格式__，请注意更换图标时格式问题。

### 更多信息请参考[CHANGELOG](CHANGELOG.md)。

## 参考

**********

* https://github.com/BililiveRecorder/BililiveRecorder
* https://rec.danmuji.org/reference/webhook/ 参考录播姬Webhook参数。
* https://www.cnblogs.com/ghgxj/p/14219075.html 参考xml弹幕参数。
