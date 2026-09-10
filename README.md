python3 -m venv venv

source venv/bin/activate

pip install exifread

# default will copy
python3 sort_media.py /path/to/source

# move
python3 sort_media.py /path/to/source --copy false
