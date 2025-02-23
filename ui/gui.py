import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
from PIL import Image
import os

class VideoCompressorGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        # Essential window settings
        self.title("Video Compressor")
        self.geometry("1000x700")
        self.resizable(False, False)
        ctk.set_appearance_mode("System")
        self.current_theme = ctk.get_appearance_mode()
        ctk.set_default_color_theme("dark-blue")
        
        # Setup constants and variables
        self.setup_constants()
        self.setup_variables()
        
        # Build UI sections
        self.create_nav_bar()
        self.create_main_content_frame()     # Grid container with 3 rows: top, common info, and theme buttons
        self.create_file_size_page()         # Builds file size UI into left_content_frame
        self.create_custom_page_frame()      # Builds custom UI into left_content_frame
        self.create_common_video_info()      # Builds common video info into right_content_frame
        
        # Start with the File Size page
        self.show_file_size_page()
        self.bind_drag_and_drop()

    def setup_constants(self):
        self.PADDING = 5
        self.BUTTON_HEIGHT = 45
        self.BUTTON_WIDTH = 300
        self.ENTRY_WIDTH = 150
        self.CORNER_RADIUS = 10
        self.FONT = ctk.CTkFont(family="Arial", size=12)
        self.THEME_OPTIONS = ["Dark", "Light", "System"]

    def setup_variables(self):
        # Video metadata
        self.video_filepath = None
        self.video_length = "N/A"
        self.video_original_resolution = "N/A"
        self.video_original_framerate = "N/A"
        self.video_original_bitrate = "N/A"
        self.estimated_output_size = "N/A"
        # Sidebar
        self.sidebar_expanded = False
        self.sidebar_width_narrow = 60
        self.sidebar_width_expanded = 150
        # Theme
        self.theme_var = tk.StringVar(value="System")
        # Shared parameters (for both pages)
        self.use_gpu_var = tk.BooleanVar(value=False)
        self.use_two_pass_var = tk.BooleanVar(value=False)
        self.codec_var = tk.StringVar(value="h264")
        self.codec_options = ["h264", "h265", "av1"]
        # Additional Custom page parameters
        self.resolution_var = tk.StringVar(value="720p")
        self.framerate_var = tk.StringVar(value="30")
        self.bitrate_var = tk.StringVar()

    def create_nav_bar(self):
        self.nav_frame = ctk.CTkFrame(self, width=self.sidebar_width_narrow, corner_radius=0, fg_color="transparent")
        self.nav_frame.pack(side="left", fill="y")
        self.nav_frame.grid_rowconfigure(4, weight=1)

        self.nav_toggle_button = ctk.CTkButton(
            self.nav_frame,
            text=">",
            image=self.load_nav_icon("nav.png"),
            width=30,
            height=30,
            command=self.toggle_sidebar
        )
        self.nav_toggle_button.grid(row=0, column=0, padx=self.PADDING, pady=self.PADDING, sticky="n")

        self.file_size_nav_button = ctk.CTkButton(
            self.nav_frame,
            text="",
            image=self.load_nav_icon("filesize.png"),
            compound="left",
            anchor="w",
            width=50,
            height=40,
            corner_radius=0,
            command=self.show_file_size_page
        )
        self.file_size_nav_button.grid(row=1, column=0, sticky="ew")

        self.custom_nav_button = ctk.CTkButton(
            self.nav_frame,
            text="",
            image=self.load_nav_icon("placeholder.png"),
            compound="left",
            anchor="w",
            width=50,
            height=40,
            corner_radius=0,
            command=self.show_custom_page
        )
        self.custom_nav_button.grid(row=2, column=0, sticky="ew")

    def create_main_content_frame(self):
        # Pack main content frame (outside grid)
        self.main_content_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_content_frame.pack(side="right", fill="both", expand=True)

        # Create a grid container inside main_content_frame with 3 rows.
        self.grid_container = ctk.CTkFrame(self.main_content_frame, fg_color="transparent")
        self.grid_container.pack(fill="both", expand=True)

        # Row 0: Top content (left & right columns)
        self.grid_container.grid_rowconfigure(0, weight=1)
        # Row 1: Common info section (status, textbox, progress)
        self.grid_container.grid_rowconfigure(1, weight=0)
        # Row 2: Theme segmented button row
        self.grid_container.grid_rowconfigure(2, weight=0)
        # Two columns: left (page-specific), right (video info)
        self.grid_container.grid_columnconfigure(0, weight=0)  # left: fixed
        self.grid_container.grid_columnconfigure(1, weight=1)  # right: expands

        # Left content frame: for page-specific UI.
        self.left_content_frame = ctk.CTkFrame(self.grid_container, fg_color="transparent")
        self.left_content_frame.grid(row=0, column=0, sticky="nsew", padx=self.PADDING, pady=self.PADDING)

        # Right content frame: for common video info.
        self.right_content_frame = ctk.CTkFrame(self.grid_container, fg_color="transparent")
        self.right_content_frame.grid(row=0, column=1, sticky="nsew", padx=self.PADDING, pady=self.PADDING)

        # Common info section (spanning full width) in row 1.
        self.common_info_frame = ctk.CTkFrame(self.grid_container, fg_color="transparent")
        self.common_info_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=self.PADDING, pady=self.PADDING)

        # Theme segmented button row in row 2.
        self.theme_frame = ctk.CTkFrame(self.grid_container, fg_color="transparent")
        self.theme_frame.grid(row=2, column=0, columnspan=2, sticky="e", padx=self.PADDING, pady=self.PADDING)
        self.theme_segmented_button = ctk.CTkSegmentedButton(
            master=self.theme_frame,
            values=self.THEME_OPTIONS,
            variable=self.theme_var,
            command=self.handle_theme_segmented,
            width=150,
            height=25
        )
        self.theme_segmented_button.pack()

    def create_file_size_page(self):
        # Build the File Size page into left_content_frame.
        self.file_size_page = ctk.CTkFrame(self.left_content_frame, corner_radius=0, fg_color="transparent")
        # Content for file size page:
        self.file_size_left_frame = ctk.CTkFrame(self.file_size_page, fg_color="transparent")
        self.file_size_left_frame.pack(side="left", fill="both", expand=True, padx=self.PADDING)

        self.browse_button = ctk.CTkButton(
            self.file_size_left_frame,
            text="Browse",
            command=self.browse_file,
            height=self.BUTTON_HEIGHT,
            width=self.BUTTON_WIDTH,
            corner_radius=self.CORNER_RADIUS,
            font=self.FONT
        )
        self.browse_button.pack(pady=(self.PADDING*2, self.PADDING/2))

        self.file_size_compression_frame = ctk.CTkFrame(self.file_size_left_frame, fg_color="transparent")
        self.file_size_compression_frame.pack(pady=self.PADDING/2)
        self.compress_button = ctk.CTkButton(
            self.file_size_compression_frame,
            text="Compress",
            command=self.compress_video,
            height=self.BUTTON_HEIGHT,
            width=(self.BUTTON_WIDTH/2)-2,
            corner_radius=self.CORNER_RADIUS,
            font=self.FONT
        )
        self.compress_button.pack(side="left", padx=(0, self.PADDING))
        self.cancel_button = ctk.CTkButton(
            self.file_size_compression_frame,
            text="Cancel",
            command=self.cancel_compression,
            height=self.BUTTON_HEIGHT,
            width=(self.BUTTON_WIDTH/2)-2,
            corner_radius=self.CORNER_RADIUS,
            font=self.FONT,
            fg_color=("#DB3E39", "#821D1A"),
            hover_color="dark red"
        )
        self.cancel_button.pack(side="left")

        # Parameters on File Size Page
        self.file_size_input_frame = ctk.CTkFrame(self.file_size_left_frame, fg_color="transparent")
        self.file_size_input_frame.pack(pady=self.PADDING/2)
        self.file_size_input_frame.grid_columnconfigure(0, minsize=150)
        self.file_size_input_frame.grid_columnconfigure(1, minsize=150)

        self.use_gpu_label = ctk.CTkLabel(self.file_size_input_frame, text="Use GPU", font=self.FONT)
        self.use_gpu_label.grid(row=0, column=0, padx=(0,5), sticky="e")
        self.use_gpu_switch = ctk.CTkSwitch(self.file_size_input_frame, text="", variable=self.use_gpu_var, font=self.FONT)
        self.use_gpu_switch.grid(row=0, column=1, columnspan=2, sticky="w", padx=(0, self.PADDING))

        self.use_two_pass_label = ctk.CTkLabel(self.file_size_input_frame, text="Two-Pass", font=self.FONT)
        self.use_two_pass_label.grid(row=1, column=0, padx=(0,5), sticky="e")
        self.use_two_pass_switch = ctk.CTkSwitch(self.file_size_input_frame, text="", variable=self.use_two_pass_var, font=self.FONT)
        self.use_two_pass_switch.grid(row=1, column=1, columnspan=2, sticky="w", padx=(0, self.PADDING))

        self.codec_label = ctk.CTkLabel(self.file_size_input_frame, text="Codec", font=self.FONT)
        self.codec_label.grid(row=2, column=0, padx=(0,5), sticky="e")
        self.codec_dropdown = ctk.CTkOptionMenu(
            self.file_size_input_frame,
            values=self.codec_options,
            variable=self.codec_var,
            width=self.ENTRY_WIDTH,
            font=self.FONT
        )
        self.codec_dropdown.grid(row=2, column=1, padx=(0, self.PADDING), sticky="w")

        self.target_size_label = ctk.CTkLabel(self.file_size_input_frame, text="Target Size (MB)", font=self.FONT)
        self.target_size_label.grid(row=3, column=0, padx=(0,5), sticky="e")
        self.target_size_entry = ctk.CTkEntry(self.file_size_input_frame, width=self.ENTRY_WIDTH, font=self.FONT)
        self.target_size_entry.grid(row=3, column=1, padx=(0, self.PADDING), sticky="w")

    def create_custom_page_frame(self):
        # Build the Custom page into left_content_frame.
        self.custom_page_frame = ctk.CTkFrame(self.left_content_frame, corner_radius=0, fg_color="transparent")
        # Content for custom page:
        self.custom_left_frame = ctk.CTkFrame(self.custom_page_frame, fg_color="transparent")
        self.custom_left_frame.pack(side="left", fill="both", expand=True, padx=self.PADDING)

        self.custom_browse_button = ctk.CTkButton(
            self.custom_left_frame,
            text="Browse",
            command=self.browse_file,
            height=self.BUTTON_HEIGHT,
            width=self.BUTTON_WIDTH,
            corner_radius=self.CORNER_RADIUS,
            font=self.FONT
        )
        self.custom_browse_button.pack(pady=(self.PADDING*2, self.PADDING/2))

        self.custom_compression_frame = ctk.CTkFrame(self.custom_left_frame, fg_color="transparent")
        self.custom_compression_frame.pack(pady=self.PADDING/2)
        self.custom_compress_button = ctk.CTkButton(
            self.custom_compression_frame,
            text="Compress",
            command=self.compress_video,
            height=self.BUTTON_HEIGHT,
            width=(self.BUTTON_WIDTH/2)-2,
            corner_radius=self.CORNER_RADIUS,
            font=self.FONT
        )
        self.custom_compress_button.pack(side="left", padx=(0, self.PADDING))
        self.custom_cancel_button = ctk.CTkButton(
            self.custom_compression_frame,
            text="Cancel",
            command=self.cancel_compression,
            height=self.BUTTON_HEIGHT,
            width=(self.BUTTON_WIDTH/2)-2,
            corner_radius=self.CORNER_RADIUS,
            font=self.FONT,
            fg_color=("#DB3E39", "#821D1A"),
            hover_color="dark red"
        )
        self.custom_cancel_button.pack(side="left")

        # Parameters on Custom Page
        self.custom_input_frame = ctk.CTkFrame(self.custom_left_frame, fg_color="transparent")
        self.custom_input_frame.pack(pady=self.PADDING/2)
        self.custom_input_frame.grid_columnconfigure(0, minsize=150)
        self.custom_input_frame.grid_columnconfigure(1, minsize=150)

        self.use_gpu_label2 = ctk.CTkLabel(self.custom_input_frame, text="Use GPU", font=self.FONT)
        self.use_gpu_label2.grid(row=0, column=0, padx=(0,5), sticky="e")
        self.use_gpu_switch2 = ctk.CTkSwitch(self.custom_input_frame, text="", variable=self.use_gpu_var, font=self.FONT)
        self.use_gpu_switch2.grid(row=0, column=1, columnspan=2, sticky="w", padx=(0, self.PADDING))

        self.use_two_pass_label2 = ctk.CTkLabel(self.custom_input_frame, text="Two-Pass", font=self.FONT)
        self.use_two_pass_label2.grid(row=1, column=0, padx=(0,5), sticky="e")
        self.use_two_pass_switch2 = ctk.CTkSwitch(self.custom_input_frame, text="", variable=self.use_two_pass_var, font=self.FONT)
        self.use_two_pass_switch2.grid(row=1, column=1, columnspan=2, sticky="w", padx=(0, self.PADDING))

        self.resolution_label = ctk.CTkLabel(self.custom_input_frame, text="Resolution", font=self.FONT)
        self.resolution_label.grid(row=2, column=0, padx=(0,5), sticky="e")
        self.resolution_options = ["720p", "1080p", "1440p"]
        self.resolution_dropdown = ctk.CTkOptionMenu(
            self.custom_input_frame,
            values=self.resolution_options,
            variable=self.resolution_var,
            command=self.update_bitrate_options,
            width=self.ENTRY_WIDTH,
            font=self.FONT
        )
        self.resolution_dropdown.grid(row=2, column=1, padx=(0, self.PADDING), sticky="w")

        self.framerate_label = ctk.CTkLabel(self.custom_input_frame, text="Framerate", font=self.FONT)
        self.framerate_label.grid(row=3, column=0, padx=(0,5), sticky="e")
        self.framerate_options = ["30", "60"]
        self.framerate_dropdown = ctk.CTkOptionMenu(
            self.custom_input_frame,
            values=self.framerate_options,
            variable=self.framerate_var,
            command=self.update_bitrate_options,
            width=self.ENTRY_WIDTH,
            font=self.FONT
        )
        self.framerate_dropdown.grid(row=3, column=1, padx=(0, self.PADDING), sticky="w")

        self.bitrate_label = ctk.CTkLabel(self.custom_input_frame, text="Bitrate", font=self.FONT)
        self.bitrate_label.grid(row=4, column=0, padx=(0,5), sticky="e")
        self.bitrate_options = []
        self.bitrate_dropdown = ctk.CTkOptionMenu(self.custom_input_frame, values=self.bitrate_options, variable=self.bitrate_var, width=self.ENTRY_WIDTH, font=self.FONT)
        self.bitrate_dropdown.grid(row=4, column=1, padx=(0, self.PADDING), sticky="w")

        self.custom_codec_label = ctk.CTkLabel(self.custom_input_frame, text="Codec", font=self.FONT)
        self.custom_codec_label.grid(row=5, column=0, padx=(0,5), sticky="e")
        self.custom_codec_dropdown = ctk.CTkOptionMenu(self.custom_input_frame, values=self.codec_options, variable=self.codec_var, width=self.ENTRY_WIDTH, font=self.FONT)
        self.custom_codec_dropdown.grid(row=5, column=1, padx=(0, self.PADDING), sticky="w")

    def create_common_video_info(self):
        # Build the common video info (right column) that is shared by both pages.
        self.right_content_frame = ctk.CTkFrame(self.grid_container, fg_color="transparent")
        self.right_content_frame.grid(row=0, column=1, sticky="nsew", padx=self.PADDING, pady=self.PADDING)
        
        self.preview_image_label = ctk.CTkLabel(self.right_content_frame, text="", width=250, height=200)
        self.preview_image_label.pack(pady=(self.PADDING*2, self.PADDING/2))
        
        self.video_info_frame = ctk.CTkFrame(self.right_content_frame, fg_color="transparent")
        self.video_info_frame.pack(pady=(0, self.PADDING), fill="x")
        self.length_res_fps_label = ctk.CTkLabel(self.video_info_frame, text="Length: N/A (N/A) N/A", font=self.FONT)
        self.length_res_fps_label.pack(anchor="w", pady=(0, 2))
        self.size_codec_bitrate_label = ctk.CTkLabel(self.video_info_frame, text="Size: N/A N/A N/A", font=self.FONT)
        self.size_codec_bitrate_label.pack(anchor="w", pady=(0, 2))
        
        # Common info section (for compression status, etc.) is placed in the common_info_frame (row 1)
        common_info = self._create_info_section(self.common_info_frame, height=300)
        self.common_info_textbox = common_info["textbox"]
        self.common_progress_bar = common_info["progress_bar"]
        self.common_status_label = common_info["status_label"]

    def _create_info_section(self, master, height=200):
        frame = ctk.CTkFrame(master, fg_color="transparent")
        frame.pack(pady=self.PADDING, padx=self.PADDING, fill="x")
        textbox = ctk.CTkTextbox(frame, wrap="word", height=height, corner_radius=self.CORNER_RADIUS, font=self.FONT)
        textbox.pack(pady=(self.PADDING, 0), fill="x")
        textbox.insert("0.0", "Ready...")
        textbox.configure(state="disabled")
        progress_bar = ctk.CTkProgressBar(frame, height=20)
        progress_bar.pack(pady=(self.PADDING/2, 0), fill="x")
        progress_bar.set(0)
        status_label = ctk.CTkLabel(frame, text="Ready", font=self.FONT)
        status_label.pack(pady=(0, self.PADDING/2))
        return {"textbox": textbox, "progress_bar": progress_bar, "status_label": status_label}

    def toggle_sidebar(self):
        if self.sidebar_expanded:
            self.nav_frame.configure(width=self.sidebar_width_narrow)
            self.file_size_nav_button.configure(text="", width=50)
            self.custom_nav_button.configure(text="", width=50)
            self.nav_toggle_button.configure(text=">")
        else:
            self.nav_frame.configure(width=self.sidebar_width_expanded)
            self.file_size_nav_button.configure(text="File Size", width=120)
            self.custom_nav_button.configure(text="Custom", width=120)
            self.nav_toggle_button.configure(text="<")
        self.sidebar_expanded = not self.sidebar_expanded

    def show_file_size_page(self):
        self.custom_page_frame.grid_forget()
        self.file_size_page.grid(row=0, column=0, sticky="nsew")
        self.update_video_info()

    def show_custom_page(self):
        self.file_size_page.grid_forget()
        self.custom_page_frame.grid(row=0, column=0, sticky="nsew")
        self.update_video_info()

    def update_bitrate_options(self, event=None):
        resolution = self.resolution_var.get()
        framerate = self.framerate_var.get()
        if resolution == "720p" and framerate == "60":
            bitrate_options = ["Ultra (9.4 Mbps)", "High (7.5 Mbps)", "Medium (5.6 Mbps)", "Low (3.8 Mbps)"]
        elif resolution == "720p" and framerate == "30":
            bitrate_options = ["Ultra (7.0 Mbps)", "High (5.6 Mbps)", "Medium (4.2 Mbps)", "Low (2.8 Mbps)"]
        elif resolution == "1080p" and framerate == "60":
            bitrate_options = ["Ultra (15.0 Mbps)", "High (12.0 Mbps)", "Medium (9.0 Mbps)", "Low (6.0 Mbps)"]
        elif resolution == "1080p" and framerate == "30":
            bitrate_options = ["Ultra (11.3 Mbps)", "High (9.0 Mbps)", "Medium (6.8 Mbps)", "Low (4.5 Mbps)"]
        elif resolution == "1440p" and framerate == "60":
            bitrate_options = ["Ultra (28.0 Mbps)", "High (22.0 Mbps)", "Medium (16.0 Mbps)", "Low (11.0 Mbps)"]
        elif resolution == "1440p" and framerate == "30":
            bitrate_options = ["Ultra (22.0 Mbps)", "High (16.5 Mbps)", "Medium (12.4 Mbps)", "Low (8.3 Mbps)"]
        else:
            bitrate_options = []
        self.bitrate_options = bitrate_options
        self.bitrate_var.set("")
        self.bitrate_dropdown.configure(values=self.bitrate_options)

    def update_video_info(self):
        if self.video_filepath:
            length_res_fps_text = f"Length: {self.video_length} ({self.video_original_resolution}) {self.video_original_framerate}"
            chosen_codec = self.codec_var.get() if self.codec_var.get() else "N/A"
            chosen_bitrate = self.bitrate_var.get() if self.bitrate_var.get() else "N/A"
            size_codec_bitrate_text = f"Size: {self.estimated_output_size} {chosen_codec} {chosen_bitrate}"
            self.length_res_fps_label.configure(text=length_res_fps_text)
            self.size_codec_bitrate_label.configure(text=size_codec_bitrate_text)
        else:
            self.length_res_fps_label.configure(text="Length: N/A (N/A) N/A")
            self.size_codec_bitrate_label.configure(text="Size: N/A N/A N/A")

    def browse_file(self):
        filepath = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4;*.avi;*.mov")])
        if filepath:
            self.video_filepath = filepath
            self.update_status(f"Selected file: {filepath}")
            self.load_preview_image(filepath)
            # For demonstration, set metadata manually
            self.video_length = "0:34"
            self.video_original_resolution = "2560x1440"
            self.video_original_framerate = "60fps"
            self.video_original_bitrate = "28Mbps"
            self.estimated_output_size = "116.83 MB"

    def load_preview_image(self, filepath):
        try:
            image_path = os.path.join(os.path.dirname(__file__), "default_preview.png")
            if os.path.exists(image_path):
                img = ctk.CTkImage(Image.open(image_path), size=(250, 200))
                self.preview_image_label.configure(image=img, text="")
            else:
                self.preview_image_label.configure(text="Preview not available")
        except Exception as e:
            print(f"Error loading preview image: {e}")
            self.preview_image_label.configure(text="Preview not available")

    def compress_video(self):
        target_size = self.target_size_entry.get()
        codec = self.codec_var.get()
        use_gpu = self.use_gpu_var.get()
        use_two_pass = self.use_two_pass_var.get()
        self.update_status("Compressing... (Placeholder)")
        self.update_progress(0.25)
        self.after(1000, lambda: self.update_progress(0.5))
        self.after(2000, lambda: self.update_progress(0.75))
        self.after(3000, lambda: self.compression_complete())

    def cancel_compression(self):
        self.update_status("Compression cancelled.")
        self.update_progress(0)

    def update_status(self, message):
        self.status_label.configure(text=message)
        self.info_textbox.configure(state="normal")
        self.info_textbox.delete("0.0", "end")
        self.info_textbox.insert("0.0", message)
        self.info_textbox.configure(state="disabled")
        self.info_textbox.see(tk.END)

        if hasattr(self, 'custom_status_label'):
            self.custom_status_label.configure(text=message)
        if hasattr(self, 'custom_info_textbox'):
            self.custom_info_textbox.configure(state="normal")
            self.custom_info_textbox.delete("0.0", "end")
            self.custom_info_textbox.insert("0.0", message)
            self.custom_info_textbox.configure(state="disabled")
            self.custom_info_textbox.see(tk.END)

    def update_progress(self, value):
        self.progress_bar.set(value)
        if hasattr(self, 'custom_progress_bar'):
            self.custom_progress_bar.set(value)

    def compression_complete(self):
        self.update_status("Compression complete!")
        self.update_progress(1.0)

    def handle_theme_segmented(self, selected_value):
        self.change_theme(selected_value)

    def change_theme(self, theme):
        ctk.set_appearance_mode(theme)
        self.current_theme = theme
        self.update()
        if theme.lower() == "dark":
            ctk.set_default_color_theme("blue")
        elif theme.lower() == "light":
            ctk.set_default_color_theme("green")
        elif theme.lower() == "system":
            if ctk.get_appearance_mode() == "Dark":
                ctk.set_default_color_theme("blue")
            else:
                ctk.set_default_color_theme("green")

    def drop(self, event):
        if event.data:
            filepath = event.data.split()[0]
            filepath = filepath.strip("{}")
            self.update_status(f"Dropped file: {filepath}")

    def bind_drag_and_drop(self):
        try:
            self.tk.call('tkdnd::drop_target', self._w, "+dropfiles")
            self.bind("<Drop>", self.drop)
        except tk.TclError:
            print("tkdnd package not available. Drag and drop will not work.")

    def drop_target_unregister(self):
        try:
            self.tk.call('tkdnd::drop_target', self._w, "-dropfiles")
        except tk.TclError:
            pass

    def load_nav_icon(self, filename):
        try:
            image_path = os.path.join(os.path.dirname(__file__), filename)
            image = ctk.CTkImage(tk.PhotoImage(file=image_path), size=(20, 20))
            return image
        except tk.TclError:
            print(f"Error loading navigation icon: {filename}. Make sure it exists in the same directory.")
            return None

if __name__ == "__main__":
    app = VideoCompressorGUI()
    app.mainloop()
