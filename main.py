import os

def get_script_dir():
    return os.path.abspath(__file__).strip('(main.py')