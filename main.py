import shutil

import pandas as pd
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
from tqdm import tqdm
from functions.utils import *
from functions.log import *

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

    return input_path, file_name, original_size, compressed_size, saved_storage, percent, output_path, is_compressed


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
                log.loc[len(log)] = [input_path, is_compressed, compression_level]
                pbar.update(1)


def main(input_folder, output_folder, compression_level, overwrite):
    # Check if the output folder exists and overwrite is False
    if not os.path.exists(output_folder):
        os.mkdir(output_folder)
    # We retrieve the files to compress
    files_to_compress = get_files_to_compress(input_folder, log)
    if len(files_to_compress) == 0:
        print(f"[INFO] Operation done : No files to compress")
        return

    # We create a list of batches of files to compress
    batches = []
    for i in range(0, len(files_to_compress), BATCH_SIZE):
        batches.append(files_to_compress[i:i + BATCH_SIZE])

    for batch in batches:
        batch_id = batches.index(batch) + 1
        process_batch(batch_id, batch, output_folder, compression_level, overwrite)

    print(f"[INFO] Compression finished")
    print(f"[INFO] Files compressed: {len(df)}")
    print(f"[INFO] Files not compressed: {len(files_to_compress) - len(df)}")
    save_log(log)
    save_compress_report(df)


# Main
input_directory = "D:/WebstormProjects/7Numby/client/public/StarRailRes/image/character_preview"
log = load_log()
df = create_compress_report()
main(input_directory, "output", 70, True)