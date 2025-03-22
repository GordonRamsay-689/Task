import json

table = []

with open("table.json", "w") as table_file:
    table_file.write(json.dumps(table, ensure_ascii=False))
    