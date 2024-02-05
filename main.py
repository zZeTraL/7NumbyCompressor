import shutil

import pandas as pd
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
from tqdm import tqdm
from functions.utils import *
from functions.logger import *

# Constants
THREAD_NUMBER = 6
BATCH_SIZE = 12


def compress_file(input_path, output_path, compression_level, overwrite):
    # We retrieve the name of the file
    file_name = os.path.basename(input_path)

    # We open the image and save it with the compression level to the output folder
    image = Image.open(input_path)
    image.save(output_path, optimize=True, quality=compression_level)

    # We compute the original size, the compressed size, the saved storage and the percent
    original_size = os.path.getsize(input_path)
    compressed_size = os.path.getsize(output_path)
    saved_storage = original_size - compressed_size
    percent = str(round((saved_storage / original_size) * 100, 2)) + "%"
    is_compressed = compressed_size <= original_size

    # If compressed size is greater than original size, we delete the compressed file
    if not is_compressed:
        os.remove(output_path)
        # print(f"[INFO] {file_name} was not compressed because the compressed size is greater than the original size")
        return input_path, file_name, original_size, original_size, 0, 0, None, False

    if overwrite:
        shutil.move(output_path, input_path)

    return input_path, file_name, original_size, compressed_size, saved_storage, percent, output_path if not overwrite else input_path, is_compressed


def process_batch(batch_id, batch, output_folder, compression_level, overwrite):
    with concurrent.futures.ThreadPoolExecutor(max_workers=THREAD_NUMBER) as executor:
        futures = []
        for file in batch:
            output_path = os.path.join(output_folder, os.path.basename(file)).replace("\\", "/")
            future = executor.submit(compress_file, file, output_path, compression_level, overwrite)
            futures.append(future)

        with tqdm(total=len(futures), desc=f"Compressing files... ({batch_id})", unit="files", leave=True) as pbar:
            for future in concurrent.futures.as_completed(futures):
                input_path, name, original_size, compressed_size, saved_storage, percent, output_path, is_compressed = future.result()
                df.loc[len(df)] = [input_path, name,
                                   convert_size(original_size),
                                   convert_size(compressed_size),
                                   convert_size(saved_storage),
                                   percent,
                                   output_path]
                history.loc[len(history)] = [input_path, is_compressed, compression_level]
                pbar.update(1)


def main(input_folder, output_folder, compression_level, overwrite):
    original_folder_size = convert_size(get_folder_size(input_folder))
    # Check if the output folder exists and overwrite is False
    if not os.path.exists(output_folder):
        os.mkdir(output_folder)
    # We retrieve the files to compress
    files_to_compress = get_files_to_compress(input_folder, history)
    if len(files_to_compress) == 0:
        print(f"[INFO] Operation done : No files to compress")
        return

    # We create a list of batches of files to compress
    batches = []
    for i in range(0, len(files_to_compress), BATCH_SIZE):
        batches.append(files_to_compress[i:i + BATCH_SIZE])
        print(f"[INFO] Batch {len(batches)} created with {len(batches[-1])} files")

    for batch in batches:
        batch_id = batches.index(batch) + 1
        process_batch(batch_id, batch, output_folder, compression_level, overwrite)

    compressed_folder_size = convert_size(get_folder_size(output_folder)) if not overwrite else convert_size(get_folder_size(input_folder))
    print("[INFO] Operation completed")
    print(f"[INFO] Original folder size: {original_folder_size}")
    print(f"[INFO] Compressed folder size: {compressed_folder_size}")
    print("[INFO] More details in the log file")

    # write in log the date and time of the operation and the number of files compressed
    log_write(
        "-----" * 32 +
        f"\n[{pd.Timestamp.now().strftime('%Y-%m-%d_%H-%M-%S')}]\n"
        f'\tinput_path: {input_folder}\n'
        f'\toutput_path: {output_folder}\n'
        f'\tOverwrite: {overwrite}\n'
        f"\tOriginal folder size: {original_folder_size}\n "
        f"\tCompressed folder size: {compressed_folder_size}\n "
        f"\tFiles compressed: {len(df)}\n "
        f"\tFiles not compressed: {len(files_to_compress) - len(df)}\n "
        f'\tCompression level: {compression_level}\n'
    )
    save_history(history)
    save_compress_report(df)


# Main
input_directory = "D:/WebstormProjects/StarRailRes_fork/icon/avatar"
history = load_history()
df = create_compress_report()

directories = [
    "D:/WebstormProjects/StarRailRes_fork/image/character_portrait",
    "D:/WebstormProjects/StarRailRes_fork/image/character_preview",
    "D:/WebstormProjects/StarRailRes_fork/image/light_cone_portrait",
    "D:/WebstormProjects/StarRailRes_fork/image/light_cone_preview",
    "D:/WebstormProjects/StarRailRes_fork/image/simulated_event",

    "D:/WebstormProjects/StarRailRes_fork/icon/avatar",
    "D:/WebstormProjects/StarRailRes_fork/icon/block",
    "D:/WebstormProjects/StarRailRes_fork/icon/character",
    "D:/WebstormProjects/StarRailRes_fork/icon/curio",
    "D:/WebstormProjects/StarRailRes_fork/icon/deco",
    "D:/WebstormProjects/StarRailRes_fork/icon/element",
    "D:/WebstormProjects/StarRailRes_fork/icon/item",
    "D:/WebstormProjects/StarRailRes_fork/icon/light_cone",
    "D:/WebstormProjects/StarRailRes_fork/icon/logo",
    "D:/WebstormProjects/StarRailRes_fork/icon/path",
    "D:/WebstormProjects/StarRailRes_fork/icon/property",
    "D:/WebstormProjects/StarRailRes_fork/icon/relic",
    "D:/WebstormProjects/StarRailRes_fork/icon/sign",
    "D:/WebstormProjects/StarRailRes_fork/icon/skill",
]

# process each path in the array
for directory in directories:
    print(f"[INFO] Processing {directory}")
    main(directory, "output", 80, True)
