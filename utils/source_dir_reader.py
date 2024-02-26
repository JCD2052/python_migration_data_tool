import os


def get_file_path_from_sources(filename: str) -> str:
    return os.path.abspath(os.path.join(os.path.dirname(__file__), f'../src/{filename}'))
