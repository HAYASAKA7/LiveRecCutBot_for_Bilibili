import subprocess
import os
import logging
from xml_parser import parse_xml
from density_calculator import calculate_density, calculate_minute_density
from curve_plotter import plot_density_curve

logging.basicConfig(filename='video_processing.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def process_video(video_file, danmaku_file, output_video, image_path, output_clips_dir):
    try:
        # Process video and danmaku
        logging.info(f"Starting video and danmaku muxing for {video_file}")
        subprocess.run(['ffmpeg', '-i', video_file, '-i', danmaku_file, '-c', 'copy', output_video], check=True)
        logging.info(f"Video and danmaku muxing completed for {video_file}, output: {output_video}")

        # Danmaku analyzation and video clipping
        timestamps, video_duration = parse_xml(danmaku_file)
        bins, density = calculate_density(timestamps)
        minute_bins, minute_density = calculate_minute_density(timestamps, video_duration)
        plot_density_curve(bins, density, minute_bins, minute_density, image_path, video_duration, output_video, output_clips_dir)
        logging.info(f"Danmaku analysis and video clipping completed for {video_file}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error processing video {video_file}: {e}")
    except Exception as e:
        logging.error(f"Unexpected error processing video {video_file}: {e}")
    