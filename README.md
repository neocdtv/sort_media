# Media Organizer Script

A Python utility to recursively scan, extract dates from metadata or filenames, prefix files with dates, and organize your mobile phone photos (`.jpg`, `.jpeg`) and videos (`.mp4`) into clean monthly folders. It also automatically detects and isolates WhatsApp media.

## Features

* **Recursive Scanning:** Deeply searches all nested subfolders within your source directory.
* **EXIF & Metadata Extraction:** Reads capture dates using `exifread` for images.
* **WhatsApp Detection & Separation:** Identifies WhatsApp media through naming conventions and sorts them into a dedicated `whatsapp/` subfolder inside each month's directory.
* **Smart Fallback Handling:** 
  1. Checks EXIF metadata.
  2. Parses dates from filenames (e.g., `IMG-20260115-WA...` or `VID-20260115-WA...`).
  3. Falls back to file modification time (`mtime`) so no file gets stranded in `no_date` unnecessarily.
* **Date-Prefixed Filenames:** Automatically renames files with their extracted full date (`YYYY-MM-DD_original_name`).
* **Conflict Resolution:** Safely appends incremental counters (`_1`, `_2`, etc.) if duplicate filenames appear in the same target folder.
* **Copy or Move Modes:** Toggle between copying files (default) or moving them via a command-line flag.

---

## Installation & Setup

1. **Clone or download** the script (`sort_media.py`) into your project directory.
2. **Create and activate a virtual environment:**
   ```bash
   python3 -m venv venv
  
   source venv/bin/activate
   ```
3. **Sort (default copy):**
   ```bash
   python3 sort_media.py "/path/to/source_photos"
   ```
4. **Sort (move):**
   ```bash
   python3 sort_media.py "/path/to/source_photos" --copy false
   ```
