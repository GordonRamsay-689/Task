import copy
from id_gen import generate_id
from globals import *

class Task:
    """ While the task object is in use the self._taskd dict is not updated. this exists only for internal access.
    When updating a task only the object attributes are updated, until updated data is commited. 

    For example deleting a task by title after that title has been changed from what it was upon import will 
    delete the task from .JSON using its Task.id. The id can never be changed under any circumstance.
    
    Using decorators or functions to set attribute values. getting them is not really necessary to enforce a getter
    as the data types are not complex. """

    def __init__(self, task_id="0", taskd=None, status=False, title="", subtasks=[], comments=[], description="", resources=[]):
        ''' The Task object can be initialized with either an existing task dictionary (typically loaded from JSON)
        or with provided parameters if argument task_dict is not provided. If taskd is provided all other arguments
        will be ignored.

        If no task_dict and no title is provided a title will be generated.
        '''

        self._taskd = copy.deepcopy(TASKD_TEMPLATE)

        if taskd:
            self._id = task_id
            self._load_dict(taskd, task_id)
        else:
            self._comments = comments
            self._description = description
            self._id = self.generate_task_id()
            self._resources = resources
            self._status = status
            self._subtasks = subtasks
            self._title = title or self.generate_task_title()

    def _load_dict(self, taskd):
        ''' Loads an existing dictionary into Task. '''
        
        try:
            self._comments = taskd[TSK_COMMENTS]
            self._description = taskd[TSK_DESCRIPTION]
            self._resources = taskd[TSK_RESOURCES]
            self._status = taskd[TSK_STATUS]
            self._subtasks = taskd[TSK_SUBTASKS]
            self._title = taskd[TSK_TITLE]
        except KeyError:
            print("Failed to load task, missing key-value pair. The data may have already been corrupted before attempt to load.")
            raise
        
        self._taskd = taskd
    
    def write_dict(self):
        ''' Updates the self._taskd dictionary and returns it. 

        Example usage: Writing a task to JSON
        '''

        if self._id == "0":
            print("No task id. Task data may be corrupted.")
            raise ValueError 

        self._taskd[TSK_COMMENTS] = self._comments
        self._taskd[TSK_DESCRIPTION] = self._description
        self._taskd[TSK_RESOURCES] = self._resources
        self._taskd[TSK_STATUS] = self._status
        self._taskd[TSK_SUBTASKS] = self._subtasks
        self._taskd[TSK_TITLE] = self._title
        key = self._id
        
        return self._taskd, key
        
    def __str__(self):
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

    def get_comments(self):
        return self._comments

    def get_description(self):
        return self._description

    def get_id(self):
        return self._id

    def get_resources(self):
        return self._resources

    def get_status(self):
        return self._status

    def get_substasks(self):
        return self._subtasks

    def get_title(self):
        return self._title

    def generate_task_id(self):
        current_id = max(table["tasks"].keys(), key=lambda id: int(id, 36))
        return generate_id(current_id)

    def generate_task_title(self): # Todo
        return "Untitled"
    
    def summarize(self):
        # todo: reformat as single and multiple based on variable type. 
        # todo: Need to dynamically get section_title.
 
        t = self._get_header_str() + '\n'

        section_title = [
            "Comments" if self._comments else "", 
            "Description" if self._description else "", 
            "Resources" if self._resources else "",
            "Subtasks" if self._subtasks else ""
        ]
        
        if any(title for title in section_title): 
            separator = '_' * 18
            t += f"\t{separator}\n"

            indentation = max(len(title) for title in section_title) + 2  # + 2 represent ': '
            
            if section_title[3]:
                t += f"\t{section_title[3]}: {' ' * pad}{len(self._subtasks)}\n"

            if section_title[0]:
                pad = self._get_pad(0, indentation, section_title)
                t += f"\t{section_title[0]}: {' ' * pad}{self._comments}\n"

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
