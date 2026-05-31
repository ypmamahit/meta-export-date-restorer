#!/usr/bin/env python3
import json
import os
import subprocess
import re
from datetime import datetime

# Dictionary map: filename -> 'YYYY:MM:DD HH:MM:SS'
media_dates = {}

def parse_meta_string_date(date_str):
    """
    Translates Meta's hidden date_time_original strings into standard EXIF format.
    Matches formats like "20250223T045820.000Z" or "2025-02-23T04:58:20".
    """
    m = re.match(r'^(\d{4})-?(\d{2})-?(\d{2})T(\d{2}):?(\d{2}):?(\d{2})', date_str)
    if m:
        return f"{m.group(1)}:{m.group(2)}:{m.group(3)} {m.group(4)}:{m.group(5)}:{m.group(6)}"
    return None

def find_best_date_in_tree(node):
    """
    Deep-scans a specific JSON sub-tree to grab the highest accuracy date available.
    """
    # PRIORITY 1: Look for the raw camera hardware timestamp if preserved
    def dig_for_exact(n):
        if isinstance(n, dict):
            if 'date_time_original' in n and isinstance(n['date_time_original'], str):
                parsed = parse_meta_string_date(n['date_time_original'])
                if parsed: return parsed
            for v in n.values():
                res = dig_for_exact(v)
                if res: return res
        elif isinstance(n, list):
            for item in n:
                res = dig_for_exact(item)
                if res: return res
        return None
        
    exact_date = dig_for_exact(node)
    if exact_date:
        return exact_date
        
    # PRIORITY 2: Fallback to Unix timestamps representing the upload date
    unix_keys = ['taken_timestamp', 'creation_timestamp', 'upload_timestamp', 'timestamp', 'timestamp_value']
    
    def dig_for_unix(n):
        if isinstance(n, dict):
            for key in unix_keys:
                if key in n and isinstance(n[key], int) and n[key] > 0:
                    return n[key]
            for v in n.values():
                res = dig_for_unix(v)
                if res: return res
        elif isinstance(n, list):
            for item in n:
                res = dig_for_unix(item)
                if res: return res
        return None
        
    unix_ts = dig_for_unix(node)
    if unix_ts:
        return datetime.fromtimestamp(unix_ts).strftime('%Y:%m:%d %H:%M:%S')
        
    return None

def extract_media(node, current_date=None):
    """
    Recursively maps media file names to their corresponding metadata timestamps.
    """
    if isinstance(node, dict):
        level_date = None
        if 'date_time_original' in node and isinstance(node['date_time_original'], str):
            level_date = parse_meta_string_date(node['date_time_original'])
        
        if not level_date:
            for key in ['taken_timestamp', 'creation_timestamp', 'upload_timestamp', 'timestamp']:
                if key in node and isinstance(node[key], int) and node[key] > 0:
                    level_date = datetime.fromtimestamp(node[key]).strftime('%Y:%m:%d %H:%M:%S')
                    break
                    
        active_date = level_date or current_date
        
        if 'uri' in node:
            uri = str(node['uri'])
            if '/' in uri:
                filename = uri.split('/')[-1]
                best_date = find_best_date_in_tree(node) or active_date
                if best_date:
                    media_dates[filename] = best_date
        
        for key, value in node.items():
            extract_media(value, active_date)
            
    elif isinstance(node, list):
        for item in node:
            extract_media(item, current_date)

def main():
    print("🔍 Scanning folders recursively for Meta JSON databases...")
    
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.json'):
                json_path = os.path.join(root, file)
                try:
                    with open(json_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        extract_media(data)
                except Exception:
                    pass  # Safely ignore unreadable or corrupted JSON files

    print(f"✅ Mapping Complete! Found timestamps for {len(media_dates)} unique media files.")
    print("📸 Injecting timeline data via ExifTool... (This may take a few minutes)")

    processed = 0
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file in media_dates:
                filepath = os.path.join(root, file)
                exif_time = media_dates[file]
                
                try:
                    # Overwrites the original to preserve space, quiet mode enabled
                    cmd = ['exiftool', '-overwrite_original', f'-AllDates={exif_time}', filepath]
                    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    processed += 1
                except Exception:
                    pass

    print(f"🎉 Done! Successfully restored metadata dates to {processed} media files.")

if __name__ == '__main__':
    main()
