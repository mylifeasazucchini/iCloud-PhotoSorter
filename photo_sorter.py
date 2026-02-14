#!/usr/bin/env python3

import os
import csv
import shutil
from pathlib import Path
from datetime import datetime

def parse_date(date_str):
    """Parse date string like 'Saturday December 9,2023 7:48 PM GMT'"""
    try:
        # Remove day of week and clean up the string
        clean_date = date_str.split(' ', 1)[1] if ' ' in date_str else date_str
        # Parse the datetime
        dt = datetime.strptime(clean_date, "%B %d,%Y %I:%M %p GMT")
        return dt
    except:
        return None

def organize_photos(source_dir, output_dir):
    """Organize photos based on CSV metadata"""
    
    source_path = Path(source_dir)
    output_path = Path(output_dir)
    
    # Check if there's an intermediate directory (common with zip extraction)
    possible_csv_paths = [
        source_path / "Photos",  # Direct Photos folder
        source_path / source_path.name / "Photos",  # Nested folder with same name as parent
        source_path / (source_path.name + ".zip")[:-4] / "Photos",  # Remove .zip from name if present
    ]
    
    # Also check for any subdirectory that contains a Photos folder
    for subdir in source_path.iterdir():
        if subdir.is_dir():
            photos_path = subdir / "Photos"
            if photos_path.exists() and photos_path.is_dir():
                possible_csv_paths.append(photos_path)
    
    csv_path = None
    for path in possible_csv_paths:
        if path.exists() and path.is_dir():
            csv_files = list(path.glob("*.csv"))
            if csv_files:
                csv_path = path
                break
    
    if not csv_path:
        print(f"No CSV files found in any of these locations:")
        for path in possible_csv_paths:
            print(f"  - {path}")
        return False
    
    # Create output directories - both sorted and hidden in the specified output directory
    sorted_dir = output_path / "SortedPhotos"
    hidden_dir = output_path / "HiddenPhotos"
    
    sorted_dir.mkdir(parents=True, exist_ok=True)
    hidden_dir.mkdir(parents=True, exist_ok=True)
    
    # Find all CSV files in Photos directory
    csv_files = list(csv_path.glob("*.csv"))
    
    if not csv_files:
        print(f"No CSV files found in any of these locations:")
        for path in possible_csv_paths:
            print(f"  - {path}")
        return False
    
    # Track used filenames to handle duplicates
    used_filenames = set()
    
    if not csv_files:
        print(f"No CSV files found in {csv_path}")
        return False
    
    total_processed = 0
    hidden_count = 0
    
    print(f"Processing {len(csv_files)} CSV files...")
    
    for csv_file in csv_files:
        print(f"Reading {csv_file.name}")
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                for row in reader:
                    img_name = row.get('imgName', '').strip()
                    hidden = row.get('hidden', '').strip()
                    favorite = row.get('favorite', '').strip()
                    creation_date = row.get('originalCreationDate', '').strip()
                    
                    if not img_name:
                        continue
                    
                    # Find the media file in source directory
                    media_file = None
                    
                    # First try exact match in the nested Photos directory
                    nested_photos_path = source_path / source_path.name / "Photos"
                    if nested_photos_path.exists():
                        potential_file = nested_photos_path / img_name
                        if potential_file.exists():
                            media_file = potential_file
                    
                    # If not found, try case-insensitive search in all directories
                    if not media_file:
                        for root, dirs, files in os.walk(source_path):
                            for file in files:
                                if file.lower() == img_name.lower():
                                    media_file = Path(root) / file
                                    break
                            if media_file:
                                break
                    
                    if not media_file:
                        print(f"  ⚠️  File not found: {img_name}")
                        continue
                    
                    # Determine destination
                    if hidden == '1' or hidden.lower() == 'yes':
                        dest_dir = hidden_dir
                        hidden_count += 1
                    else:
                        # Check for special file types
                        file_ext = media_file.suffix.lower()
                        
                        if file_ext == '.png':
                            # PNG files go to Screenshots folder (no date subfolders)
                            screenshots_dir = sorted_dir / "Screenshots"
                            screenshots_dir.mkdir(parents=True, exist_ok=True)
                            dest_dir = screenshots_dir
                        elif file_ext in ['.jpg', '.jpeg']:
                            # JPG files go to Misc folder (no date subfolders)
                            misc_dir = sorted_dir / "Misc"
                            misc_dir.mkdir(parents=True, exist_ok=True)
                            dest_dir = misc_dir
                        else:
                            # Other files use date-based organization
                            dest_dir = sorted_dir
                            
                            # Create subdirectories based on date
                            dt = parse_date(creation_date)
                            if dt:
                                year_dir = dest_dir / str(dt.year)
                                month_dir = year_dir / f"{dt.month:02d}-{dt.strftime('%B')}"
                                month_dir.mkdir(parents=True, exist_ok=True)
                                dest_dir = month_dir
                            else:
                                # If date parsing fails, use "Unknown Date"
                                unknown_dir = dest_dir / "Unknown Date"
                                unknown_dir.mkdir(parents=True, exist_ok=True)
                                dest_dir = unknown_dir
                            
                            # Create favorites subdirectory if marked as favorite
                            if favorite == '1' or favorite.lower() == 'yes':
                                fav_dir = dest_dir / "Favorites"
                                fav_dir.mkdir(parents=True, exist_ok=True)
                                dest_dir = fav_dir
                    
                    # Copy the file
                    dest_file = dest_dir / media_file.name
                    
                    # Handle duplicate filenames
                    counter = 1
                    original_dest = dest_file
                    while dest_file.name in used_filenames or dest_file.exists():
                        stem = original_dest.stem
                        suffix = original_dest.suffix
                        dest_file = dest_dir / f"{stem}_{counter}{suffix}"
                        counter += 1
                    
                    used_filenames.add(dest_file.name)
                    
                    try:
                        shutil.copy2(media_file, dest_file)
                        total_processed += 1
                    except Exception as e:
                        print(f"  ❌ Error copying {img_name}: {e}")
                        
        except Exception as e:
            print(f"  ❌ Error reading {csv_file.name}: {e}")
    
    print(f"\n✅ Processing complete!")
    print(f"Total files processed: {total_processed}")
    print(f"Hidden files: {hidden_count}")
    print(f"Sorted files: {total_processed - hidden_count}")
    print(f"Photos organized in: {sorted_dir}")
    print(f"Hidden photos in: {hidden_dir}")
    
    return True

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 3:
        print("Usage: python photo_sorter.py <source_directory> <output_directory>")
        print("Example: python photo_sorter.py /path/to/iCloud_Photos /path/to/output")
        sys.exit(1)
    
    source_dir = sys.argv[1]
    output_dir = sys.argv[2]
    
    if not os.path.exists(source_dir):
        print(f"❌ Source directory does not exist: {source_dir}")
        sys.exit(1)
    
    organize_photos(source_dir, output_dir)
