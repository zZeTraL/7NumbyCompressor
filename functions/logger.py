import os
import pandas as pd


def load_history():
    if os.path.exists("./history.csv"):
        return pd.DataFrame(pd.read_csv("./history.csv"))
    else:
        return pd.DataFrame(columns=["path", "is_compressed", "compression_level"])


def save_history(log):
    log.to_csv("./history.csv", index=False)


def update_history(log, path, is_compressed, compression_level):
    log.loc[len(log)] = [path, is_compressed, compression_level]
    return log


def create_compress_report():
    return pd.DataFrame(columns=["input_path", "name", "original_size", "compressed_size", "saved_storage", "percent",
                                 "output_path"])


def save_compress_report(df):
    date = pd.Timestamp.now().strftime("%Y-%m-%d_%H-%M-%S")
    df.to_csv(f"compression_report_{date}.csv", index=False)


def log_open():
    # if log.txt exists, open it and read the content
    # if log.txt doesn't exist, create it
    # return the content
    if os.path.exists("./log.txt"):
        with open("./log.txt", "r") as f:
            return f.read()
    else:
        with open("./log.txt", "w") as f:
            f.write("")
        return ""


def log_write(content):
    # open log.txt in append mode
    # write the content
    with open("./log.txt", "a") as f:
        f.write(content)
