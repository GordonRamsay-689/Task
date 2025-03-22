import sys
import json

MAX_TITLE_LENGTH = 38

MAX_RESOURCES_TO_DISPLAY = 2

COMPLETED_SYMBOL = 'x'
UNCOMPLETED_SYMBOL = '-'

ADD = "add"
RM = "remove"
CLEAR = "clear"
EDIT = "edit"
LIST = "list"

FUNCTIONS = [ADD, RM, CLEAR, EDIT, LIST]

task = {"completed": False, "title": "", "comment": "", "description": "", "resources": []}

tasks = []

with open("table.json", "r") as table_file:
    table = json.loads(table_file.read())

def difference(i, indent, section_title):
    return (indent - 2 - len(f"{section_title[i]}"))

def display_table():
    for i, task in enumerate(table):
        status = COMPLETED_SYMBOL if task["completed"] else UNCOMPLETED_SYMBOL
        comment = task["comment"]
        resources = task["resources"]
        title = task["title"]

        title_length = len(title)
        if title_length > MAX_TITLE_LENGTH:
            title = title[:MAX_TITLE_LENGTH] + '...'

        print(f"{i+1}: |{status}|\t{title}")
        
        if comment or resources:
            separator = '_' * 18
            print(f"\t{separator}")
            section_title = ["", ""]

            comment_str = ''

            if comment:
                section_title[0] = "Comment"

            if resources:
                section_title[1] = "Long"

            indent = indent = max(len(title) for title in section_title) + 2  # + 2 represent ': '
            
            if comment:
                diff = difference(0, indent, section_title)
                print(f"\t{section_title[0]}: {' ' * diff}{comment}")

            if resources:
                n = len(resources)
                diff = difference(1, indent, section_title)

                for i in range(0, MAX_RESOURCES_TO_DISPLAY):
                    if i >= n:
                        break

                    print("\t", end='')
                    if i == 0:
                        print(f"{section_title[1]}: {' ' * diff}", end='')
                    else:
                        print(f"{' ' * indent}", end='')

                    print(f"{resources[i]}")

                if n > MAX_RESOURCES_TO_DISPLAY:
                    print(f"\t{' ' * indent}{n - MAX_RESOURCES_TO_DISPLAY} more resources.")

def parse_args(argv):
    # not implemented
    return argv[0]

if __name__ == '__main__':
    argv = sys.argv[1:]
    argc = len(argv)

    if (argc == 0):
        display_table()
        sys.exit()
    
    task["title"] = parse_args(argv)

    tasks.append(task)

    for task in tasks:
        if len(table) >= 10:
            print("Table is full. Unable to add new task.")
            break

        table.append(task)

    table_json = json.dumps(table, ensure_ascii=False)

    with open("table.json", "w") as table_file:
        table_file.write(table_json)