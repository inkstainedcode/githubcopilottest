import os

# Try to import mutagen for MP3 metadata extraction; handle missing library gracefully
try:
    from mutagen.id3 import ID3
    from mutagen.mp3 import MP3  # Add this import
except ImportError:
    ID3 = None
    MP3 = None

# Try to import PyYAML for YAML output; handle missing library gracefully
try:
    import yaml
except ImportError:
    yaml = None

# Function to get all mp3 files in the 'audio' directory (default)
def get_mp3_files(directory='audio'):
    """
    Returns a list of mp3 files in the specified directory.

    :param directory: Directory to search for mp3 files.
    :return: List of dicts with 'path', 'filename', and 'size' keys.
    """
    mp3_files = []
    if os.path.exists(directory):
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            # Only include files that are .mp3
            if os.path.isfile(file_path) and filename.lower().endswith('.mp3'):
                size = os.path.getsize(file_path)
                mp3_files.append({
                    'path': file_path,              # Full path to the file
                    'filename': f'/audio/{filename}', # Relative path for output
                    'size': size                   # File size in bytes
                })
    return mp3_files

# Helper function to format seconds as HH:MM:SS
def format_duration(seconds):
    """Format seconds as HH:MM:SS string."""
    if seconds is None:
        return None
    seconds = int(seconds)
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours:02}:{minutes:02}:{secs:02}"

# Function to extract title, comments, and duration from an mp3 file's ID3 tags
def get_title_and_comments(mp3_file):
    """
    Reads the title, comments, and duration fields from an mp3 file's ID3 tags.

    :param mp3_file: Path to the mp3 file.
    :return: Dictionary with 'title', 'comments', and 'duration' keys.
    """
    if ID3 is None or MP3 is None:
        # If mutagen is not installed, return error info
        return {'file': mp3_file, 'title': None, 'comments': None, 'duration': None, 'error': 'mutagen not installed'}
    try:
        audio = ID3(mp3_file)         # Read ID3 tags
        mp3_audio = MP3(mp3_file)     # Read MP3 info (duration)
        title = audio.get('TIT2')     # Get title tag
        # Get all comment frames, extract text from first if available
        comments_frames = audio.getall('COMM')
        comments = comments_frames[0].text[0] if comments_frames and comments_frames[0].text else None
        duration = mp3_audio.info.length if mp3_audio and mp3_audio.info else None
        return {
            'title': str(title.text[0]) if title and title.text else None,      # Song title
            'description': str(comments) if comments else None,                 # Comments/description
            'duration': format_duration(duration)                               # Duration as HH:MM:SS
        }
    except Exception as e:
        # If any error occurs, return error info
        return {'file': mp3_file, 'title': None, 'comments': None, 'duration': None, 'error': str(e)}

# Main logic: gather mp3 info and write to YAML
mp3_files = get_mp3_files()  # Get list of mp3 files
results = []
for mp3_info in mp3_files:
    fields = get_title_and_comments(mp3_info['path'])  # Extract metadata
    fields['file'] = mp3_info['filename']              # Add relative filename
    fields['length'] = "{:,}".format(mp3_info['size']) # Format size with commas
    results.append(fields)

# Write results to YAML if PyYAML is available, else print warning
if yaml is not None:
    with open("episodes.yml", "w", encoding="utf-8") as f:
        yaml.dump(results, f, allow_unicode=True, sort_keys=False)
    print("YAML written to episodes.yml")
else:
    print("PyYAML is not installed. Please install it with 'pip install pyyaml'.")