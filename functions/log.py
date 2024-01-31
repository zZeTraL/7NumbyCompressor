import os
import pandas as pd


def load_log():
    if os.path.exists("./log.csv"):
        return pd.DataFrame(pd.read_csv("./log.csv"))
    else:
        return pd.DataFrame(columns=["path", "is_compressed", "compression_level"])


def save_log(log):
    log.to_csv("./log.csv", index=False)


def update_log(log, path, is_compressed, compression_level):
    log.loc[len(log)] = [path, is_compressed, compression_level]
    return log


def create_compress_report():
    return pd.DataFrame(columns=["input_path", "name", "original_size", "compressed_size", "saved_storage", "percent",
                                 "output_path"])


def save_compress_report(df):
    date = pd.Timestamp.now().strftime("%Y-%m-%d_%H-%M-%S")
    df.to_csv(f"compression_report_{date}.csv", index=False)