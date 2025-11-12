#!/usr/bin/env python3

import os
import re
import sys
from pathlib import Path

# Compile regex for valid file extensions (.md, .mdx, .txt)
VALID_EXTENSIONS = re.compile(r'\.(md|mdx|txt)$', re.IGNORECASE)

def count_words_in_file(file_path):
    """Return word count for a single text file."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read()
            return len(text.split())
    except Exception as e:
        print(f"Skipping {file_path}: {e}")
        return 0

def recursive_word_count(parent_folder):
    """Recursively count words in .md, .mdx, and .txt files."""
    total_words = 0
    for root, _, files in os.walk(parent_folder):
        for name in files:
            if VALID_EXTENSIONS.search(name):
                file_path = Path(root) / name
                total_words += count_words_in_file(file_path)
    return total_words

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: wordcount.py <file_or_folder_path>")
        sys.exit(1)

    target_path = Path(sys.argv[1])

    if not target_path.exists():
        print(f"Error: Path does not exist: {target_path}")
        sys.exit(1)

    if target_path.is_file():
        # Single file mode
        if VALID_EXTENSIONS.search(target_path.name):
            total = count_words_in_file(target_path)
            print(f"Word count in {target_path}: {total}")
        else:
            print(f"Error: File must be .md, .mdx, or .txt")
            sys.exit(1)
    elif target_path.is_dir():
        # Directory mode
        total = recursive_word_count(target_path)
        print(f"Total word count in {target_path}: {total}")
    else:
        print(f"Error: Path is neither a file nor a directory: {target_path}")
        sys.exit(1)
