#!/usr/bin/env python3

import os
import shutil

def clean_project_tree(root='.'):
    exts_to_delete = {'.pyd', '.so', '.pyc'}
    dirs_to_delete = {'__pycache__'}

    removed_files = 0
    removed_dirs = 0

    for dirpath, dirnames, filenames in os.walk(root, topdown=False):
        # Delete files
        for filename in filenames:
            ext = os.path.splitext(filename)[1]
            if ext in exts_to_delete:
                filepath = os.path.join(dirpath, filename)
                try:
                    os.remove(filepath)
                    removed_files += 1
                    print(f"Deleted file: {filepath}")
                except Exception as e:
                    print(f"Failed to delete {filepath}: {e}")

        # Delete __pycache__ directories
        for dirname in dirnames:
            if dirname in dirs_to_delete:
                dir_to_remove = os.path.join(dirpath, dirname)
                try:
                    shutil.rmtree(dir_to_remove)
                    removed_dirs += 1
                    print(f"Deleted directory: {dir_to_remove}")
                except Exception as e:
                    print(f"Failed to delete {dir_to_remove}: {e}")

    print(f"\n✅ Removed {removed_files} files and {removed_dirs} directories.")

if __name__ == "__main__":
    clean_project_tree()
