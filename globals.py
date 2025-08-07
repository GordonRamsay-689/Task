from ordered_set import OrderedSet

# ! Extend OrderedSet (v 4.1.0)

class OrderedSet(OrderedSet):
    def move(self, value, steps):
        ''' Moves a value 'steps' indices and return the position of 
        value. If new index would be out of range (would produce 
        IndexError) the current index of value is returned immediately
        without attempting to move the item. '''
        i = self.index(value)

        if i + steps < 0 or i + steps > len(self) - 1:
            return i
        
        step = -1 if steps < 0 else 1 
        for j in range(i, i + steps, step):
            self.items[j], self.items[j + step] = self.items[j + step], self.items[j]
            self.map[self.items[j]] = j
            self.map[self.items[j + step]] = j + step
        
        return i + steps

# ! STATIC GLOBALS

COMPLETED_SYMBOL = 'x'
UNCOMPLETED_SYMBOL = '-'

## Configurable values.
MAX_DISPLAY_TITLE_LENGTH = 38
MAX_RESOURCES_TO_DISPLAY = 2
MAX_SUBTASKS_TO_DISPLAY = 4
MAX_PARENTS_TO_DISPLAY = 4
MAX_COMMENTS_TO_DISPLAY = 4

## 9999 is a placeholder value, but also does limit some (ridiculously) erroneous assignments.
MAX_COMMENT_LEN = 9999
MAX_COMMENTS = 9999
MAX_DESCRIPTION_LEN = 9999
MAX_RESOURCE_LEN = 9999
MAX_RESOURCES = 9999
MAX_PARENTS = 9999
MAX_SUBTASKS = 9999
MAX_TITLE_LENGTH = 9999

MAX_GROUP_TITLE_LENGTH = 50

## Task Keys
TASK_COMMENTS = "comments"
TASK_DESCRIPTION = "description"
TASK_FILES = "files"
TASK_LINKS = "links"
TASK_STATUS = "completed"
TASK_SUBTASKS = "subtasks"
TASK_TITLE = "title"
TASK_PARENTS = "parents"

## Data Keys
DATA_ACTIVE_GROUP = "active_group"
DATA_CURRENT_GROUP = "current_group"
DATA_CURRENT_TASK = "current_task"
DATA_GROUPS = "groups"
DATA_TASKS = "tasks"

GROUP_TASKS = "task_ids"
GROUP_TITLE = "title"

## Templates

TASKD_TEMPLATE = {
    TASK_COMMENTS: [], 
    TASK_DESCRIPTION: "", 
    TASK_FILES: [],
    TASK_LINKS: [],
    TASK_STATUS: False, 
    TASK_SUBTASKS: [],
    TASK_PARENTS: [],
    TASK_TITLE: ""
}

GROUP_TEMPLATE = {
    "task_ids": OrderedSet(),
    "title": ""
    }

# ! Custom Exceptions

class CustomException(Exception):
    def _construct_error_str(self, desc, msg):
        text = f"Error: {desc}"
        
        if msg:
            text += f"\nDetail: {msg}"

        return text

    def __str__(self):
        return self._construct_error_str(self.desc, self.msg)

class DataError(CustomException): # ? On DataError, restore master.STORAGE_BACKUP 
    ''' Master.data (or storage file) or specific Task data is corrupted or otherwise unexpected. '''
    def __init__(self, msg="", path=None, task_id=None):
        
        self.msg = msg
        self.path = path
        self.task_id = task_id

        part = ''
        if self.task_id:
            part += f"in task with ID '{self.task_id}' "
        if self.path:
            part += f"at path '{self.path}' "

        self.desc = f"Data {part}is corrupt or unexpected."

class FSError(CustomException):
    ''' A filesystem error occured. '''
    def __init__(self, path, msg="", task_id=None):
        
        self.msg = msg
        self.task_id = task_id
        self.path = path

        part = ""
        if self.task_id:
            part += f" while handling '{self.task_id}'"

        self.desc = f"An error occured while trying to access '{self.path}'{part}."

class GroupNotFoundError(CustomException):
    def __init__(self, group_id, msg="", task_id=None,):
        
        self.group_id = group_id
        self.msg = msg
        self.task_id = task_id

        self.desc = f"No group ID found with ID: '{self.group_id}'"

class TaskCreationError(CustomException):
    ''' An error occured during Task object creation. '''
    def __init__(self, task_id,  msg=""):
        
        self.msg = msg
        self.task_id = task_id

        self.desc = f"Failed to create task with ID: '{self.task_id}'"

class TaskNotFoundError(CustomException):
    def __init__(self, task_id,  msg=""):
        
        self.msg = msg
        self.task_id = task_id
        
        self.desc = f"No task found with ID: '{self.task_id}'"