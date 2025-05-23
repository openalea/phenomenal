#!/usr/bin/env python3

from pathlib import Path
import shutil

def clean_project_tree(root='.'):
    exts_to_delete = {'.pyd', '.so', '.pyc'}
    dirs_to_delete = {'__pycache__'}

    removed_files = 0
    removed_dirs = 0

    root_path = Path(root)

    for path in root_path.rglob('*'):
        # Delete files with unwanted extensions
        if path.is_file() and path.suffix in exts_to_delete:
            try:
                path.unlink()
                removed_files += 1
                print(f"Deleted file: {path}")
            except Exception as e:
                print(f"Failed to delete {path}: {e}")

        # Delete __pycache__ directories (robustly)
        elif path.is_dir() and path.name in dirs_to_delete:
            try:
                shutil.rmtree(path)
                removed_dirs += 1
                print(f"Deleted directory: {path}")
            except Exception as e:
                print(f"Failed to delete {path}: {e}")

    print(f"\n✅ Removed {removed_files} files and {removed_dirs} directories.")


if __name__ == "__main__":
    clean_project_tree()
