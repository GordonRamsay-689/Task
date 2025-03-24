import json

# Local imports
from globals import *

table = {TBL_KEY_NAME: "", TBL_KEY_CONTENTS: []}

with open("table.json", "w") as table_file:
    table_file.write(json.dumps(table[TBL_KEY_CONTENTS], ensure_ascii=False))
    