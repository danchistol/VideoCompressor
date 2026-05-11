import subprocess
import shutil
import threading
from pathlib import Path
from typing import Optional, Callable

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

try:
    import ffmpeg_downloader as ffdl
except ImportError:
    ffdl = None


FFMPEG_CMD: Optional[str] = None

def init_ffmpeg() -> bool:
    """
    Search for ffmpeg in two ways:
    1) via ffmpeg-downloader (ffdl.ffmpeg_path)
    2) via PATH (shutil.which("ffmpeg"))

    Returns True if found, otherwise False.
    """
    global FFMPEG_CMD

    if ffdl is not None:
        try:
            path = getattr(ffdl, "ffmpeg_path", None)
            if path and Path(path).exists():
                FFMPEG_CMD = path
                return True
        except Exception:
            pass

    path = shutil.which("ffmpeg")
    if path:
        FFMPEG_CMD = path
        return True

    FFMPEG_CMD = None
    return False

def build_output_path(input_path: Path, output_folder: Optional[Path], suffix: str) -> Path:
    if output_folder:
        output_folder.mkdir(parents=True, exist_ok=True)
        return output_folder / (input_path.stem + suffix + input_path.suffix)
    else:
        return input_path.with_name(input_path.stem + suffix + input_path.suffix)

def compress_video(
    input_file: Path,
    output_file: Path,
    crf: int = 23,
    preset: str = "medium",
    audio_bitrate: str = "128k",
    overwrite: bool = True,
    log_callback: Optional[Callable[[str], None]] = None,
) -> bool:
    """Run ffmpeg to compress a single file."""
    if not input_file.exists():
        if log_callback:
            log_callback(f"[ERROR] File does not exist: {input_file}")
        return False

    if FFMPEG_CMD is None:
        if log_callback:
            log_callback("[ERROR] ffmpeg is not available. Check the installation.")
        return False

    cmd = [
        FFMPEG_CMD,
        "-y" if overwrite else "-n",
        "-i",
        str(input_file),
        "-vcodec",
        "libx264",
        "-crf",
        str(crf),
        "-preset",
        preset,
        "-acodec",
        "aac",
        "-b:a",
        audio_bitrate,
        "-movflags",
        "+faststart",
        str(output_file),
    ]

    if log_callback:
        log_callback(f"\n=== Compressing {input_file.name} ===")
        log_callback(f"Output: {output_file.name}")
        log_callback(f"CRF={crf}, preset={preset}, audio={audio_bitrate}")
        log_callback(f"ffmpeg command: {FFMPEG_CMD}")

    try:
        proc = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )

        if log_callback:
            log_callback(proc.stdout)

        if proc.returncode == 0:
            if log_callback:
                log_callback("[OK] Compression completed.\n")
            return True
        else:
            if log_callback:
                log_callback(f"[ERROR] ffmpeg returned code {proc.returncode}.\n")
            return False

    except FileNotFoundError:
        if log_callback:
            log_callback("[ERROR] ffmpeg was not found. Check the installation.\n")
        return False


class VideoCompressorApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Video Compressor (Python + ffmpeg)")
        self.root.geometry("750x520")

        self.input_path_var = tk.StringVar()
        self.output_folder_var = tk.StringVar()
        self.crf_var = tk.IntVar(value=23)
        self.preset_var = tk.StringVar(value="medium")
        self.audio_bitrate_var = tk.StringVar(value="128k")

        self.create_widgets()

        ok = init_ffmpeg()

        if not ok:
            messagebox.showwarning(
                "Warning",
                "ffmpeg was not found.\n\n"
                "- install classic ffmpeg and add it to PATH\n"
                "- or run in terminal:\n"
                "    pip install ffmpeg-downloader\n"
                "    ffdl install\n"
            )
        else:
            self.log(f"ffmpeg found: {FFMPEG_CMD}")

    def create_widgets(self):
        padding = {"padx": 10, "pady": 5}

        frame_input = ttk.Frame(self.root)
        frame_input.pack(fill="x", **padding)

        ttk.Label(frame_input, text="Video file / folder:").pack(anchor="w")

        row1 = ttk.Frame(frame_input)
        row1.pack(fill="x")

        ttk.Entry(row1, textvariable=self.input_path_var).pack(
            side="left",
            fill="x",
            expand=True,
        )

        ttk.Button(
            row1,
            text="Browse...",
            command=self.browse_input,
        ).pack(side="left", padx=5)

        frame_output = ttk.Frame(self.root)
        frame_output.pack(fill="x", **padding)

        ttk.Label(frame_output, text="Output folder (optional):").pack(anchor="w")

        row2 = ttk.Frame(frame_output)
        row2.pack(fill="x")

        ttk.Entry(row2, textvariable=self.output_folder_var).pack(
            side="left",
            fill="x",
            expand=True,
        )

        ttk.Button(
            row2,
            text="Browse...",
            command=self.browse_output_folder,
        ).pack(side="left", padx=5)

        frame_settings = ttk.LabelFrame(self.root, text="Compression Settings")
        frame_settings.pack(fill="x", **padding)

        crf_row = ttk.Frame(frame_settings)
        crf_row.pack(fill="x", pady=3)

        ttk.Label(
            crf_row,
            text="CRF (quality, recommended 18–28):",
        ).pack(side="left")

        crf_scale = ttk.Scale(
            crf_row,
            from_=18,
            to=30,
            orient="horizontal",
            variable=self.crf_var,
        )

        crf_scale.pack(side="left", fill="x", expand=True, padx=5)

        crf_entry = ttk.Entry(
            crf_row,
            textvariable=self.crf_var,
            width=4,
        )

        crf_entry.pack(side="left")

        preset_row = ttk.Frame(frame_settings)
        preset_row.pack(fill="x", pady=3)

        ttk.Label(preset_row, text="Preset (speed):").pack(side="left")

        presets = [
            "ultrafast",
            "superfast",
            "veryfast",
            "faster",
            "fast",
            "medium",
            "slow",
            "slower",
            "veryslow",
        ]

        preset_combo = ttk.Combobox(
            preset_row,
            values=presets,
            textvariable=self.preset_var,
            width=10,
            state="readonly",
        )

        preset_combo.pack(side="left", padx=5)
        preset_combo.current(presets.index("medium"))

        audio_row = ttk.Frame(frame_settings)
        audio_row.pack(fill="x", pady=3)

        ttk.Label(
            audio_row,
            text="Audio bitrate (example: 96k, 128k, 192k):",
        ).pack(side="left")

        ttk.Entry(
            audio_row,
            textvariable=self.audio_bitrate_var,
            width=10,
        ).pack(side="left", padx=5)

        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(fill="x", **padding)

        self.start_button = ttk.Button(
            btn_frame,
            text="Start Compression",
            command=self.start_compression,
        )

        self.start_button.pack(side="left")

        self.status_label = ttk.Label(btn_frame, text="")
        self.status_label.pack(side="left", padx=10)

        log_frame = ttk.LabelFrame(self.root, text="Log")
        log_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.log_text = tk.Text(log_frame, wrap="word", height=10)
        self.log_text.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        scrollbar.pack(side="right", fill="y")

        self.log_text.configure(yscrollcommand=scrollbar.set)

    def log(self, message: str):
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")
        self.root.update_idletasks()

    def browse_input(self):
        choice = messagebox.askyesno(
            "Selection",
            "Do you want to select a FOLDER with multiple videos?\n"
            "Yes = folder, No = file.",
        )

        if choice:
            path = filedialog.askdirectory(title="Select the video folder")
        else:
            path = filedialog.askopenfilename(
                title="Select a video file",
                filetypes=[
                    (
                        "Video Files",
                        "*.mp4 *.mkv *.avi *.mov *.flv *.wmv *.webm",
                    ),
                    ("All Files", "*.*"),
                ],
            )

        if path:
            self.input_path_var.set(path)

    def browse_output_folder(self):
        path = filedialog.askdirectory(title="Select output folder")

        if path:
            self.output_folder_var.set(path)

    def start_compression(self):
        input_path_str = self.input_path_var.get().strip()

        if not input_path_str:
            messagebox.showerror(
                "Error",
                "Please select a file or input folder.",
            )
            return

        input_path = Path(input_path_str)

        if not input_path.exists():
            messagebox.showerror(
                "Error",
                "Input path does not exist.",
            )
            return

        output_folder = (
            Path(self.output_folder_var.get().strip())
            if self.output_folder_var.get().strip()
            else None
        )

        try:
            crf = int(self.crf_var.get())
        except ValueError:
            messagebox.showerror(
                "Error",
                "CRF must be an integer.",
            )
            return

        preset = self.preset_var.get()
        audio_bitrate = self.audio_bitrate_var.get().strip()

        self.start_button.config(state="disabled")
        self.status_label.config(text="Running...")

        thread = threading.Thread(
            target=self.run_compression,
            args=(input_path, output_folder, crf, preset, audio_bitrate),
            daemon=True,
        )

        thread.start()

    def run_compression(
        self,
        input_path: Path,
        output_folder: Optional[Path],
        crf: int,
        preset: str,
        audio_bitrate: str,
    ):
        self.log("=== Starting compression ===")

        if input_path.is_file():
            out_path = build_output_path(
                input_path,
                output_folder,
                "_compressed",
            )

            compress_video(
                input_file=input_path,
                output_file=out_path,
                crf=crf,
                preset=preset,
                audio_bitrate=audio_bitrate,
                overwrite=True,
                log_callback=self.log,
            )

        elif input_path.is_dir():
            video_exts = {
                ".mp4",
                ".mkv",
                ".avi",
                ".mov",
                ".flv",
                ".wmv",
                ".webm",
            }

            files = [
                f
                for f in input_path.iterdir()
                if f.is_file() and f.suffix.lower() in video_exts
            ]

            if not files:
                self.log("No video files found in the folder.")
            else:
                self.log(f"Found {len(files)} video files.")

                for idx, f in enumerate(files, start=1):
                    self.log(f"\n--- File {idx}/{len(files)} ---")

                    out_path = build_output_path(
                        f,
                        output_folder,
                        "_compressed",
                    )

                    compress_video(
                        input_file=f,
                        output_file=out_path,
                        crf=crf,
                        preset=preset,
                        audio_bitrate=audio_bitrate,
                        overwrite=True,
                        log_callback=self.log,
                    )

        else:
            self.log("[ERROR] Input path is neither a file nor a folder.")

        self.log("=== Done ===")

        self.start_button.config(state="normal")
        self.status_label.config(text="Completed")


if __name__ == "__main__":
    root = tk.Tk()
    app = VideoCompressorApp(root)
    root.mainloop()