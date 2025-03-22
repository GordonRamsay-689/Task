import sys
import json

task = {"completed": False, "title": "", "description": "", "resources": []}

tasks = []

with open("table.json", "r") as table_file:
    table = json.loads(table_file.read())

def parse_args():
    args = sys.argv[1:]

    return args[0]

if __name__ == '__main__':
    if (len(sys.argv) < 2):
        sys.exit()

    task["title"] = parse_args()
    
    tasks.append(task)

    for task in tasks:
        if len(table) >= 10:
            print("Table is full")
            break

        table.append(task)

    table_json = json.dumps(table, ensure_ascii=False)

    with open("table.json", "w") as table_file:
        table_file.write(table_json)