# Meta Export Date Restorer (Facebook & Instagram)

When downloading your historical archives from Facebook or Instagram, the exported photos and videos lose their original timeline metadata. Local files are forced to show the creation date of the *day you downloaded the archive*, throwing your local file system, photo library, or cloud storage backup into total chronological chaos.

Fortunately, Meta ships database logs alongside your media in `.json` format. This script crawls your export root directory, maps filenames to their true historical timestamps, and uses `exiftool` to permanently inject those dates back into the binary EXIF properties of your photos and videos.

## ⚠️ Important Accuracy Note: Camera Date vs. Upload Date

Because Meta aggressively modifies user uploads, it is critical to understand what metadata your export actually contains:

1. **True Camera Dates (Priority 1):** In certain parts of modern backups (such as Instagram Stories), Meta retains the true hardware capture stamp under a buried variable `date_time_original` (e.g., `20250223T045820.000Z`). **This script is hardcoded to prioritize this exact timestamp.**
2. **Platform Upload Dates (Priority 2 Fallback):** For standard timeline posts or older archival blocks, Meta permanently strips the camera EXIF file metadata upon upload. For those files, the backup only provides a `creation_timestamp`, which tracks **the day and time you uploaded the file to Facebook or Instagram**.

If a true camera date does not exist, this script automatically falls back to the Platform Upload date. While this means a photo taken in 2015 but posted as a throwback in 2018 will register as 2018, it still successfully moves your media files out of the present day and directly back into their proper historical timeline.

## Prerequisites

1. **Python 3.x:** Installed and added to your system environment variables.
2. **ExifTool:** The script drives ExifTool in the background to modify core image metadata.
   - **Windows:** Download the application executable from the Official ExifTool Site (https://exiftool.org/), rename your download to `exiftool.exe`, and drag it directly into the directory containing this script.
   - **macOS:** Install via Homebrew: `brew install exiftool`
   - **Linux:** Install via your package manager: `sudo apt install libimage-exiftool-perl`

## Execution and Setup

Download the `restore_dates.py` file and place it directly into the root directory of your extracted data folder.

### Directory Structure Examples

#### For Facebook Exports:

    /your_facebook_export/
    ├── /messages/
    ├── /photos_and_videos/
    ├── /posts/
    └── restore_dates.py

#### For Instagram Exports:

    /your_instagram_export/
    ├── /media/
    ├── /your_instagram_activity/
    └── restore_dates.py

### Running the Utility

Open your command prompt or terminal, change directory (`cd`) into your root export folder, and run the following command:

    python restore_dates.py

## How It Processes Your Files
- **Discovery:** Walks down all paths to open and read nested `.json` indices.
- **Deduplication & Extraction:** Resolves filenames derived from data URIs, parses date matrices, and ensures accurate data targeting.
- **Safe Execution:** Commands are safely piped. File anomalies or broken JSON formatting will be skipped without interrupting or crashing a multi-thousand file execution batch.
