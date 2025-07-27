PROGRAM_NAME = "ctd"

# Configurable variables.
MAX_DISPLAY_TITLE_LENGTH = 38
MAX_RESOURCES_TO_DISPLAY = 2

MAX_COMMENT_LEN = 9999
MAX_COMMENTS = 9999
MAX_DESCRIPTION_LEN = 9999
MAX_RESOURCE_LEN = 9999
MAX_RESOURCES = 9999
MAX_PARENTS = 9999
MAX_SUBTASKS = 9999
MAX_TITLE_LENGTH = 9999

MAX_GROUP_TITLE_LENGTH = 50

# Task
TSK_COMMENTS = "comments"
TSK_DESCRIPTION = "description"
TSK_FILES = "files"
TSK_LINKS = "links"
TSK_STATUS = "completed"
TSK_SUBTASKS = "subtasks"
TSK_TITLE = "title"
TSK_PARENTS = "parents"

TASKD_TEMPLATE = {
    TSK_COMMENTS: [], 
    TSK_DESCRIPTION: "", 
    TSK_FILES: [],
    TSK_LINKS: [],
    TSK_STATUS: False, 
    TSK_SUBTASKS: [],
    TSK_PARENTS: [],
    TSK_TITLE: ""
}

COMPLETED_SYMBOL = 'x'
UNCOMPLETED_SYMBOL = '-'

# ! Custom Exceptions

class CustomException(Exception):
    def _construct_error_str(self, desc, msg):
        text = f"Error: {desc}"
        
        if msg:
            text += f"\nInfo: {msg}"

        return text

    def __str__(self):
        return self._construct_error_str(self.desc, self.msg)

class DataError(CustomException): # ? On DataError, restore master.STORAGE_BACKUP 
    ''' Master.data (or storage file) is corrupted or otherwise unexpected. '''
    def __init__(self, e=None, msg="", path=None, task_id=None):
        self.e = e
        self.msg = msg
        self.path = path
        self.task_id = task_id

        self.desc = f"Data is corrupt."

class FSError(CustomException):
    ''' A filesystem error occured. '''
    def __init__(self, path, e=None, msg="", task_id=None):
        self.e = e
        self.msg = msg
        self.task_id = task_id
        self.path = path

        self.desc = f"An error occured while trying to access: '{self.path}'."

class GroupNotFoundError(CustomException):
    def __init__(self, group_id, e=None, msg="", task_id=None,):
        self.e = e
        self.group_id = group_id
        self.msg = msg
        self.task_id = task_id

        self.desc = f"No group ID found with ID: '{self.group_id}'"

class TaskCreationError(CustomException):
    ''' An error occured during Task object creation. '''
    def __init__(self, task_id, e=None, msg=""):
        self.e = e
        self.msg = msg
        self.task_id = task_id

        self.desc = f"Failed to create task with ID: '{self.task_id}'"

class TaskNotFoundError(CustomException):
    def __init__(self, task_id, e=None, msg=""):
        self.e = e
        self.msg = msg
        self.task_id = task_id
        
        self.desc = f"No task found with ID: '{self.task_id}'"