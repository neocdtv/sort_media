from pathlib import Path
import sys

def list_file_types(directory_path):
    path = Path(directory_path)
    if not path.exists():
        print(f"Directory not found: {directory_path}")
        return
    
    extensions = set()
    for file_path in path.rglob('*'):
        if file_path.is_file():
            ext = file_path.suffix.lower()
            extensions.add(ext if ext else "[no extension]")
                
    print(f"Unique file types in '{path.resolve()}':")
    for ext in sorted(extensions):
        print(ext)

if __name__ == "__main__":
    target_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    list_file_types(target_dir)
