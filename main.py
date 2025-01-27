from src.compressor import compress_video

if __name__ == "__main__":
    # Input and output video paths
    input_video = "C:/Users/imti/Documents/Programming/Compressor/clips/ezgame.mp4"  # Replace with input video file path
    output_video = "C:/Users/imti/Documents/Programming/Compressor/clips/ezgametest.mp4"  # *Replace or auto-generate the output filename

    target_size = 10  # Target size in MB

    # Compression options
    use_gpu = True  # Enable GPU encoding if available
    use_h265 = True  # Use H.265 encoding if available (H.264 will be used if False or unsupported)
    use_two_pass = True  # Enable two-pass encoding where supported

    # Select codec based on user preference and workflow
    codec = "h265" if use_h265 else "h264"

    compress_video(input_video, output_video, target_size, use_gpu=use_gpu, use_two_pass=use_two_pass, codec=codec)
