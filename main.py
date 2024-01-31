import os
import shutil

import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
from tqdm import tqdm

# Constants
THREAD_NUMBER = 6
BATCH_SIZE = 16
START_KEYWORD = "StarRailRes"


def convert_size(size_bytes):
    if size_bytes == 0:
        return "0B"
    units = ["B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"]
    i = 0
    while size_bytes >= 1024 and i < len(units) - 1:
        size_bytes /= 1024.0
        i += 1
    return f"{round(size_bytes, 2)} {units[i]}"


def compress(file_path, output_path, quality):
    image = Image.open(file_path)
    original_size = os.path.getsize(file_path)
    image.save(output_path, optimize=True, quality=quality)
    compressed_size = os.path.getsize(output_path)
    storage_saved = original_size - compressed_size
    percent = str(round((storage_saved / original_size) * 100, 2)) + "%"

    return original_size, compressed_size, storage_saved, percent


def get_files_to_compress(input_folder, log):
    files_to_compress = []
    for root, dirs, files in os.walk(input_folder):
        for file in files:
            path = os.path.join(root, file).replace("\\", "/")
            if path not in log["path"].values:
                files_to_compress.append(path)
    return files_to_compress


def process_batch(batch, current_dir, output_folder, quality, df, log):
    with ThreadPoolExecutor(max_workers=THREAD_NUMBER) as executor:
        futures = []
        for path in batch:
            file_name = path[path.rfind("/") + 1:]
            output_file = os.path.join(output_folder, file_name).replace("\\", "/")

            future = executor.submit(compress, path, output_file, quality)
            futures.append((path, future))

        for path, future in futures:
            original_size, compressed_size, storage_saved, percent = future.result()
            df.loc[len(df)] = [current_dir, file_name,
                               convert_size(original_size),
                               convert_size(compressed_size),
                               convert_size(storage_saved),
                               percent,
                               path]
            log.loc[len(log)] = [path]


def main(input_folder, output_folder, quality=80, overwrite=False):

    if not os.path.exists("log.csv"):
        pd.DataFrame(columns=["path"]).to_csv("log.csv", index=False)

    if not overwrite:
        if os.path.exists(output_folder):
            shutil.rmtree(output_folder)
            os.mkdir(output_folder)
        else:
            os.mkdir(output_folder)
    else:
        output_folder = input_folder;

    log = pd.DataFrame(pd.read_csv("log.csv"))
    df = pd.DataFrame(columns=["folder", "file_name", "original_size", "compressed_size", "storage_saved", "percent", "path"])

    files_to_compress = get_files_to_compress(input_folder, log)

    if not files_to_compress:
        print("[INFO] No files to compress")
        return

    print(f"[INFO] Already compressed files: {len(log)}")
    print(f"[INFO] Files to compress: {len(files_to_compress)}")

    current_dir = input_folder[input_folder.rfind(START_KEYWORD):]
    batched_files = [files_to_compress[i:i + BATCH_SIZE] for i in range(0, len(files_to_compress), BATCH_SIZE)]

    print("[INFO] Compressing files...")
    for batch in tqdm(batched_files, desc="Batch progression"):
        process_batch(batch, current_dir, output_folder, quality, df, log)

    print("[INFO] Saving report...")
    log.to_csv("log.csv", index=False)
    date = pd.Timestamp.now().strftime("%Y-%m-%d_%H-%M-%S")
    df.to_csv(f"compression_report_{date}.csv", index=False)
    print("[INFO] Operation done")
    print(f"[INFO] Total compressed files: {len(df)}")


# Example usage
input_directory = "D:/WebstormProjects/7Numby/client/public/StarRailRes/image/character_portrait"
main("input", "output", 50, True)
