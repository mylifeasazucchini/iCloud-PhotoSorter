#!/usr/bin/env python3

import os
import csv
from pathlib import Path

def count_files():
    directory = Path("/home/zucc/Dev/PhotoSorter/TestData/iCloud Photos Part 1 of 23/")
    csv_directory = Path("/home/zucc/Dev/PhotoSorter/TestData/iCloud Photos Part 1 of 23/Photos")
    
    # Count media files
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.heic', '.heif', '.mov', '.mp4', '.avi'}
    media_count = 0
    
    print("Scanning directory...")
    for root, dirs, files in os.walk(directory):
        for file in files:
            if Path(file).suffix.lower() in image_extensions:
                media_count += 1
    
    print(f"Found {media_count} media files")
    
    # Count CSV entries
    csv_count = 0
    csv_files = list(csv_directory.glob("*.csv"))
    
    print(f"Found {len(csv_files)} CSV files")
    
    for csv_file in csv_files:
        print(f"Reading {csv_file.name}")
        try:
            with open(csv_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                file_count = 0
                for row in reader:
                    if 'imgName' in row and row['imgName']:
                        file_count += 1
                csv_count += file_count
                print(f"  - {file_count} entries")
        except Exception as e:
            print(f"  - Error: {e}")
    
    print(f"Total CSV entries: {csv_count}")
    
    if media_count == csv_count:
        print("✅ SUCCESS: Counts match!")
    else:
        print(f"❌ MISMATCH: Directory has {media_count}, CSV has {csv_count}")
        print(f"Difference: {media_count - csv_count}")

if __name__ == "__main__":
    count_files()
