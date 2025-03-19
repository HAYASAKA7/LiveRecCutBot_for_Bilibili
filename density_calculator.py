import numpy as np

def calculate_density(timestamps, bin_size=1/60):
    """
    Calculate the danmaku density based on timestamps.
    :param timestamps: List of danmaku timestamps.
    :param bin_size: Size of each time bin.
    :return: A tuple containing bin edges and density values.
    """
    if not timestamps:
        return [], []
    min_time = min(timestamps)
    max_time = max(timestamps)
    bins = np.arange(min_time, max_time + bin_size, bin_size)
    density, _ = np.histogram(timestamps, bins=bins)
    return bins[:-1], density

def calculate_minute_density(timestamps, video_duration):
    """
    Calculate the danmaku density per minute.
    :param timestamps: List of danmaku timestamps.
    :param video_duration: Duration of the video.
    :return: A tuple containing bin edges and density values.
    """
    if not timestamps:
        return [], []
    num_minutes = int(np.ceil(video_duration))
    bins = np.arange(0, num_minutes + 1)
    density, _ = np.histogram(timestamps, bins=bins)
    return bins[:-1], density
    