from flask import Flask, request
import os
import global_vars
import logging
from video_processor import process_video
from datetime import datetime

app = Flask(__name__)

logging.basicConfig(filename='webhook_listener.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Create output directory
os.makedirs(global_vars.OUTPUT_VIDEO_DIR, exist_ok=True)
os.makedirs(global_vars.OUTPUT_IMAGE_DIR, exist_ok=True)
os.makedirs(global_vars.OUTPUT_CLIPS_DIR, exist_ok=True)

def is_video_processed(video_file):
    if not os.path.exists(global_vars.PROCESSED_VIDEOS_FILE):
        return False
    with open(global_vars.PROCESSED_VIDEOS_FILE, 'r') as f:
        processed_videos = f.read().splitlines()
    return video_file in processed_videos

def mark_video_processed(video_file):
    with open(global_vars.PROCESSED_VIDEOS_FILE, 'a') as f:
        f.write(video_file + '\n')

def get_daily_video_count(date_str):
    """Access processed video amount"""
    count = 0
    for filename in os.listdir(global_vars.OUTPUT_VIDEO_DIR):
        if date_str in filename:
            count += 1
    return count

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json()
        video_file = data.get('file path')
        danmaku_file = data.get('danmu path')
        if not video_file or not danmaku_file:
            logging.error("Missing video_file or danmaku_file in webhook data")
            return "Missing video_file or danmaku_file", 204

        if is_video_processed(video_file):
            logging.info(f"Video {video_file} has already been processed, skipping.")
            return "Video already processed", 200

        # Access date of recording
        now = datetime.now()
        date_str = now.strftime("%Y%m%d")
        # Access video number
        video_count = get_daily_video_count(date_str) + 1

        # Generate full video name
        output_video_name = f"{date_str}_{video_count:03d}"
        # Generate output path
        output_video = os.path.join(global_vars.OUTPUT_VIDEO_DIR, f"{output_video_name}.mp4")
        image_path = os.path.join(global_vars.OUTPUT_IMAGE_DIR, f"{output_video_name}_danmaku_density.png")
        output_clips_sub_dir = os.path.join(global_vars.OUTPUT_CLIPS_DIR, output_video_name)
        os.makedirs(output_clips_sub_dir, exist_ok=True)

        process_video(video_file, danmaku_file, output_video, image_path, output_clips_sub_dir)
        mark_video_processed(video_file)
        return "Video processing completed", 200
    except Exception as e:
        logging.error(f"Error handling webhook: {e}")
        return f"Error handling webhook: {e}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
    