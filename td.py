import sys
import copy
import json

# Local imports
from globals import * 
from task import Task

def add(options):
    task = Task(title=options[OPT_TITLE], 
                resources=options[OPT_RESOURCES])

    if len(table[TBL_CONTENTS]) >= 10:
        print(f"Table is full. Unable to add new task: {task._title}")
        sys.exit()

    table[TBL_CONTENTS].append(task)

    write_tasks()

def display_table(options):
    if not table[TBL_CONTENTS]:
        print("Table is empty.")
    else:
        display_tasks(table[TBL_CONTENTS], 
                      detailed=options[OPT_DETAILED])
    
def display_tasks(lst, detailed=False):
    for i, task in enumerate(lst):
        index = f"{i+1}:"
        print(f"{index:4}", end='')

        if detailed:
            print(task.summarize(), end='')   
        else:
            print(task)

def execute(fn, options):
    if fn == FN_ADD:
        if any(options[key] for key in options.keys()):
            add(options)
        else:
            print("Nothing to add. Add requires arguments")
            sys.exit()
    elif fn == FN_REMOVE:
        if any(options[key] for key in options.keys()):
            remove(options)
        else:
            print("Nothing to add. Add requires arguments")
            sys.exit()
    elif fn == FN_LIST:
        display_table(options)
        sys.exit()
    elif fn == FN_CLEAR:
        clear()
        sys.exit()

def remove(options):
    if options[OPT_ID]:
        if (options[OPT_ID] < 1):
            print("Invalid ID provided.")
            return

        for task in table[TBL_CONTENTS]:
            if task._id.lower() == options[OPT_ID].lower():
                table[TBL_CONTENTS].remove(task)
                write_tasks()
                return
        print(f"Could not locate a task on table with ID: '{options[OPT_ID]}'")
    elif options[OPT_TITLE]:
        matches = []

        for i, task in enumerate(table[TBL_CONTENTS]):
            if task._title == options[OPT_TITLE]:
                matches.append(task)

        if not matches:
            print(f"Could not locate a task on table with title: '{options[OPT_TITLE]}'")
            return
        
        if len(matches) > 1:
            print("Several tasks match provdided title. Select one to remove by index:" )
            display_tasks(matches, detailed=True)
            print(f"Select index in range 1-{len(matches)}.")

            # todo: function get_int(), and function get_index()
            i = int(input("> "))
            i -= 1
            # todo: if i valid range
        else:
            i = 0

        table[TBL_CONTENTS].remove(matches[i])
        write_tasks()

def import_table(filename, local):
    with open(filename, "r") as f:
        imported = json.loads(f.read())

        local[TBL_NAME] = imported[TBL_NAME]

        for d in imported[TBL_CONTENTS]:
            local[TBL_CONTENTS].append(Task(taskd=d))

def clear():
    table = TABLE.copy()

    with open("table.json", "w") as table_file:
        table_file.write(json.dumps(table, ensure_ascii=False))

def init_options(fn):
    return copy.deepcopy(FUNCTIONS[fn])

def is_keyword(x):
    return x in OPTION_ALIASES.keys() or x in FUNCTIONS.keys()

def parse_args(args):    
    queue = []
    
    if len(args) == 0:
        fn = FN_LIST
    else:
        fn = args.pop(0)
        if fn not in FUNCTIONS.keys(): 
            print(f"Not a valid function: {fn}")
            sys.exit()
            
    options = init_options(fn)

    while args:
        arg = args.pop(0)

        if arg in FUNCTIONS.keys():
            print(f"Already provided function: {fn}")
            sys.exit()

        if arg in OPTION_ALIASES.keys() and OPTION_ALIASES[arg] in FUNCTIONS[fn].keys():
            opt = OPTION_ALIASES[arg]

            # Denotes new task
            if opt in [OPT_TITLE, OPT_ID] and options[opt]:
                queue.append(options)
                options = init_options(fn)

            if isinstance(options[opt], bool):
                options[opt] = True
            else:
                parse_opt_args(args, options, opt)
        elif arg.startswith('-'):
            print(f"Invalid option '{arg}' for function '{fn}'.")
            sys.exit()
        else: # Positionals
            if fn == FN_ADD:
                if options[OPT_TITLE]:
                    print("USAGE: ")
                    sys.exit()

                options[OPT_TITLE] = arg
                continue

    queue.append(options)

    return fn, queue

def parse_opt_args(args, options, opt):
    while args and not is_keyword(args[0]):  
        arg = args.pop(0)       

        if isinstance(options[opt], int):
            if not arg.isdigit():
                print(f"Option '-{opt}' requires a numerical value as argument, not '{arg}'.")
                sys.exit()

            options[opt] = int(arg)
            return
        elif isinstance(options[opt], str):
            options[opt] = arg
            return

        options[opt].append(arg)

    if not options[opt]:
        print(f"Failed to parse args for option: '-{opt}'")

        if len(args) == 0:
            print(f"Option '-{opt}' requires at lest one argument.")
        elif is_keyword(args[0]):
            print(f"Option '-{opt}' cannot take keywords as arguemnts: '{args[0]}'")
        sys.exit() 

def write_tasks():
    wtable = copy.deepcopy(TABLE)
    for task in table[TBL_CONTENTS]:
        wtable[TBL_CONTENTS].append(task.write_dict())

    with open("table.json", "w") as f:
        f.write(json.dumps(wtable, ensure_ascii=False))

if __name__ == '__main__':
    table = copy.deepcopy(TABLE)

    try:
        import_table(filename="table.json", local=table)
    except (KeyError, FileNotFoundError):
        print("File is not a valid table.")
        sys.exit()
    
    fn, queue = parse_args(sys.argv[1:])
    
    for options in queue:
        execute(fn, options)
