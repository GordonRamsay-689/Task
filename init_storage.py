import json
import copy
from globals import *

storage = {
    "active": 0,
    "groups": {0: [0]},
    "tasks": {0: copy.deepcopy(TASKD_TEMPLATE)} 
}

with open("storage.json", "w") as f:
    f.write(json.dumps(storage, ensure_ascii=False))

with open("storage.json", "r") as f:
    written = json.loads(f.read())


    # TODO: Load JSON numerical keys to int properly 
    '''
    print(written)
    print(storage)
    if written == storage:
        print("Succesfully dumped to file: ")
    else:
        print("Failed to dump or read dumped file")
    '''