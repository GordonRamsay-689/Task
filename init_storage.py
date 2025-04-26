import json
import copy
from globals import *

# IDs are in base 36, hence strings
storage = {
    "active": "0",
    "groups": {"0": ["0"]},
    "tasks": {"0": copy.deepcopy(TASKD_TEMPLATE)} 
}

with open("storage.json", "w") as f:
    f.write(json.dumps(storage, ensure_ascii=False))

with open("storage.json", "r") as f:
    written = json.loads(f.read())

    if written == storage:
        print("Succesfully dumped to file: ")
    else:
        print("Expected:", storage)
        print("Actual:", written)
        print("Failed to dump or read dumped file")