import json
import os
import subprocess
from datetime import datetime

media_data = {}

# Search-and-rescue function for hidden timestamps
def find_timestamp_in_tree(node):
    if isinstance(node, dict):
        for key in ['creation_timestamp', 'timestamp', 'taken_timestamp', 'upload_timestamp', 'timestamp_value', 'update_timestamp']:
            if key in node and isinstance(node[key], int) and node[key] > 0:
                return node[key]
        for key, value in node.items():
            res = find_timestamp_in_tree(value)
            if res: return res
    elif isinstance(node, list):
        for item in node:
            res = find_timestamp_in_tree(item)
            if res: return res
    return None

def extract_media(node, current_time=None):
    if isinstance(node, dict):
        time_at_this_level = None
        for key in ['creation_timestamp', 'timestamp', 'taken_timestamp', 'upload_timestamp', 'timestamp_value', 'update_timestamp']:
            if key in node and isinstance(node[key], int) and node[key] > 0:
                time_at_this_level = node[key]
                break
        
        time_value = time_at_this_level or current_time
        
        if 'uri' in node:
            uri = str(node['uri'])
            if '/' in uri:
                # Strip away the folder path to get just the filename
                filename = uri.split('/')[-1]
                
                best_time = time_value or find_timestamp_in_tree(node)
                if best_time:
                    media_data[filename] = best_time
                    
        for key, value in node.items():
            extract_media(value, time_value)
            
    elif isinstance(node, list):
        for item in node:
            extract_media(item, current_time)

print("Hunting down EVERY JSON file in all folders and subfolders...")

# THE FIX: This now digs into album/0, album/1, etc., to read their internal JSONs
for root, dirs, files in os.walk('.'):
    for file in files:
        if file.endswith('.json'):
            json_path = os.path.join(root, file)
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    extract_media(data)
            except Exception as e:
                pass  # Silently skip any broken json files

print(f"Success! Found {len(media_data)} total media timestamps in the databases.")
print("Scanning subfolders and injecting dates... (This will take a moment)")

processed = 0
for root, dirs, files in os.walk('.'):
    for file in files:
        if file in media_data:
            filepath = os.path.join(root, file)
            timestamp = media_data[file]
            
            try:
                exif_time = datetime.fromtimestamp(timestamp).strftime('%Y:%m:%d %H:%M:%S')
                cmd = ['exiftool', '-overwrite_original', f'-AllDates={exif_time}', filepath]
                subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                processed += 1
            except Exception:
                pass

print(f"Done! Successfully injected real dates into {processed} files.")
