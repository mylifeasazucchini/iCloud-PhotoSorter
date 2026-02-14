#!/usr/bin/env python3

import os
import csv
from pathlib import Path

def count_media_files(directory):
    """Count media files in directory and subdirectories"""
    directory = Path(directory)
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.heic', '.heif', '.mov', '.mp4', '.avi', '.png'}
    
    media_count = 0
    for root, dirs, files in os.walk(directory):
        for file in files:
            if Path(file).suffix.lower() in image_extensions:
                media_count += 1
    
    return media_count

def count_csv_entries(csv_directory):
    """Count total entries in all CSV files"""
    
    # Check if there's an intermediate directory (common with zip extraction)
    possible_csv_paths = [
        Path(csv_directory),  # Direct path
        Path(csv_directory).parent / Path(csv_directory).name / "Photos",  # Nested folder
    ]
    
    # Also check for any subdirectory that contains a Photos folder
    source_path = Path(csv_directory).parent
    for subdir in source_path.iterdir():
        if subdir.is_dir():
            photos_path = subdir / "Photos"
            if photos_path.exists() and photos_path.is_dir():
                possible_csv_paths.append(photos_path)
    
    csv_files = []
    for path in possible_csv_paths:
        if path.exists() and path.is_dir():
            found_files = list(path.glob("*.csv"))
            if found_files:
                csv_files.extend(found_files)
                break
    
    if not csv_files:
        print(f"No CSV files found in any of these locations:")
        for path in possible_csv_paths:
            print(f"  - {path}")
        return 0, []
    
    total_entries = 0
    file_details = []
    
    for csv_file in csv_files:
        try:
            with open(csv_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                file_count = 0
                hidden_count = 0
                favorite_count = 0
                
                for row in reader:
                    img_name = row.get('imgName', '').strip()
                    hidden = row.get('hidden', '').strip()
                    favorite = row.get('favorite', '').strip()
                    
                    if img_name:
                        file_count += 1
                        if hidden == '1' or hidden.lower() == 'yes':
                            hidden_count += 1
                        if favorite == '1' or favorite.lower() == 'yes':
                            favorite_count += 1
                
                total_entries += file_count
                file_details.append({
                    'file': csv_file.name,
                    'entries': file_count,
                    'hidden': hidden_count,
                    'favorites': favorite_count
                })
                
        except Exception as e:
            print(f"Error reading {csv_file.name}: {e}")
    
    return total_entries, file_details

def verify_sorting(source_dir, sorted_dir, hidden_dir):
    """Verify that all files from CSV are present in sorted directories"""
    
    source_path = Path(source_dir)
    sorted_path = Path(sorted_dir)
    hidden_path = Path(hidden_dir)
    
    # Check if there's an intermediate directory for CSV files
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
    
    print("🔍 Photo Sorting Verification Report")
    print("=" * 50)
    
    # Count files in source directory
    print(f"\n📁 Source Directory: {source_path}")
    source_media_count = count_media_files(source_path)
    print(f"Media files found: {source_media_count}")
    
    # Count CSV entries
    print(f"\n📊 CSV Analysis: {csv_path}")
    csv_total, csv_details = count_csv_entries(csv_path)
    print(f"Total CSV entries: {csv_total}")
    print(f"CSV files processed: {len(csv_details)}")
    
    for detail in csv_details:
        print(f"  - {detail['file']}: {detail['entries']} entries ({detail['hidden']} hidden, {detail['favorites']} favorites)")
    
    # Count files in sorted directories
    print(f"\n📂 Sorted Directory: {sorted_path}")
    sorted_media_count = count_media_files(sorted_path)
    print(f"Media files in sorted directory: {sorted_media_count}")
    
    print(f"\n📂 Hidden Directory: {hidden_path}")
    hidden_media_count = count_media_files(hidden_path)
    print(f"Media files in hidden directory: {hidden_media_count}")
    
    # Summary
    total_sorted_files = sorted_media_count + hidden_media_count
    print(f"\n📋 Summary:")
    print(f"  Source media files: {source_media_count}")
    print(f"  CSV entries: {csv_total}")
    print(f"  Total sorted files: {total_sorted_files}")
    print(f"    - Sorted: {sorted_media_count}")
    print(f"    - Hidden: {hidden_media_count}")
    
    # Verification results
    print(f"\n✅ Verification Results:")
    
    success = True
    
    if source_media_count != csv_total:
        print(f"  ❌ Mismatch: Source files ({source_media_count}) != CSV entries ({csv_total})")
        success = False
    else:
        print(f"  ✅ Source files match CSV entries")
    
    if total_sorted_files != csv_total:
        print(f"  ❌ Mismatch: Sorted files ({total_sorted_files}) != CSV entries ({csv_total})")
        success = False
    else:
        print(f"  ✅ All CSV entries found in sorted directories")
    
    if success:
        print(f"\n🎉 VERIFICATION SUCCESSFUL! All files properly sorted.")
    else:
        print(f"\n⚠️  VERIFICATION FAILED! Some files may be missing.")
    
    return success

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 4:
        print("Usage: python verify_sorting.py <source_directory> <sorted_directory> <hidden_directory>")
        print("Example: python verify_sorting.py /path/to/iCloud_Photos /path/to/SortedPhotos /path/to/HiddenPhotos")
        sys.exit(1)
    
    source_dir = sys.argv[1]
    sorted_dir = sys.argv[2]
    hidden_dir = sys.argv[3]
    
    if not os.path.exists(source_dir):
        print(f"❌ Source directory does not exist: {source_dir}")
        sys.exit(1)
    
    verify_sorting(source_dir, sorted_dir, hidden_dir)
