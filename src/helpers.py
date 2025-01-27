import subprocess
import json

def get_video_duration(input_path):
    ffprobe_path = "C:/Users/imti/Documents/Programming/Compressor/ffmpeg_bin/ffprobe.exe"
    cmd = [
        ffprobe_path,
        "-v", "error", # Supresses unnecessary logs 
        "-show_entries", "format=duration", # Fetches only duration field
        "-of", "json", # Output as JSON, ez parsing
        input_path
    ]
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, text=True)
        # Parse JSON output, get duration
        duration = json.loads(result.stdout)["format"]["duration"]
        return float(duration)
    except Exception as e:
        print(f"Error fetching video duration: {e}")
        return 0
    

def calculate_bitrate(target_size_mb, duration, audio_bitrate_kbps=128):
    """
    target video bitrate for a given file size and duration.
    """
    total_bitrate = (target_size_mb * 8192) / duration
    video_bitrate = total_bitrate - audio_bitrate_kbps # Subtract space needed for audio
    return max(1, int(video_bitrate)) # Ensures bitrate is positive for FFMPEG to work