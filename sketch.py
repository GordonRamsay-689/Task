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

TSK_KEY_STATUS = "completed"
TSK_KEY_TITLE = "title"
TSK_KEY_COMMENT = "comment"
TSK_KEY_DESCRIPTION = "description"
TSK_KEY_RESOURCES = "resources"
TSK_KEY_ID = "id"

tasks = []


def difference(i, indent, section_title):
    return (indent - 2 - len(f"{section_title[i]}"))
    
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

    # def format_attributes()

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
        
    def _print_task_header(self):
        ''' Prints the task header row. Consists of task.title and task.status. ''' 

        title_str = self._title
        status_symbol = COMPLETED_SYMBOL if self._status else UNCOMPLETED_SYMBOL

        title_length = len(title_str)
        if title_length > MAX_TITLE_LENGTH:
            title_str = title_str[:MAX_TITLE_LENGTH] + '...'

        print(f"|{status_symbol}|\t{title_str} (ID: {self._id})")

    def print_task(self):
        self._print_task_header()   

        if self._comment or self._resources:
            separator = '_' * 18
            print(f"\t{separator}")
            section_title = ["", ""]

            if self._comment:
                section_title[0] = "Comment"

            if self._resources:
                section_title[1] = "Resources"

            indent = max(len(title) for title in section_title) + 2  # + 2 represent ': '
            
            if self._comment:
                diff = difference(0, indent, section_title)
                print(f"\t{section_title[0]}: {' ' * diff}{self._comment}")

            if self._resources:
                n = len(self._resources)
                diff = difference(1, indent, section_title)

                for i in range(0, MAX_RESOURCES_TO_DISPLAY):
                    if i >= n:
                        break

                    print("\t", end='')
                    if i == 0:
                        print(f"{section_title[1]}: {' ' * diff}", end='')
                    else:
                        print(f"{' ' * indent}", end='')

                    print(f"{self._resources[i]}")

                if n > MAX_RESOURCES_TO_DISPLAY:
                    print(f"\t{' ' * indent}{n - MAX_RESOURCES_TO_DISPLAY} more resources.")

def display_table():
    for i, task in enumerate(table):
        print(f"{i+1}: ", end='')
        task.print_task()        

def parse_args(argv):
    # not implemented
    return argv[0]

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
    

    title = parse_args(argv)
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