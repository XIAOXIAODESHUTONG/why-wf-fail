import os


def create_folder(path):
    is_exists = os.path.exists(path)
    if not is_exists:
        os.mkdir(path)
