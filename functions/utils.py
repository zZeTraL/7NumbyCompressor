import os
import pandas as pd
from PIL import Image


def convert_size(size_bytes):
    if size_bytes == 0:
        return "0 B"
    units = ["B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"]
    i = 0
    while size_bytes >= 1024 and i < len(units) - 1:
        size_bytes /= 1024.0
        i += 1
    return f"{round(size_bytes, 2)} {units[i]}"


def get_files(input_folder):
    # Retrieve every file in the input_folder
    files_name = os.listdir(input_folder)
    files_path = []
    for name in files_name:
        files_path.append(os.path.join(input_folder, name).replace("\\", "/"))
    return files_name, files_path


def get_files_to_compress(input_folder, history):
    files_name, files_path = get_files(input_folder)
    files_to_compress = []
    files_already_compressed = []

    print(f"[INFO] Files in the input folder: {len(files_path)}")

    for path in files_path:
        # Check if the file is already compressed
        if path in history["path"].values:
            files_already_compressed.append(path)
        else:
            files_to_compress.append(path)

    print(f"[INFO] Files already compressed: {len(files_path) - len(files_to_compress)}")
    # DEBUG
    # for path in files_already_compressed:
    # print(f"{os.path.basename(path)}")
    print(f"[INFO] Files to compress: {len(files_to_compress)}")
    # DEBUG
    # for path in files_to_compress:
    # print(f"{os.path.basename(path)}")
    return files_to_compress


def get_folder_size(folder_path):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(folder_path):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            total_size += os.path.getsize(file_path)
    return total_size
