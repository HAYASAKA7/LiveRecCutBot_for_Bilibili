import os

# Processed events and videos check
PROCESSED_VIDEOS_FILE = 'processed_videos.txt'
PROCESSED_EVENTS_FILE = 'processed_events.txt'

# Default save directories for output files
DEFAULT_OUTPUT_VIDEO_DIR = 'output_videos'
DEFAULT_OUTPUT_IMAGE_DIR = 'output_images'
DEFAULT_OUTPUT_CLIPS_DIR = 'output_clips'

# Initialize output directories
OUTPUT_VIDEO_DIR = DEFAULT_OUTPUT_VIDEO_DIR
OUTPUT_IMAGE_DIR = DEFAULT_OUTPUT_IMAGE_DIR
OUTPUT_CLIPS_DIR = DEFAULT_OUTPUT_CLIPS_DIR

# Create default output directories if they don't exist
os.makedirs(OUTPUT_VIDEO_DIR, exist_ok=True)
os.makedirs(OUTPUT_IMAGE_DIR, exist_ok=True)
os.makedirs(OUTPUT_CLIPS_DIR, exist_ok=True)
    