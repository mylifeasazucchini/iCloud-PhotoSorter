#!/usr/bin/env python3

import os
import sys
import subprocess
import zipfile
from pathlib import Path

def extract_zip(zip_path, extract_to):
    """Extract zip file with zip bomb detection disabled and encoding handling"""
    print(f"📦 Extracting {zip_path} to {extract_to}")
    
    # Create extraction directory if it doesn't exist
    Path(extract_to).mkdir(parents=True, exist_ok=True)
    
    # Use unzip with zip bomb detection disabled and encoding options
    cmd = [
        'unzip', 
        '-o',  # overwrite existing files
        '-O', 'UTF-8',  # specify character encoding
        str(zip_path),
        '-d', str(extract_to)
    ]
    
    env = os.environ.copy()
    env['UNZIP_DISABLE_ZIPBOMB_DETECTION'] = 'TRUE'
    
    try:
        result = subprocess.run(cmd, env=env, capture_output=True, text=True, check=True)
        print(f"✅ Extraction completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Extraction failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def find_zip_files(directory):
    """Find all zip files in directory"""
    directory = Path(directory)
    zip_files = list(directory.glob("*.zip"))
    return zip_files

def run_script(script_path, *args):
    """Run a Python script and return success status"""
    cmd = ['python3', script_path] + list(args)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(result.stdout)
        if result.stderr:
            print(f"Warnings: {result.stderr}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Script failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def process_zip_file(zip_file, base_output_dir):
    """Process a single zip file: extract, sort, verify"""
    
    zip_name = zip_file.stem
    extract_dir = base_output_dir / f"extracted_{zip_name}"
    sorted_output_dir = base_output_dir / f"sorted_{zip_name}"
    
    print(f"\n{'='*60}")
    print(f"🔄 Processing: {zip_file.name}")
    print(f"{'='*60}")
    
    # Step 1: Extract zip file
    if not extract_zip(zip_file, extract_dir):
        print(f"❌ Failed to extract {zip_file.name}")
        return False
    
    # Step 2: Sort photos
    print(f"\n📋 Sorting photos...")
    if not run_script('photo_sorter.py', str(extract_dir), str(sorted_output_dir)):
        print(f"❌ Failed to sort photos from {zip_file.name}")
        return False
    
    # Step 3: Verify sorting
    print(f"\n🔍 Verifying sorting...")
    sorted_dir = sorted_output_dir / "SortedPhotos"
    hidden_dir = sorted_output_dir / "HiddenPhotos"
    
    if not run_script('verify_sorting.py', str(extract_dir), str(sorted_dir), str(hidden_dir)):
        print(f"❌ Verification failed for {zip_file.name}")
        return False
    
    print(f"\n✅ Successfully processed {zip_file.name}")
    print(f"📁 Extracted to: {extract_dir}")
    print(f"📂 Sorted to: {sorted_output_dir}")
    
    return True

def main():
    """Main automation script"""
    
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: python auto_photo_sorter.py <directory_with_zips> [output_directory]")
        print("Example: python auto_photo_sorter.py /path/to/zip_files")
        print("Example: python auto_photo_sorter.py /path/to/zip_files /custom/output/path")
        sys.exit(1)
    
    zip_directory = Path(sys.argv[1])
    
    if not zip_directory.exists():
        print(f"❌ Directory does not exist: {zip_directory}")
        sys.exit(1)
    
    # Set output directory
    if len(sys.argv) == 3:
        base_output_dir = Path(sys.argv[2])
    else:
        base_output_dir = zip_directory / "PhotoSorter_Output"
    
    # Find all zip files
    zip_files = find_zip_files(zip_directory)
    
    if not zip_files:
        print(f"❌ No zip files found in {zip_directory}")
        sys.exit(1)
    
    print(f"🔍 Found {len(zip_files)} zip files:")
    for zip_file in zip_files:
        print(f"  - {zip_file.name}")
    
    # Create base output directory
    base_output_dir.mkdir(parents=True, exist_ok=True)
    
    # Process each zip file
    successful = 0
    failed = 0
    
    for zip_file in zip_files:
        if process_zip_file(zip_file, base_output_dir):
            successful += 1
        else:
            failed += 1
    
    # Final summary
    print(f"\n{'='*60}")
    print(f"📊 PROCESSING COMPLETE")
    print(f"{'='*60}")
    print(f"Total zip files: {len(zip_files)}")
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"📁 Output directory: {base_output_dir}")
    
    if failed == 0:
        print(f"\n🎉 All files processed successfully!")
    else:
        print(f"\n⚠️  {failed} files failed to process. Check the logs above.")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
