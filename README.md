# Photo Sorter

Automated photo sorting tool for iCloud Photo exports. Organizes photos and videos based on CSV metadata into structured directories.

## Features

- **Automatic Sorting**: Organizes photos by date (year/month) and favorites
- **Hidden Photos Handling**: Separates hidden photos into dedicated folder
- **Verification**: Ensures all files are properly sorted and accounted for
- **Batch Processing**: Processes multiple zip files automatically
- **Date-based Organization**: Creates year/month subdirectories based on creation dates

## Files

- `photo_sorter.py` - Core sorting logic
- `verify_sorting.py` - Verification and reporting tool
- `auto_photo_sorter.py` - Main automation script
- `test_verification.py` - Original verification script (legacy)

## Usage

### Quick Start (Recommended)

Process all zip files in a directory:

```bash
python3 auto_photo_sorter.py /path/to/zip/files
```

Or specify custom output directory:

```bash
python3 auto_photo_sorter.py /path/to/zip/files /custom/output/path
```

This will:
1. Extract all zip files
2. Sort photos based on CSV metadata
3. Verify the sorting process
4. Create organized output in `PhotoSorter_Output/`

### Manual Processing

#### Step 1: Extract Zip File

```bash
UNZIP_DISABLE_ZIPBOMB_DETECTION=TRUE unzip "iCloud Photos Part 1 of 23.zip"
```

#### Step 2: Sort Photos

```bash
python3 photo_sorter.py <extracted_directory> <output_directory>
```

Example:
```bash
python3 photo_sorter.py ./iCloud_Photos_Part_1 ./sorted_output
```

#### Step 3: Verify Sorting

```bash
python3 verify_sorting.py <source_directory> <sorted_directory> <hidden_directory>
```

Example:
```bash
python3 verify_sorting.py ./iCloud_Photos_Part_1 ./sorted_output/SortedPhotos ./sorted_output/HiddenPhotos
```

## Output Structure

```
output_directory/
├── SortedPhotos/
│   ├── Screenshots/          # All .png files
│   ├── Misc/                 # All .jpg/.jpeg files
│   ├── 2023/
│   │   ├── 12-December/
│   │   │   ├── Favorites/    # If marked as favorite
│   │   │   └── *.mov, *.heic, etc.
│   │   └── 11-November/
│   ├── 2022/
│   │   └── ...
│   ├── Unknown Date/
│   │   └── *.mov, *.heic, etc.  # Files with unparseable dates
│   └── ...
├── HiddenPhotos/
│   └── *.jpg, *.mov, etc.  # Hidden files
└── ...
```

**Special Folder Rules:**
- **Screenshots/**: All `.png` files (no date subfolders)
- **Misc/**: All `.jpg` and `.jpeg` files (no date subfolders)
- **Date folders**: All other file types (.mov, .heic, .mp4, etc.) organized by year/month

## CSV Format

The script reads CSV files with the following structure:

```csv
imgName,fileChecksum,favorite,hidden,deleted,originalCreationDate,viewCount,importDate
IMG_2440.MOV,AcY77dui2utS3bfYNqNwPXvOHvkM,no,no,no,"Saturday December 9,2023 7:48 PM GMT",0,"Saturday December 9,2023 7:49 PM GMT"
```

- `imgName`: Filename of the media
- `favorite`: "yes"/"1" or "no"/"0" - creates Favorites subdirectory
- `hidden`: "yes"/"1" or "no"/"0" - moves to HiddenPhotos folder
- `originalCreationDate`: Used for date-based organization

## Requirements

- Python 3.6+
- `unzip` command-line tool
- Sufficient disk space for extracted and sorted files

## Error Handling

The scripts include comprehensive error handling:
- Missing files are reported but don't stop processing
- CSV parsing errors are logged
- Verification reports mismatches between source and sorted files
- Failed zip extractions are clearly indicated

## Examples

### Process Multiple iCloud Photo Parts

```bash
# Assuming you have multiple parts in a directory
python3 auto_photo_sorter.py ./iCloud_Photo_Parts
```

This will create:
```
iCloud_Photo_Parts/PhotoSorter_Output/
├── extracted_iCloud_Photos_Part_1/
├── sorted_iCloud_Photos_Part_1/
├── extracted_iCloud_Photos_Part_2/
├── sorted_iCloud_Photos_Part_2/
└── ...
```

### Manual Single File Processing

```bash
# Extract
UNZIP_DISABLE_ZIPBOMB_DETECTION=TRUE unzip "iCloud Photos Part 1 of 23.zip"

# Sort
python3 photo_sorter.py "./iCloud Photos Part 1 of 23" "./sorted_photos"

# Verify
python3 verify_sorting.py "./iCloud Photos Part 1 of 23" "./sorted_photos/SortedPhotos" "./sorted_photos/HiddenPhotos"
```

## Troubleshooting

### "File not found" errors
- Check that the media files exist in the extracted directory
- Verify the CSV files are in the `Photos/` subdirectory
- Some files might be in subdirectories - the script searches recursively

### Date parsing errors
- Files with unparseable dates go to "Unknown Date" folder
- Check the CSV date format matches: "Month Day,Year Hour:Minute AM/PM GMT"

### Permission errors
- Ensure write permissions in the output directory
- Check that the unzip command has permission to create directories

## Performance Notes

- Large photo libraries (10,000+ files) may take several minutes to process
- Disk space usage: ~2x the original size (extracted + sorted copies)
- Memory usage is minimal as files are processed sequentially
