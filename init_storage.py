import json
import copy
import os
from globals import *

def init_storage(script_dir):
    # IDs are in base 36, hence strings
    storage = {
        "current_id": "0",
        "active_group": "0",
        "groups": {"0": {"task_ids": ["0"], "name": ''}},
        "tasks": {"0": copy.deepcopy(TASKD_TEMPLATE)} 
    }

    file_path = os.path.join(script_dir, "storage.json")

    with open(file_path, "w") as f:
        f.write(json.dumps(storage, ensure_ascii=False))

    with open(file_path, "r") as f:
        written = json.loads(f.read())

        if written == storage:
            print(f"Succesfully initialized storage file at '{file_path}'.")
        else:
            print("Expected:", storage)
            print("Actual:", written)
            print("Failed to dump or read dumped file")