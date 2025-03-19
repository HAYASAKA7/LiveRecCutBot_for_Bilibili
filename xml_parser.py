import xml.etree.ElementTree as ET

def parse_xml(xml_file):
    """
    Parse the XML file to extract danmaku timestamps and calculate video duration.
    :param xml_file: Path to the XML file.
    :return: A tuple containing a list of timestamps and the video duration.
    """
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        timestamps = []
        for danmaku in root.findall('d'):
            p = danmaku.get('p')
            if p:
                timestamp = float(p.split(',')[0]) / 60
                timestamps.append(timestamp)
        video_duration = (timestamps[-1] + 10 / 60) if timestamps else 0
        return timestamps, video_duration
    except FileNotFoundError:
        print("Error: File not found!")
    except Exception as e:
        print(f"Error: An unknown error occurred: {e}")
    return [], 0
    