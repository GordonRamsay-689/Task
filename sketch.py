import sys
import json

MAX_TITLE_LENGTH = 38

MAX_RESOURCES_TO_DISPLAY = 2

COMPLETED_SYMBOL = 'x'
UNCOMPLETED_SYMBOL = '-'

FN_ADD = "add"
FN_REMOVE = "remove"
FN_CLEAR = "clear"
FN_EDIT = "edit"
FN_LIST = "list"
FN_STASH = "stash"

FUNCTIONS = {
    FN_ADD: {}, # option: n_args || option:more_options
    FN_REMOVE: {}, 
    FN_CLEAR: {}, 
    FN_EDIT: {}, 
    FN_LIST: {}, 
    FN_STASH: {}
}

TSK_KEY_STATUS = "completed"
TSK_KEY_TITLE = "title"
TSK_KEY_COMMENT = "comment"
TSK_KEY_DESCRIPTION = "description"
TSK_KEY_RESOURCES = "resources"
TSK_KEY_ID = "id"

tasks = []
    
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

    def summarize(self):
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

def display_table(detailed=True):
    for i, task in enumerate(table):
        print(f"{i+1}: ", end='')

        if detailed:
            print(task.summarize(), end='')   
        else:
            print(task)

def parse_args(args):
    if len(args) != len(set(args)):
        print("Duplicate arguments provided.")
        sys.exit()
    
    arg = args.pop(0)

    if arg in FUNCTIONS.keys(): 
        fn = arg
    else:
        fn = FN_ADD
        task_title = arg

    # Move into main scope 
    options = []
    for option in FUNCTIONS[fn]:
        options[option] = False
    # options[option] can contain either list or bool. this forces check isattribute(list) which is a bit messy?

    while args:
        arg = args.pop(0)

        if arg in FUNCTIONS.keys():
            print(f"Already provided function: {fn}")
            sys.exit()

        if arg.startswith('-'): 
            option = arg

            if option not in FUNCTIONS[fn]:
                print("Unrecognised option '{option}' for function '{mode}'.")    
                sys.exit()


            if FUNCTIONS[fn][option]: # option takes arguments
                if not args:
                    print(f"Option '{option}' requires at least one argument.")
                    sys.exit()

                options[option] = [] # list of arguments for option # Should probably init outside of this
                while args:
                    if any(args[0] == fn or args[0] in FUNCTIONS[fn] for fn in FUNCTIONS.keys()): ## If next arg is another keyword it is not a valid arg for option
                        if not options[option]: ## if no args have been provided for an option that requires args then exit
                            print(f"Option '{option}' requires at lest one argument.")
                            sys.exit()
                        break 
                    
                    options[option].append(args.pop(0)) # pop happens after check so we avoid having to reappend another option for example
            else:
                options[option] = True
        else:
            pass # positional based on mode

if __name__ == '__main__':
    table = []
    with open("table.json", "r") as table_file:
        l = json.loads(table_file.read())
        for d in l:
            table.append(Task(taskd=d))

    argv = sys.argv[1:]
    argc = len(argv)

    if (argc == 0):
        display_table()
        sys.exit()
    
    title = parse_args(argv, argc)
    task = Task(title=title)
    
    tasks.append(task)

    for task in tasks:
        if len(table) >= 10:
            print("Table is full. Unable to add new task.")
            break

        table.append(task.write_dict())

    table_json = json.dumps(table, ensure_ascii=False)

    with open("table.json", "w") as table_file:
        table_file.write(table_json)