from flask import Flask, request
import os
import global_vars
import logging
from video_processor import process_video
from datetime import datetime

app = Flask(__name__)

processed_event_ids = set()

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
        EventId = data.get('EventId')
        EventType = data.get('EventType')
        EventData = data.get('EventData')
        relative_path = EventData.get('RelativePath')

        # Check if the EventId has already been processed
        if EventId in processed_event_ids:
            logging.info(f"Event {EventId} has already been processed, ignoring.")
            return "Event already processed", 200

        if not relative_path:
            logging.error("Missing RelativePath in webhook data")
            return "Missing RelativePath", 204
        
        if EventType == 'FileClosed':
            if relative_path.endswith('.flv'):
                video_file = relative_path
                danmaku_file = None
            elif relative_path.endswith('.xml'):
                video_file = None
                danmaku_file = relative_path
            else:
                logging.error(f"Unsupported file type: {relative_path}")
                return "Unsupported file type", 204

            # Check if we have both video and danmaku files
            if hasattr(webhook, 'video_file') and hasattr(webhook, 'danmaku_file'):
                video_file = webhook.video_file
                danmaku_file = webhook.danmaku_file
                delattr(webhook, 'video_file')
                delattr(webhook, 'danmaku_file')

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

                processed_event_ids.add(EventId)
                return "Clips processed", 200
            elif video_file:
                webhook.video_file = video_file
                return "Waiting for danmaku file", 200
            elif danmaku_file:
                webhook.danmaku_file = danmaku_file
                return "Waiting for video file", 200
        else:
            logging.info(f"Received event of type {EventType}, ignoring.")
            return "Event received and ignored", 200
        
    except Exception as e:
        logging.error(f"Error handling webhook: {e}")
        return f"Error handling webhook: {e}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
    