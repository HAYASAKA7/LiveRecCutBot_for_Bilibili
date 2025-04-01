# LiveReCBot
#### Bilibiliライブ用のライブ録画カットボット

**********

[中文README | Chinese](README_CN.md)
<br>[英語README | English](README.md)

## 紹介

**********

* このプロジェクトは、弾幕を自動的に圧縮し、弾幕密度曲線を生成し、ライブ録画からホットクリップを処理することを目的としています。
* これは一人で行っているプロジェクトで、主にCS2ゲームの解説クリップのために自分用に作成しました。
* まだ__完全な自動化のレベルには達していません__が、クリップを作成する際に多くの時間を節約できます。
* 今後も更新を続け、さらに多くの機能を追加する予定です。
* 私の進行状況に興味がある場合は、気軽に連絡してください。
* __*<u>[TOKO的小嘴巴](https://space.bilibili.com/202371545?spm_id_from=333.337.0.0)</u>*__ は私のBilibiliアカウントで、最近アップロードされたビデオのほとんどはこのプロジェクトに基づいています。
* CS2ゲームの競技に興味があり、Bilibiliで中国語の解説者を探している場合は、__*<u>[老懂哥0ff1c1aL](https://space.bilibili.com/475083446?spm_id_from=333.337.0.0)</u>*__ を購読してください。彼は著作権侵害がない限り、すべてのゲームに解説を行います。昼夜を問わず。

## 必要条件

**********

* Python (__Python 3.6以上を使用することをお勧めします__、低いバージョンはテストされていません)
* numpy (新しいPythonバージョンにはデフォルトで含まれているはずですが、コンピュータにインストールされているか確認してください)
```
    pip install numpy
```
* <u>[FFmpeg](https://www.gyan.dev/ffmpeg/builds/)</u> ==(__FFmpegがシステム環境変数にあることを確認してください。そうでないとビデオ処理機能が機能しません__)==
*gitを使用してffmpegをインストールすることもできます*
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
* <u>[Danmuji (またはBiliLiveRecorder)]( https://github.com/BililiveRecorder/BililiveRecorder/releases)</u>

## 使用方法

**********

### 直接インストール

リリースから実行可能ファイルを直接ダウンロードした場合、何もインストールせずに実行できます。

### ソースコードからインストール

* リポジトリをクローン
* すべての必要条件をインストール
* LiveRecBotをインストール
```
    pyinstaller --onefile --windowed --add-data --dist LiveRecBot -i LRB.ico LiveRecBot.py
```
* LiveRecBotディレクトリに移動し、__LiveRecBot.exe__ を実行
* 実行すると、デフォルトのファイルディレクトリが実行可能ファイルと同じディレクトリに作成されます。
* 使用する機能を選択

### 機能

**********

#### .xml弾幕と.flvビデオファイルを圧縮
* __Select Video File__ と __Select Danmaku File__ をクリックして、処理するファイルを選択します。
* __Select Video Output Path__ と __Select Image Output Path__ をクリックして、出力ファイルのパスを設定します。
* __Process Video__ をクリックして処理を開始します。

#### 弾幕密度曲線画像を生成
* __Select Danmaku File__ をクリックして、処理する弾幕ファイルを選択します。
* __Select Image Output Path__ をクリックして、出力ファイルのパスを設定します。
* __Process Danmaku Only__ をクリックして処理を開始します。

#### 自動圧縮とホットクリップの生成
* __Select Video Output Path__ と __Select Image Output Path__ をクリックして、出力ファイルのパスを設定します。
* Danmuji内でWebhookインターフェースを設定: https://host:port//webhook (__デフォルトのポートは5000__)
* __Select Base Path__ をクリックして、Danmujiの自動録画保存先を選択します。
* WebhookテキストボックスにWebhookインターフェースアドレスを入力します。
* __Start Listening__ をクリックします。ウィンドウを閉じてもプログラムはバックグラウンドで実行され続けます。

## ファイルディレクトリ

**********

| ファイル名 | 説明 |
| --------- | ----------- |
| LiveRecBot.py | メインプログラム |
| curve_plotter.py | 弾幕密度曲線を生成 <br>ffmpegコマンドを送信してクリップを処理 |
| density_calculator.py | 弾幕密度を計算 |
| flask_app.py | Flask webhookサーバー |
| global_vars.py | グローバル変数 |
| log_manager.py | 期限切れのログファイルを削除 |
| logger_config.py | ロガー設定 |
| main_window.py | メインウィンドウGUI |
| video_processor.py | 弾幕とビデオファイルを圧縮 |
| webhook_listener.py | Webhookをリッスン <br>BililiveRecorderからjsonを読み取る |
| xml_parser.py | 弾幕xmlファイルを解析 |
| LRB.ico | 可能なアプリケーションアイコン |
| LRB.png | 可能なトレイアイコン |

アイコンは好きなように変更できます。~~デフォルトのアイコンはAIによって生成されました~~。
 ただし、==__アプリケーションアイコンには.icoファイルを、トレイアイコンには.pngファイルを使用してください__==。

 ## Tips

**********

* 自動クリップ生成は __まだ完全な機能ではありません__、弾幕密度が __平均の1.5倍__ 高い時間の周りに5分間のクリップを提供します。
* 時間の長さは__CS2ゲームのラウンドごとの時間と弾幕の遅延__のために5分に設定されています。
* 密度のしきい値は、__*<u>[老懂哥](https://live.bilibili.com/21674333?broadcast_type=0&is_room_feed=1&spm_id_from=333.999.to_liveroom.0.click&live_from=86002)</u>*__ のライブ録画に基づいて実験的に設定されており、あなたのライブ録画には正確でないかもしれません。
* コード内のしきい値を変更することができます (__curve_plotter.pyの53行目__)。相対的な機能は開発中です。
* 処理は密度曲線画像を生成するため、しきい値を調整したりビデオをカットしたりするために使用できます。
* 密度曲線画像は __300 dpi__ で保存されるように設定されているため、ズームインしてカーブの詳細を見ることができます。
* プログラムが実行されている場合、ログファイルは __30日ごとに__ 削除されます。プログラムを閉じた場合、ログファイルは削除されません。しかし、LRBを再起動すると、期限切れのログファイルが削除されます。

## 既知の問題

**********

* __このバージョンは一度に1つのビデオファイルと1つの弾幕ファイルのみをサポートします__。ストリーミングが実行されているときに手動で処理しないでください。そうしないと、自動カット機能が動作しません。__複数ファイルのサポートは開発中です__。
* __このバージョンは.xml弾幕ファイルのみをサポートします__。多くの人がビデオ編集で.ass弾幕ファイルを使用しますが、BililiveRecorderは自動的に.xml弾幕ファイルを保存するため、直接使用できます。トランスコードする必要はありません。
* __トレイアイコンは.pngファイルのみをサポートします__。実際のところ、.icoファイルが機能しない理由はわかりません。~~多分PythonはC++とは違うのでしょう。~~

### 詳細は[CHANGELOG](CHANGELOG.md)をご覧ください

## 参考文献

**********

* https://github.com/BililiveRecorder/BililiveRecorder
* https://rec.danmuji.org/reference/webhook/ Webhookパラメータの参考として使用
* https://www.cnblogs.com/ghgxj/p/14219075.html xml弾幕パラメータの参考として使用