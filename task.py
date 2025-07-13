import copy
from id_gen import generate_id
from globals import *

class Task:
    def __init__(self, master, taskd={}, task_id=None, status=False, title="", subtasks=[], parents=[], comments=[], description="", resources=[]):
        ''' The Task object can be initialized with either an existing task dictionary (typically loaded from JSON)
        or with provided parameters if argument task_dict is not provided. If taskd is provided all other keyword 
        arguments will be ignored.

        If taskd is provided a task_id must also be provided

        If no taskd and no title is provided a title will be generated.
        '''

        self.master = master

        self._taskd = copy.deepcopy(TASKD_TEMPLATE)

        self._validate_args(taskd=taskd, task_id=task_id, status=status, title=title, subtasks=subtasks, parents=parents, comments=comments, description=description, resources=resources)

        if taskd:
            self._id = task_id
            self._load_dict(taskd)
        else:
            self._comments = comments
            self._description = description
            self._resources = resources
            self._status = status
            self._subtasks = set(subtasks)
            self._parents = set(parents)
            self._title = title or self.generate_task_title()
            self._id = self.generate_task_id() # Last, so errors happen before increment of current_id

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

    def _load_dict(self, taskd):
        ''' Loads an existing dictionary into Task. '''
        
        self._comments = taskd[TSK_COMMENTS]
        self._description = taskd[TSK_DESCRIPTION]
        self._resources = taskd[TSK_RESOURCES]
        self._status = taskd[TSK_STATUS]
        self._subtasks = set(taskd[TSK_SUBTASKS])
        self._parents = set(taskd[TSK_PARENTS])
        self._title = taskd[TSK_TITLE]
        
        self._taskd = taskd

    def _validate_args(self, taskd, task_id, status, title, subtasks, parents, comments, description, resources):
        ''' Validates provided arguments (including data in taskd, if provided). 
        
        Raises:
            TypeError
            ValueError
        '''
        if taskd:
            self._validate_id(task_id)

            if not isinstance(taskd, dict):
                raise TypeError("'taskd' is not of type dict.")
            
            if taskd.keys() != copy.deepcopy(TASKD_TEMPLATE).keys():
                raise TypeError(f"Provided 'taskd' does not follow the expected structure of a task dictionary.\nIf this dictionary was loaded this indicates that data may have been corrupted.")

            comments = taskd[TSK_COMMENTS]
            description = taskd[TSK_DESCRIPTION]
            resources = taskd[TSK_RESOURCES]
            status = taskd[TSK_STATUS]
            subtasks = taskd[TSK_SUBTASKS]
            parents = taskd[TSK_PARENTS]
            title = taskd[TSK_TITLE]

        self._validate_comments(comments)
        self._validate_description(description)
        self._validate_resources(resources)
        self._validate_status(status)
        self._validate_subtasks(subtasks)
        self._validate_parents(parents)
        self._validate_title(title)

    def _validate_base_length(self, object, length, name):
        if len(object) > length:
            raise ValueError(f"Lenght of '{name}' exceeds maximum of {length}.") ## Not very helpful

    def _validate_base_list(self, lst, fn, name, item_type=None):
        self._validate_base_object(lst, list, name)

        for item in lst:
            try:
                fn(item)
            except TypeError as e:
                if fn == self._validate_id:
                    msg = f"One of the IDs in '{name}' is not a valid task ID."
                else:
                    msg = f"One of the items in '{name}' is not of type {item_type}."
                
                raise TypeError(msg) from e
            except ValueError as e:
                raise TypeError(f"One of the itmes in '{name}' exceeds maximum length.") from e

    def _validate_base_object(self, object, type, name, length=None):
        if not isinstance(object, type):
            raise TypeError(f"'{name}' is not of type {type}.")
        
        if length:
            self._validate_base_length(object, length, name)

    def _validate_comment(self, comment):
        self._validate_base_object(comment, str, "comment", length=MAX_COMMENT_LEN)
        
    def _validate_comments(self, comments):
        self._validate_base_list(comments, self._validate_comment, 'comments', item_type=str)
        
        self._validate_base_length(comments, MAX_COMMENTS, "comments")

    def _validate_description(self, description):
        self._validate_base_object(description, str, "description", length=MAX_DESCRIPTION_LEN)
        
    def _validate_id(self, task_id):
        try:
            int(task_id, 36)
        except (TypeError, ValueError) as e:
            raise TypeError(f"Invalid task ID. Not a base-36 string.") from e

    def _validate_parents(self, parents):
        self._validate_base_list(parents, self._validate_id, 'parents')

    def _validate_resource(self, resource):
        self._validate_base_object(resource, str, "resource", length=MAX_RESOURCE_LEN)

    def _validate_resources(self, resources):
        self._validate_base_list(resources, self._validate_resource, 'resources', item_type=str)
        self._validate_base_length(resources, MAX_RESOURCES, 'resources')
        
    def _validate_status(self, status):
        self._validate_base_object(status, bool, "status")

    def _validate_subtasks(self, subtasks):
        self._validate_base_list(subtasks, self._validate_id, 'subtasks')

    def _validate_title(self, title):
        self._validate_base_object(title, str, "title", length=MAX_TITLE_LENGTH)

    def add_parent(self, parent_id):
        self._validate_id(parent_id)
        self._parents.add(parent_id)

    def add_subtask(self, subtask_id):
        self._validate_id(subtask_id)
        self._subtasks.add(subtask_id)

    def add_comment(self, comment):
        self._validate_comment(comment)
        self._comments.append(comment)
    
    def add_resource(self, resource):
        self._validate_resource(resource)
        self._resources.append(resource)

    def remove_comment(self, index):
        self._comments.pop(index)
    
    def remove_resource(self, index):
        self._resources.pop(index)

    def remove_parent(self, parent_id):
        try:
            self._parents.remove(parent_id)
        except KeyError:
            pass

    def remove_subtask(self, subtask_id):
        try:
            self._subtasks.remove(subtask_id)
        except KeyError:
            pass

    def generate_task_id(self):
        id = generate_id(self.master.data["current_id"])
        self.master.update_current_id(id)
        return id

    def generate_task_title(self): # Todo
        return "Untitled"

    def get_comments(self):
        return self._comments

    def get_description(self):
        return self._description

    def get_id(self):
        return self._id

    def get_parents(self):
        return list(self._parents)

    def get_resources(self):
        return self._resources

    def get_status(self):
        return self._status
    
    def get_status_symbol(self):
        return COMPLETED_SYMBOL if self.get_status() else UNCOMPLETED_SYMBOL
    
    def get_subtasks(self):
        return list(self._subtasks)

    def get_title(self):
        return self._title

    def set_title(self, title):
        self._validate_title(title)
        self._title = title

    def set_description(self, description):
        self._validate_description(description)
        self._description = description
        
    def set_status(self, status):
        self._validate_status(status)

        self._status = status

    def toggle_status(self):
        self._status = not self._status

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
            
            # Subtasks
            if section_title[3]:
                t += f"\t{section_title[3]}: {' ' * pad}{len(self._subtasks)}\n"

            # Comments
            if section_title[0]:
                pad = self._get_pad(0, indentation, section_title)
                t += f"\t{section_title[0]}: {' ' * pad}{self._comments}\n"

            # Resources
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

    def write_dict(self):
        ''' Updates the self._taskd dictionary and returns it.

        Example usage: Writing a task to JSON
        '''

        self._taskd[TSK_COMMENTS] = self._comments
        self._taskd[TSK_DESCRIPTION] = self._description
        self._taskd[TSK_RESOURCES] = self._resources
        self._taskd[TSK_STATUS] = self._status
        self._taskd[TSK_SUBTASKS] = list(self._subtasks)
        self._taskd[TSK_PARENTS] = list(self._parents)
        self._taskd[TSK_TITLE] = self._title
        
        return self._taskd