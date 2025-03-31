import sys
import copy # potentially replace with just manual copying of the dict, if this has any impact at all on speed id.
import json

# Local imports
from globals import * 

class Task:
    ## While the task object is in use the self._taskd dict is not updated. this exists only for internal access.
    ## When updating a task only the object attributes are updated, until you choose to either write the task 
    ## or delete it. 

    ## For example deleting a task by title after that title has been changed from what it was upon import will 
    ## delete the task from .JSON using its Task.id. The id can never be changed under any circumstance.
    
    ## Using decorators or functions to set attribute values. getting them is not really necessary to enforce a getter
    ## as the data types are not complex.

    def __init__(self, taskd=None, status=False, title="", comment="", description="", resources=[]):
        ''' The Task object can be initialized with either an existing task dictionary (typically loaded from JSON)
        or with provided parameters if argument task_dict is not provided. If taskd is provided all other arguments
        will be ignored.

        If no task_dict and no title is provided a title will be generated.
        '''

        # Initialising _taskd ensures a key is never missed when writing to file, even if it requires default values (if changed) to be updated both in init of self._taskd and in function parameters
        self._taskd = {
            TSK_KEY_TITLE: "", 
            TSK_KEY_COMMENT: "", 
            TSK_KEY_DESCRIPTION: "", 
            TSK_KEY_RESOURCES: [], 
            TSK_KEY_ID: 0
        }

        if taskd:
            self._load_dict(taskd)
        else:
            # Do .copy() for lists?
            self._comment = comment
            self._description = description
            self._id = self.generate_task_id()
            self._resources = resources
            self._status = status
            self._title = title or self.generate_task_title()

    def _load_dict(self, taskd):
        ''' Loads an existing dictionary into Task. '''

        try:
            self._comment = taskd[TSK_KEY_COMMENT]
            self._description = taskd[TSK_KEY_DESCRIPTION]
            self._id = taskd[TSK_KEY_ID]
            self._resources = taskd[TSK_KEY_RESOURCES]
            self._status = taskd[TSK_KEY_STATUS]
            self._title = taskd[TSK_KEY_TITLE]
        except KeyError:
            print("Failed to load task, missing key-value pair. The data may have already been corrupted before attempt to load.")
            raise
        
        self._taskd = taskd
        return True
    
    def write_dict(self):
        ''' Updates the self._taskd dictionary and returns it. 

        Example usage: Writing a task to JSON
        '''

        # Example error check for attempt to write 
        if self._id == 0:
            print("No task id. Task data may be corrupted.")
            raise ValueError 

        self._taskd[TSK_KEY_COMMENT] = self._comment
        self._taskd[TSK_KEY_DESCRIPTION] = self._description
        self._taskd[TSK_KEY_ID] = self._id
        self._taskd[TSK_KEY_RESOURCES] = self._resources
        self._taskd[TSK_KEY_STATUS] = self._status
        self._taskd[TSK_KEY_TITLE] = self._title

        return self._taskd 
        
    def __str__(self, ):
        return self._get_header_str()

    def _get_header_str(self):
        ''' Format the task header row. Consists of task.title and task.status. ''' 

        status = COMPLETED_SYMBOL if self._status else UNCOMPLETED_SYMBOL
        
        title = self._title
        if len(title) > MAX_TITLE_LENGTH:
            title = title[:MAX_TITLE_LENGTH] + '...'

        return f"|{status}|\t{title} (ID: {self._id})"

    def _get_pad(self, i, indent, section_title):
        return (indent - 2 - len(f"{section_title[i]}")) # -2 represent': '

    def generate_task_id(self):
        return 1

    def summarize(self):
        # Is a hardcoded summary desireable or acceptable? Leveraging the design of the FUNCTIONS dictionary as 'parse_args()' does would be more elegant.
        # The FUNCTIONS dictionary is designed so that altering an option is as simple as changing the type in the init dict. If in the future we want to 
        # for example add the ability to add multiple comments, then it would basically be formatted the same way as section_title[2] (resources) is being
        # formatted at the moment. Obviously repeating this code is dumb

        # Potentially a check for type could be performed against the contents of the class variables and based on that select a formatting method (single or multiple)
        # this would however require a way to get the correct section_title for each comment. Not sure how to do that dynamically based on the variable name, but you
        # can probably get a string from a variable name somehow and then map in a dict or something.
        t = self._get_header_str() + '\n'

        section_title = [
            "Comment" if self._comment else "", 
            "Description" if self._description else "", 
            "Resources" if self._resources else "",
        ]
        
        if any(title for title in section_title): 
            separator = '_' * 18
            t += f"\t{separator}\n"

            indentation = max(len(title) for title in section_title) + 2  # + 2 represent ': '
            
            if section_title[0]:
                pad = self._get_pad(0, indentation, section_title)
                t += f"\t{section_title[0]}: {' ' * pad}{self._comment}\n"

            if section_title[2]:
                n = len(self._resources)
                pad = self._get_pad(2, indentation, section_title)

                for i in range(0, MAX_RESOURCES_TO_DISPLAY):
                    if i >= n:
                        break

                    t += '\t'
                    if i == 0:
                        t += f"{section_title[2]}: {' ' * pad}"
                    else:
                        t += f"{' ' * indentation}"

                    t += f"{self._resources[i]}\n"

                if n > MAX_RESOURCES_TO_DISPLAY:
                    t += f"\t{' ' * indentation}{n - MAX_RESOURCES_TO_DISPLAY} more resources.\n"
        
        return t

def display_table(options):
    for i, task in enumerate(table[TBL_KEY_CONTENTS]):
        print(f"{i+1}: ", end='') # Add dynamic whitespace calculation based on strlen of i.

        if options[OPT_DETAILED]:
            print(task.summarize(), end='')   
        else:
            print(task)

def is_keyword(x):
    return x in OPTION_ALIASES.keys() or x in FUNCTIONS.keys()

def parse_opt_args(args, options, opt):
    while args and not is_keyword(args[0]):  
        arg = args.pop(0)       

        if isinstance(options[opt], str):
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

def init_options(fn):
    return copy.deepcopy(FUNCTIONS[fn])

def parse_args(args):    
    stack = []
    
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

        if arg in OPTION_ALIASES.keys():
            opt = OPTION_ALIASES[arg]

            # Specifies a new task. ex: -t name_for_task0 -r resource_for_task0 -t name_for_task1 -r resource_for_task1
            if opt == OPT_TITLE and options[OPT_TITLE]:
                stack.append(options)
                options = init_options(fn)

            if isinstance(options[opt], bool):
                options[opt] = True
            else:
                parse_opt_args(args, options, opt)
        elif arg.startswith('-'): # everything starting with - is an option but all options do not start with -
            print(f"Invalid option '{arg}' for function '{fn}'.")
            sys.exit()
        else: # Positionals based on current function.
            if fn == FN_ADD:
                if options[OPT_TITLE]:
                    print("USAGE: ")
                    sys.exit()

                options[OPT_TITLE] = arg
                continue

    stack.append(options)

    return fn, stack

def main(fn, options):
    if fn == FN_ADD:
        add(options)
    elif fn == FN_LIST:
        display_table(options)

def add(options):
    task = Task(title=options[OPT_TITLE], resources=options[OPT_RESOURCES]) # Add cleaner arg parsing and rest of args.

    tasks = []
    tasks.append(task)

    for task in tasks:
        if len(table[TBL_KEY_CONTENTS]) >= 10:
            print("Table is full. Unable to add new task.") # give some indication of what failed to write
            sys.exit()

        table[TBL_KEY_CONTENTS].append(task)

    ## Move to function write tasks
    table_to_write = copy.deepcopy(TABLE)
    for task in table[TBL_KEY_CONTENTS]:
        table_to_write[TBL_KEY_CONTENTS].append(task.write_dict())

    table_json = json.dumps(table_to_write, ensure_ascii=False)

    with open("table.json", "w") as table_file:
        table_file.write(table_json)
    ## Move to function write tasks

def import_table(filename, local):
    with open(filename, "r") as f:
        imported = json.loads(f.read())

        local[TBL_KEY_NAME] = imported[TBL_KEY_NAME]

        for d in imported[TBL_KEY_CONTENTS]:
            local[TBL_KEY_CONTENTS].append(Task(taskd=d))

if __name__ == '__main__':
    table = copy.deepcopy(TABLE)

    try:
        import_table(filename="table.json", local=table)
    except (KeyError, FileNotFoundError):
        print("File is not a valid table.")
        sys.exit()

    args = sys.argv[1:]
    fn, stack = parse_args(args)

    for options in stack:
        main(fn, options)
