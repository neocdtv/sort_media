import argparse
import os
import re
import shutil
from datetime import datetime
import exifread

def is_whatsapp(filename):
    """Check if the filename matches typical WhatsApp naming conventions."""
    return bool(re.search(r'(-WA|\bwhatsapp\b)', filename, re.IGNORECASE))

def extract_date_from_filename(filename):
    """Extract date from filename if EXIF metadata is missing (common for WhatsApp images/videos)."""
    match = re.search(r'(?:VID|IMG)-(\d{4})(\d{2})(\d{2})-WA', filename, re.IGNORECASE)
    if match:
        return f"{match.group(1)}-{match.group(2)}-{match.group(3)}"

    match_alt = re.search(r'(\d{4}-\d{2}-\d{2})', filename)
    if match_alt:
        return match_alt.group(1)

    return None

def get_file_date_from_mtime(file_path):
    """Fallback to file modification time if no EXIF or filename date is found."""
    try:
        mtime = os.path.getmtime(file_path)
        parsed_date = datetime.fromtimestamp(mtime)
        return parsed_date.strftime("%Y-%m"), parsed_date.strftime("%Y-%m-%d")
    except Exception as e:
        print(f"Could not read file modification time for {file_path}: {e}")
    return None, None

def get_media_info(file_path, filename):
    """Extract dates and determine if the file is from WhatsApp for JPG/JPEG and MP4 files."""
    whatsapp_flag = is_whatsapp(filename)
    year_month, full_date = None, None
    ext = filename.lower()

    # 1. Try reading EXIF metadata for JPG/JPEG files
    if ext.endswith(('.jpg', '.jpeg')):
        try:
            with open(file_path, 'rb') as img_file:
                tags = exifread.process_file(img_file, stop_tag='EXIF DateTimeOriginal', details=False)
                date_tag = tags.get('EXIF DateTimeOriginal') or tags.get('Image DateTime')
                
                if date_tag:
                    date_str = str(date_tag).split()[0]
                    parsed_date = datetime.strptime(date_str, "%Y:%m:%d")
                    year_month = parsed_date.strftime("%Y-%m")
                    full_date = parsed_date.strftime("%Y-%m-%d")
        except Exception as e:
            print(f"Could not read EXIF metadata for {file_path}: {e}")

    # 2. If date is still missing, try extracting from filename (especially for WhatsApp)
    if not full_date:
        fallback_date_str = extract_date_from_filename(filename)
        if fallback_date_str:
            try:
                parsed_date = datetime.strptime(fallback_date_str, "%Y-%m-%d")
                year_month = parsed_date.strftime("%Y-%m")
                full_date = parsed_date.strftime("%Y-%m-%d")
            except ValueError:
                pass

    # 3. Final fallback to file modification time so no file goes to 'no_date' if system time exists
    if not full_date:
        year_month, full_date = get_file_date_from_mtime(file_path)

    return year_month, full_date, whatsapp_flag

def get_unique_destination_path(target_folder, prefixed_filename):
    """Generate a non-conflicting path by appending _1, _2, etc. if file exists."""
    dest_path = os.path.join(target_folder, prefixed_filename)
    if not os.path.exists(dest_path):
        return dest_path

    base_name, ext = os.path.splitext(prefixed_filename)
    counter = 1

    while True:
        new_filename = f"{base_name}_{counter}{ext}"
        new_dest_path = os.path.join(target_folder, new_filename)
        if not os.path.exists(new_dest_path):
            return new_dest_path
        counter += 1

def str_to_bool(v):
    """Convert string command line arguments to boolean values."""
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected (true/false).')

def organize_media(source_directory, output_directory=None, copy_files=True):
    source_directory = os.path.abspath(source_directory)
    
    if output_directory:
        output_directory = os.path.abspath(output_directory)
    else:
        output_directory = source_directory

    if not os.path.exists(source_directory):
        print(f"Error: Source directory '{source_directory}' does not exist.")
        return

    action_label = "Copying" if copy_files else "Moving"
    print(f"Scanning directory tree starting at: {source_directory} ({action_label} files)\n")

    for root, dirs, files in os.walk(source_directory):
        if output_directory == source_directory:
            rel_path = os.path.relpath(root, source_directory)
            if rel_path != '.':
                top_folder = rel_path.split(os.sep)[0]
                if top_folder == 'no_date' or (len(top_folder) == 7 and top_folder.count('-') == 1):
                    continue

        for filename in files:
            if not filename.lower().endswith(('.jpg', '.jpeg', '.mp4')):
                continue

            file_path = os.path.join(root, filename)
            year_month, full_date, whatsapp_flag = get_media_info(file_path, filename)
            
            if year_month:
                folder_name = os.path.join(year_month, 'whatsapp') if whatsapp_flag else year_month
            else:
                folder_name = os.path.join('no_date', 'whatsapp') if whatsapp_flag else 'no_date'

            target_folder = os.path.join(output_directory, folder_name)

            if not os.path.exists(target_folder):
                os.makedirs(target_folder)

            prefix = full_date if full_date else 'no_date'
            prefixed_filename = f"{prefix}_{filename}"

            dest_path = get_unique_destination_path(target_folder, prefixed_filename)
            
            if copy_files:
                shutil.copy2(file_path, dest_path)
                action_text = "Copied"
            else:
                shutil.move(file_path, dest_path)
                action_text = "Moved"

            final_filename = os.path.basename(dest_path)
            rel_src = os.path.relpath(file_path, source_directory)
            print(f"{action_text}: {rel_src} -> {folder_name}/{final_filename}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Recursively scan JPG and MP4 media, prefix filenames with dates, sort into YYYY-MM monthly folders, and separate WhatsApp items."
    )
    parser.add_argument(
        'source',
        nargs='?',
        default='.',
        help="Root path to search for media files (default: current directory)"
    )
    parser.add_argument(
        '--output', '-o',
        help="Optional separate output directory where sorted folders will be created"
    )
    parser.add_argument(
        '--copy',
        type=str_to_bool,
        default=True,
        help="Set to true to copy files, or false to move files (default: true)"
    )

    args = parser.parse_args()
    organize_media(args.source, args.output, args.copy)
