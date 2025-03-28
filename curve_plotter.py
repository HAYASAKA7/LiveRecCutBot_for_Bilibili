import matplotlib.pyplot as plt
import numpy as np
import os
import subprocess
from logger_config import setup_logger

logger = setup_logger()

# Set matplotlib to support Chinese
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False


def plot_density_curve(bins, density, minute_bins, minute_density, save_path, video_duration, input_video=None, output_dir=None):
    """
    Plot the danmaku density curve and save it as an image.
    Additionally, output a .txt file listing the time segments of high-density regions.
    :param bins: Bin edges for the density calculation.
    :param density: Density values.
    :param minute_bins: Bin edges for the minute density calculation.
    :param minute_density: Minute density values.
    :param save_path: Path to save the image.
    :param video_duration: Duration of the video.
    :param input_video: Path to the input video.
    :param output_dir: Directory to save the output videos.
    """
    if len(bins) == 0 or len(density) == 0:
        return
    fig_width = max(6, video_duration * 2)
    fig_height = max(4, max(density) / 10 if len(density) > 0 else 4)
    plt.figure(figsize=(fig_width, fig_height))

    plt.plot(bins, density)
    plt.xlabel('Time (Hours:Minutes)')
    plt.ylabel('Danmaku Density')
    plt.title('Danmaku Density Curve')

    plt.xlim(0, video_duration)
    plt.ylim(0, max(density) * 1.1 if len(density) > 0 else 1)

    # Generate hour:minute format tick labels
    tick_locations = np.arange(0, video_duration + 1, 1)
    tick_labels = [f"{int(t // 60):02d}:{int(t % 60):02d}" for t in tick_locations]
    plt.xticks(tick_locations, tick_labels)

    if len(density) > 0:
        average_density = np.mean(density)
        plt.axhline(y=average_density, color='r', linestyle='--', label=f'Average Density: {average_density:.2f}')
        plt.legend()

    if len(density) >= 5:
        top_5_indices = np.argsort(density)[-5:][::-1]
        for index in top_5_indices:
            plt.axvline(x=bins[index], color='r', linestyle='-', linewidth=2)

    if len(minute_density) > 0:
        threshold = 1.5 * np.mean(minute_density)
        high_density_indices = np.where(minute_density > threshold)[0]
        segments = []
        start_index = None

        txt_output_path = save_path.replace('.png', '_segments.txt')
        with open(txt_output_path, 'w') as txt_file:
            txt_file.write(f"High-density segments (Minutes):\n")
            txt_file.write("=" * 40 + "\n")

            for i in range(len(high_density_indices)):
                if start_index is None:
                    start_index = high_density_indices[i]
                if i == len(high_density_indices) - 1 or high_density_indices[i + 1] != high_density_indices[i] + 1:
                    end_index = high_density_indices[i]
                    start_time = minute_bins[start_index]
                    end_time = minute_bins[end_index] + 1
                    segments.append((start_time, end_time))
                    plt.axvspan(start_time, end_time, color='y', alpha=0.3)
                    plt.axvline(x=start_time, color='m', linestyle='--', linewidth=1)
                    plt.axvline(x=end_time, color='m', linestyle='--', linewidth=1)
                    txt_file.write(f"{int(start_time // 60):02d}:{int(start_time % 60):02d} - "
                                   f"{int(end_time // 60):02d}:{int(end_time % 60):02d}\n")
                    start_index = None

        if input_video and output_dir:
            os.makedirs(output_dir, exist_ok=True)
            # Get the name of the muxed video
            output_video_name = os.path.basename(input_video).replace('.mp4', '')
            for i, (start_time, end_time) in enumerate(segments, start=1):
                clip_start = max(0, start_time - 2)
                clip_end = min(video_duration, end_time + 2)
                # Generate the file name for the clipped video segment
                output_file = os.path.join(output_dir, f"{output_video_name}_clip{i:03d}.mp4")
                try:
                    subprocess.run([
                        'ffmpeg', '-y', '-i', input_video,
                        '-ss', str(clip_start * 60),
                        '-to', str(clip_end * 60),
                        '-c', 'copy', output_file
                    ], check=True)
                    logger.info(f"Clipped video saved to {output_file}")
                except subprocess.CalledProcessError as e:
                    logger.info(f"Error clipping video: {e}")

    try:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=300)
        plt.close()
    except OSError as e:
        logger.info(f"Error saving file: {e}")
    