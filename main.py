import os
from src.compressor import compress_video

def generate_output_filename(input_video, target_size, custom_name=None, output_dir=None):
    """
    Generates an output filename based on user input or defaults to original filename with compression details.
    Preserves the original file extension.
    """
    filename, ext = os.path.splitext(os.path.basename(input_video))

    # Ensure custom name has an extension (preserve original extension)
    if custom_name and not os.path.splitext(custom_name)[1]:
        custom_name += ext  

    # Use custom name or auto-generate filename
    output_filename = custom_name if custom_name else f"{filename}_{target_size}MB_compressed{ext}"

    # Use selected output directory or default to input file's directory
    output_folder = output_dir or os.path.dirname(input_video)

    return os.path.join(output_folder, output_filename)

def validate_input_file(input_video):
    """ Validates the input file exists before compressing. """
    if not os.path.exists(input_video):
        print(f"Error: Input video '{input_video}' not found.")
        exit(1)

if __name__ == "__main__":
    # Video file selected via GUI (drag-and-drop or browse)
    input_video = "C:/Users/imti/Documents/Programming/Compressor/clips/ezgame.mp4"  # Example, replace via GUI
    
    validate_input_file(input_video)

    # Optional User-selected output folder (None = same folder as input)
    custom_output_folder = None  

    # Optional User-defined output filename (None = auto-generated)
    custom_output_name = None  

    # Compression parameters
    target_size = 10  # Target size in MB
    use_gpu = True  # Enable GPU encoding if available
    use_h265 = True  # Use H.265 encoding if available (H.264 will be used if False or unsupported)
    use_two_pass = True  # Enable two-pass encoding where supported

    # Select codec based on user preference
    codec = "h265" if use_h265 else "h264"  

    # Convert empty values to None to prevent unintended behavior
    custom_output_folder = custom_output_folder or None
    custom_output_name = custom_output_name or None

    # Generate output filename
    output_video = generate_output_filename(input_video, target_size, custom_output_name, custom_output_folder)

    # Print selected options for confirmation
    print(f"Compressing: {input_video} → {output_video}")
    print(f"Input Video: {input_video}")
    print(f"Output Video: {output_video}")
    print(f"Target Size: {target_size} MB")
    print(f"Using GPU: {'Yes' if use_gpu else 'No'}")
    print(f"Codec: {codec}")
    print(f"Two-Pass Encoding: {'Enabled' if use_two_pass else 'Disabled'}")

    # Call the compression function
    compress_video(
        input_path=input_video,
        output_path=output_video,
        target_size_mb=target_size,
        use_gpu=use_gpu,
        use_two_pass=use_two_pass,
        codec=codec,
    )

    print("Done.")
    