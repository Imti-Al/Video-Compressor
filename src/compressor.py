import os
import subprocess
from src.helpers import get_video_duration, calculate_bitrate, detect_gpu_encoders, get_audio_bitrate


def compress_video(input_path, output_path, target_size_mb, use_gpu=True, use_two_pass=True, codec="h265"):
    """
    Compress a video to a target size using FFMPEG.
    Supports GPU acceleration, two-pass encoding, and H.264 or H.265 selection.
    Includes audio compression by dynamically adjusting bitrate allocation.
    """
    ffmpeg_path = "ffmpeg_bin/ffmpeg.exe"

    # Get the duration of the video
    duration = get_video_duration(input_path)
    if duration == 0:
        print("Unable to fetch video duration. Exiting.")
        return

    # Get the audio bitrate
    audio_bitrate_kbps = get_audio_bitrate(input_path)
    if audio_bitrate_kbps is None:
        print("Unable to fetch audio bitrate. Defaulting to 128 kbps.")
        audio_bitrate_kbps = 128

    # Calculate video bitrate kbps
    video_bitrate_kbps = calculate_bitrate(target_size_mb - 0.5, duration, audio_bitrate_kbps=audio_bitrate_kbps)

    # Detect GPU encoders
    gpu_encoder = None
    if use_gpu:
        gpu_encoders = detect_gpu_encoders(ffmpeg_path)
        if codec == "h265" and "hevc_nvenc" in gpu_encoders:
            gpu_encoder = "hevc_nvenc"
        elif codec == "h264" and "h264_nvenc" in gpu_encoders:
            gpu_encoder = "h264_nvenc"
        elif codec == "h265" and "hevc_amf" in gpu_encoders:
            gpu_encoder = "hevc_amf"
        elif codec == "h264" and "h264_amf" in gpu_encoders:
            gpu_encoder = "h264_amf"
        elif codec == "h265" and "hevc_qsv" in gpu_encoders:
            gpu_encoder = "hevc_qsv"
        elif codec == "h264" and "h264_qsv" in gpu_encoders:
            gpu_encoder = "h264_qsv"

    # Choose encoder based on GPU availability or fallback to CPU
    if gpu_encoder:
        encoder = gpu_encoder
    elif codec == "h265":
        encoder = "libx265"  # CPU fallback for H.265
    else:
        encoder = "libx264"  # CPU fallback for H.264

    print(f"Selected encoder: {encoder}")

    # Construct FFMPEG command based on the encoder and vendor-specific settings
    if gpu_encoder == "hevc_nvenc":  # NVIDIA H.265
        # NVIDIA supports single-pass CRF encoding for H.265
        cmd = [
            ffmpeg_path,
            "-i", input_path,
            "-c:v", encoder,
            "-crf", "23",  # CRF for quality control
            "-b:v", f"{video_bitrate_kbps}k",  # Target bitrate
            "-maxrate", f"{int(video_bitrate_kbps * 1.5)}k",  # Set max bitrate
            "-bufsize", f"{int(video_bitrate_kbps * 2)}k",  # Set buffer size
            "-preset", "p6",  # High-quality preset for NVIDIA
            "-c:a", "aac",  # Audio codec
            "-b:a", f"{audio_bitrate_kbps}k",  # Target audio bitrate
            "-y",
            output_path,
        ]
    elif gpu_encoder == "hevc_amf":  # AMD H.265
        # AMD uses quality-based encoding with constant quality (CQ)
        cmd = [
            ffmpeg_path,
            "-i", input_path,
            "-c:v", encoder,
            "-cq", "23",  # Constant Quality for AMD
            "-b:v", f"{video_bitrate_kbps}k",  # Target bitrate for better control
            "-preset", "quality",  # AMD-specific preset
            "-c:a", "aac",
            "-b:a", f"{audio_bitrate_kbps}k",
            "-y",
            output_path,
        ]
    elif gpu_encoder == "hevc_qsv":  # Intel H.265
        if use_two_pass:
            # Intel supports two-pass encoding for better quality
            cmd_pass_1 = [
                ffmpeg_path,
                "-i", input_path,
                "-b:v", f"{video_bitrate_kbps}k",
                "-c:v", encoder,
                "-preset", "balanced",  # Intel-specific preset
                "-pass", "1",
                "-an",  # Disable audio in first pass
                "-f", "null",  # Ensures not saved as file
                "NUL" if os.name == "nt" else "/dev/null",
            ]

            cmd_pass_2 = [
                ffmpeg_path,
                "-i", input_path,
                "-b:v", f"{video_bitrate_kbps}k",
                "-c:v", encoder,
                "-preset", "balanced",
                "-pass", "2",
                "-c:a", "aac",
                "-b:a", f"{audio_bitrate_kbps}k",
                "-y",
                output_path,
            ]

            try:
                print(f"Running first pass: {' '.join(cmd_pass_1)}")
                subprocess.run(cmd_pass_1, check=True)

                print(f"Running second pass: {' '.join(cmd_pass_2)}")
                subprocess.run(cmd_pass_2, check=True)

                print(f"Compressed {input_path} to {output_path} successfully with two-pass encoding.")
            except subprocess.CalledProcessError as e:
                print(f"Error during two-pass compression: {e}")
            return
    elif use_two_pass:
        # Two-pass encoding for CPU or fallback scenarios
        cmd_pass_1 = [
            ffmpeg_path,
            "-i", input_path,
            "-b:v", f"{video_bitrate_kbps}k",
            "-c:v", encoder,
            "-preset", "medium",
            "-pass", "1",
            "-an",
            "-f", "null",
            "NUL" if os.name == "nt" else "/dev/null",
        ]

        cmd_pass_2 = [
            ffmpeg_path,
            "-i", input_path,
            "-b:v", f"{video_bitrate_kbps}k",
            "-c:v", encoder,
            "-preset", "medium",
            "-pass", "2",
            "-c:a", "aac",
            "-b:a", f"{audio_bitrate_kbps}k",
            "-y",
            output_path,
        ]

        try:
            print(f"Running first pass: {' '.join(cmd_pass_1)}")
            subprocess.run(cmd_pass_1, check=True)

            print(f"Running second pass: {' '.join(cmd_pass_2)}")
            subprocess.run(cmd_pass_2, check=True)

            print(f"Compressed {input_path} to {output_path} successfully with two-pass encoding.")
        except subprocess.CalledProcessError as e:
            print(f"Error during two-pass compression: {e}")
        return  # Exit after two-pass encoding
    else:
        # Single-pass encoding for fallback scenarios
        cmd = [
            ffmpeg_path,
            "-i", input_path,
            "-b:v", f"{video_bitrate_kbps}k",
            "-c:v", encoder,
            "-preset", "medium",
            "-c:a", "aac",
            "-b:a", f"{audio_bitrate_kbps}k",
            "-y",
            output_path,
        ]

    try:
        print(f"Running command: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)
        print(f"Compressed {input_path} to {output_path} successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error during compression: {e}")
