import os
import logging
from flask import Flask, request
from xml_parser import parse_xml
from density_calculator import calculate_density, calculate_minute_density
from curve_plotter import plot_density_curve
import global_vars
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

app = Flask(__name__)


def is_event_processed(event_id):
    try:
        if not os.path.exists(global_vars.PROCESSED_EVENTS_FILE):
            return False
        with open(global_vars.PROCESSED_EVENTS_FILE, 'r') as f:
            processed_events = f.read().splitlines()
        return event_id in processed_events
    except Exception as e:
        logging.error(f"Error checking if event is processed: {e}")
        return False

def mark_event_processed(event_id):
    try:
        with open(global_vars.PROCESSED_EVENTS_FILE, 'a') as f:
            f.write(event_id + '\n')
        logging.info(f"Marked event {event_id} as processed.")
    except Exception as e:
        logging.error(f"Error marking event as processed: {e}")


def is_video_processed(video_file):
    try:
        if not os.path.exists(global_vars.PROCESSED_VIDEOS_FILE):
            return False
        with open(global_vars.PROCESSED_VIDEOS_FILE, 'r') as f:
            processed_videos = f.read().splitlines()
        return video_file in processed_videos
    except Exception as e:
        logging.error(f"Error checking if video is processed: {e}")
        return False


def mark_video_processed(video_file):
    try:
        with open(global_vars.PROCESSED_VIDEOS_FILE, 'a') as f:
            f.write(video_file + '\n')
        logging.info(f"Marked video {video_file} as processed.")
    except Exception as e:
        logging.error(f"Error marking video as processed: {e}")


def get_daily_video_count(date_str):
    """Get the number of videos processed on the current day"""
    try:
        count = 0
        for filename in os.listdir(global_vars.OUTPUT_VIDEO_DIR):
            if date_str in filename:
                count += 1
        return count
    except Exception as e:
        logging.error(f"Error getting daily video count: {e}")
        return 0


@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json()
        event_type = data.get('EventType')
        event_id = data.get('EventId')
        event_data = data.get('EventData')
        if event_type != 'FileClosed':
            logging.info(f"Received event of type {event_type}, ignoring.")
            return "Event received and ignored", 200

        relative_path = event_data.get('RelativePath')
        if not relative_path:
            logging.warning("Missing RelativePath in webhook data")
            return "Missing RelativePath", 204

        if relative_path.endswith('.flv'):
            video_file = relative_path
            danmaku_file = None
        elif relative_path.endswith('.xml'):
            video_file = None
            danmaku_file = relative_path
        else:
            logging.warning(f"Unsupported file type: {relative_path}")
            return "Unsupported file type", 204

        # Check if we have both video and danmaku files
        if hasattr(webhook, 'video_file') and hasattr(webhook, 'danmaku_file'):
            video_file = webhook.video_file
            danmaku_file = webhook.danmaku_file
            delattr(webhook, 'video_file')
            delattr(webhook, 'danmaku_file')
        elif video_file:
            webhook.video_file = video_file
            return "Waiting for danmaku file", 200
        elif danmaku_file:
            webhook.danmaku_file = danmaku_file
            return "Waiting for video file", 200
        else:
            return "Incomplete data", 204

        if is_video_processed(video_file):
            logging.info(f"Video {video_file} has already been processed, skipping.")
            return "Video already processed", 200

        # Get the recording completion date
        from datetime import datetime
        now = datetime.now()
        date_str = now.strftime("%Y%m%d")
        # Get the number of videos processed on the current day
        video_count = get_daily_video_count(date_str) + 1

        # Generate the name of the muxed video
        output_video_name = f"{date_str}_{video_count:03d}"
        # Generate the path for the output video
        output_video = os.path.join(global_vars.OUTPUT_VIDEO_DIR, f"{output_video_name}.mp4")
        # Generate the path for the output image
        image_path = os.path.join(global_vars.OUTPUT_IMAGE_DIR, f"{output_video_name}_danmaku_density.png")
        # Generate the directory for the output video clips
        output_clips_sub_dir = os.path.join(global_vars.OUTPUT_CLIPS_DIR, output_video_name)
        os.makedirs(output_clips_sub_dir, exist_ok=True)

        timestamps, video_duration = parse_xml(danmaku_file)
        bins, density = calculate_density(timestamps)
        minute_bins, minute_density = calculate_minute_density(timestamps, video_duration)
        plot_density_curve(bins, density, minute_bins, minute_density, image_path, video_duration, output_video,
                           output_clips_sub_dir)
        mark_video_processed(video_file)
        mark_event_processed(event_id)
        logging.info(f"Video processing completed for {video_file}")
        return "Video processing completed", 200
    except Exception as e:
        logging.error(f"Error handling webhook: {e}")
        return f"Error handling webhook: {e}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)