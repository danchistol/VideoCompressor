# Video Compressor

A simple desktop video-compression app built with Python, Tkinter, and FFmpeg.

The app lets you select one video file or a folder of videos, choose compression settings, and generate compressed outputs using H.264 video and AAC audio.

## Features

- Compress a single video file or all videos in a folder
- GUI built with Tkinter
- Configurable CRF quality setting
- Configurable FFmpeg preset
- Configurable audio bitrate
- Optional output folder
- Automatic FFmpeg detection from PATH or `ffmpeg-downloader`

## Supported input formats

The folder mode scans for:

- `.mp4`
- `.mkv`
- `.avi`
- `.mov`
- `.flv`
- `.wmv`
- `.webm`

## Requirements

- Python 3.9+
- FFmpeg installed and available in PATH, or installed through `ffmpeg-downloader`

## Installation

Clone the repository:

```bash
git clone https://github.com/danchistol/video-compressor.git
cd video-compressor
```

Create and activate a virtual environment:

```bash
python -m venv .venv
```

On Windows:

```bash
.venv\Scripts\activate
```

On macOS/Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Optional: install FFmpeg using `ffmpeg-downloader`:

```bash
ffdl install
```

You can also install FFmpeg manually and add it to your system PATH.

## Usage

Run the app:

```bash
python VideoCompressor.py
```

Then:

1. Choose a video file or a folder containing videos.
2. Optionally choose an output folder.
3. Set CRF, preset, and audio bitrate.
4. Click **Start Compression**.

Compressed files are saved with the `_compressed` suffix.

Example:

```text
input.mp4 -> input_compressed.mp4
```

## Compression settings

### CRF

CRF controls video quality and output size.

- Lower CRF = better quality, larger file
- Higher CRF = lower quality, smaller file
- Recommended range: `18–28`
- Default: `23`

### Preset

Preset controls compression speed and efficiency.

- Faster presets finish sooner but may create larger files
- Slower presets take longer but can create smaller files
- Default: `medium`

### Audio bitrate

Examples:

- `96k` for smaller files
- `128k` as a balanced default
- `192k` for better audio quality

## Notes

- The app overwrites existing output files with the same name.
- Folder compression only processes videos directly inside the selected folder, not nested subfolders.
- FFmpeg output is displayed in the app log.

## Project structure

```text
video-compressor/
├── VideoCompressor.py
├── README.md
├── requirements.txt
├── .gitignore
├── LICENSE
├── pyproject.toml
├── CONTRIBUTING.md
├── CHANGELOG.md
└── .github/
    └── workflows/
        └── python-check.yml
```

## License

This project is licensed under the MIT License.
