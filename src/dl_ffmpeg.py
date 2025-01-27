import os
import requests
import zipfile
import shutil

FFMPEG_URL = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
FFMPEG_DIR = "ffmpeg_bin"  # Directory to store FFMPEG binaries

def download_ffmpeg():
    if not os.path.exists(FFMPEG_DIR):
        os.makedirs(FFMPEG_DIR)

    zip_path = os.path.join(FFMPEG_DIR, "ffmpeg.zip")

    # Download FFMPEG zip
    print("Downloading FFMPEG...")
    with requests.get(FFMPEG_URL, stream=True) as response:
        response.raise_for_status()
        with open(zip_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

    # Extract the zip file
    print("Extracting FFMPEG...")
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(FFMPEG_DIR)

    # Move the binaries to the main folder
    extracted_folder = os.path.join(FFMPEG_DIR, os.listdir(FFMPEG_DIR)[0], "bin")
    for filename in os.listdir(extracted_folder):
        shutil.move(os.path.join(extracted_folder, filename), FFMPEG_DIR)

    # Cleanup
    shutil.rmtree(os.path.join(FFMPEG_DIR, os.listdir(FFMPEG_DIR)[0]))
    os.remove(zip_path)

    print(f"FFMPEG installed in {FFMPEG_DIR}")

if __name__ == "__main__":
    download_ffmpeg()
