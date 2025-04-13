import os
import re

def ensure_dir_exists(path):
    os.makedirs(path, exist_ok=True)

def parse_page_ranges(page_ranges_str, max_page=None):
    """
    Parse a string like "1-3,5,7-9" into a sorted list of 0-based page indices.
    If max_page is given, clamp indices to [0, max_page-1].
    """
    if not page_ranges_str:
        return None
    pages = set()
    for part in page_ranges_str.split(","):
        part = part.strip()
        if "-" in part:
            start, end = part.split("-")
            for i in range(int(start), int(end) + 1):
                pages.add(i - 1)
        else:
            pages.add(int(part) - 1)
    if max_page is not None:
        pages = {i for i in pages if 0 <= i < max_page}
    return sorted(pages)

def get_basename_no_ext(path):
    return os.path.splitext(os.path.basename(path))[0]

def format_exception(e):
    return f"{type(e).__name__}: {e}"