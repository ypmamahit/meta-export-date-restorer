# Facebook JSON Metadata EXIF Restorer

A lightweight, zero-dependency Python script designed for Linux Mint/Ubuntu users to parse complex Facebook "Download Your Information" database hierarchies and hardcode original timestamps back into photo and video headers.

### Why This Exists
Facebook strips original camera EXIF data upon upload, but provides historical timestamps inside a messy web of localized, nested JSON files when you export your archive. Existing tools often choke on localized folder names (like Romaji translations) or split multi-file album structures. 

This script maps all 6 known variations of Facebook's time markers (`creation_timestamp`, `taken_timestamp`, `upload_timestamp`, etc.) and pushes them directly into your media files recursively.

### Prerequisites
Ensure `exiftool` is installed on your Linux machine:
```bash
sudo apt update && sudo apt install exiftool -y```

How to Use
1. Download your Facebook information from Meta in JSON format (Select the Posts activity block only).
2. Extract the ZIP archive onto your computer.
3. Drop fb_meta_fixer.py into the root posts/ directory (the folder containing your master JSON indices alongside the media/ and album/ subfolders).
4. Right-click an empty space inside that directory, choose Open in Terminal, and execute:
```python3 fb_meta_fixer.py```
