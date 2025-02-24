import subprocess
import json
import os


def detect_gpu_encoders(ffmpeg_path):
    """
    Detect available GPU encoders from FFMPEG.
    :return: List of supported GPU encoders.
    """
    try:
        cmd = [ffmpeg_path, "-hide_banner", "-encoders"]
        output = subprocess.check_output(cmd, universal_newlines=True)
        encoders = []
        if "h264_nvenc" in output:
            encoders.append("h264_nvenc")
        if "hevc_nvenc" in output:
            encoders.append("hevc_nvenc")
        if "h264_amf" in output:
            encoders.append("h264_amf")
        if "hevc_amf" in output:
            encoders.append("hevc_amf")
        if "h264_qsv" in output:
            encoders.append("h264_qsv")
        if "hevc_qsv" in output:
            encoders.append("hevc_qsv")
        return encoders
    except subprocess.CalledProcessError:
        return []


def get_video_duration(input_path):
    ffprobe_path = "C:/Users/imti/Documents/Programming/Compressor/ffmpeg_bin/ffprobe.exe"
    cmd = [
        ffprobe_path,
        "-v", "error",  # Suppresses unnecessary logs 
        "-show_entries", "format=duration",  # Fetches only duration field
        "-of", "json",  # Output as JSON, easy parsing
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
    video_bitrate = total_bitrate - audio_bitrate_kbps  # Subtract space needed for audio
    return max(1, int(video_bitrate))  # Ensures bitrate is positive for FFMPEG to work


def get_audio_bitrate(input_path):
    """
    Get the audio bitrate from a video file using ffprobe.
    :param input_path: Path to the video file.
    :return: Audio bitrate in kbps or None if unavailable.
    """
    ffprobe_path = "C:/Users/imti/Documents/Programming/Compressor/ffmpeg_bin/ffprobe.exe"
    cmd = [
        ffprobe_path,
        "-v", "error",
        "-select_streams", "a:0",  # Select the first audio stream
        "-show_entries", "stream=bit_rate",
        "-of", "json",
        input_path
    ]
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, text=True)
        audio_info = json.loads(result.stdout)
        bit_rate = audio_info["streams"][0]["bit_rate"]
        return round(float(bit_rate) / 1000) if bit_rate else 0  # Convert to kbps
    except Exception as e:
        print(f"Error fetching audio bitrate: {e}")
        return None
