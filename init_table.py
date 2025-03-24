import json

# Local imports
from globals import *

table = TABLE.copy()

with open("table.json", "w") as table_file:
    table_file.write(json.dumps(table, ensure_ascii=False))
    