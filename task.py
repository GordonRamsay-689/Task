import copy, os
from id_gen import increment_id
from globals import *

# Todo: add min_length=x to calls to _base_validate_length()

class Task:
    ''' Represents a task. 
    
    If 'taskd' is passed the data from 'taskd' (task dictionary) will be validated and then used to construct self (Task). 'task_id' will also be validated. 
    See '_validate_id()' for format and type requirements. If 'taskd' is not passed 'task_id' will be ignored, and an ID will be generated. All other 
    arguments will be used (except 'master'), if any, to construct the Task object. 'master' is always optional and if passed is expected to contain method 'get_current_task_id()'. 
    
    Args:
    
        taskd, task_id, [master]
            OR 
        [status], [title], [subtasks], [parents], [comments], [description], [links], [files], [master]


    Function prefixes:

        '__'          : Only to be called by Python.
        '_'           : Private, to be called by self (Task).
        '_validate_x' : Validates data passed to object corresponding to attribute '_x'. See each individual '_validate' function to see what format is expected
                        for each attribute.
        'get_x'       : Returns a copy of the attribute '_x' in Task (with some exceptions, like 'get_status_symbol()' which doesn't correspond
                        directly to any attribute). Modifying the returned copy does not modify the Task object itself.
        'set_x'       : Sets attribute '_x' to provided data if it passes validation by '_validate_x'.
        'replace_x'   : Replaces (sets) the value of an already existing list entry after provided data if it passes validation by '_validate_x'.
                        Trying to update an index with no associated value will raise IndexError.
        'add_x'       : Adds value to list or set if it passes validation by '_validate_x'.
        'remove_x'    : Removes by value from set or by index from list. 
    '''

    def __init__(self, master=None, taskd={}, task_id=None, status=False, title="", subtasks=[], parents=[], comments=[], description="", links=[], files=[]):
        self.master = master

        self._taskd = copy.deepcopy(TASKD_TEMPLATE)

        self._validate_args(taskd=taskd, task_id=task_id, status=status, title=title, subtasks=subtasks, parents=parents, comments=comments, description=description, links=links, files=files)

        if taskd:
            self._id = task_id
            self._load_dict(taskd)
        else:
            self._comments = comments
            self._description = description
            self._init_files(files)
            self._links = links
            self._status = status
            self._subtasks = OrderedSet(subtasks)
            self._parents = OrderedSet(parents)
            self._title = title or self.generate_task_title()
            self._id = self.generate_task_id() # Last, so errors happen before increment of current_id

    def __str__(self):
        return self._get_header_str()

    def _get_header_str(self):
        ''' Format the task header row. Consists of task.title and task.status. ''' 

        status = COMPLETED_SYMBOL if self._status else UNCOMPLETED_SYMBOL
        
        title = self._title
        if len(title) > MAX_DISPLAY_TITLE_LENGTH:
            title = title[:MAX_DISPLAY_TITLE_LENGTH] + '...'

        return f"|{status}|\t{title} (ID: {self._id})"

    def _get_pad(self, i, indent, section_title):
        return (indent - 2 - len(f"{section_title[i]}")) # -2 represent': '
    
    def _init_files(self, files):
        self._files = []
        for path in files:
            self._files.append(os.path.abspath(path))
    
    def _load_dict(self, taskd):
        ''' Loads an existing dictionary into Task. '''
        
        self._comments = taskd[TASK_COMMENTS]
        self._description = taskd[TASK_DESCRIPTION]
        self._links = taskd[TASK_LINKS]
        self._init_files(taskd[TASK_FILES])
        self._status = taskd[TASK_STATUS]
        self._subtasks = OrderedSet(taskd[TASK_SUBTASKS])
        self._parents = OrderedSet(taskd[TASK_PARENTS])
        self._title = taskd[TASK_TITLE]
        
        self._taskd = taskd

    def _validate_args(self, taskd, task_id, status, title, subtasks, parents, comments, description, links, files):
        ''' Validates provided arguments (including data in taskd, if provided). 
        
        Raises:
            TypeError
            ValueError
        '''
        if taskd:
            self._validate_id(task_id)

            if not isinstance(taskd, dict):
                raise TypeError("'taskd' is not of type dict.")
            
            if taskd.keys() != TASKD_TEMPLATE.keys():
                raise ValueError(f"Provided 'taskd' does not follow the expected structure of a task dictionary.\nIf this dictionary was loaded this indicates that data may have been corrupted.")

            comments = taskd[TASK_COMMENTS]
            description = taskd[TASK_DESCRIPTION]
            links = taskd[TASK_LINKS]
            files = taskd[TASK_FILES]
            status = taskd[TASK_STATUS]
            subtasks = taskd[TASK_SUBTASKS]
            parents = taskd[TASK_PARENTS]
            title = taskd[TASK_TITLE]

        self._validate_comments(comments)
        self._validate_description(description)
        self._validate_links(links)
        self._validate_files(files)
        self._validate_status(status)
        self._validate_subtasks(subtasks)
        self._validate_parents(parents)
        self._validate_title(title)

    def _validate_base_length(self, object, max_length, min_length, name):
        obj_len = len(object)
        
        if obj_len > max_length:
            if not isinstance(object, str):
                object = str(object)            
            msg = f"Lenght of '{name}' ({object[:6]}..) exceeds exceeds maximum of {max_length}."
            raise ValueError(msg)
        elif obj_len < min_length:
            msg = f"Lenght of '{name}' does not satisfy minimum of {min_length}."
            raise ValueError(msg)

    def _validate_base_list(self, lst, fn, name, item_type=None):
        type_to_max_len = {
            TASK_COMMENTS: MAX_COMMENTS,
            TASK_LINKS: MAX_RESOURCES,
            TASK_FILES: MAX_RESOURCES,
            TASK_SUBTASKS: MAX_SUBTASKS,
            TASK_PARENTS: MAX_PARENTS
        } # ? Probably redundant, unless only one parent should be allowed.

        self._validate_base_object(lst, list, name, max_length=type_to_max_len[name], min_length=0)

        for item in lst:
            try:
                fn(item)
            except TypeError as e:
                if fn == self._validate_id:
                    msg = f"One of the IDs in '{name}' is not a valid task ID:\n\t{e}"
                else:
                    msg = f"One of the items in '{name}' is not of type {item_type}:\n\t{e}"
                
                raise TypeError(msg) from e
            except ValueError as e:
                if fn == self._validate_id:
                    msg = f"One of the IDs in '{name}' is not a valid task ID:\n\t{e}"
                else:
                    msg = f"One of the values in '{name}' is invalid:\n\t{e}"

                raise ValueError(msg) from e

    def _validate_base_object(self, object, type, name, max_length=99999, min_length=0):
        if not isinstance(object, type):
            raise TypeError(f"'{name}' is not of type {type}.")
        
        if hasattr(type, '__len__'):
            self._validate_base_length(object, max_length, min_length, name)

    def _validate_comment(self, comment):
        self._validate_base_object(comment, str, "comment", max_length=MAX_COMMENT_LEN)
        
    def _validate_comments(self, comments):
        self._validate_base_list(comments, self._validate_comment, 'comments', item_type=str)
        
    def _validate_description(self, description):
        self._validate_base_object(description, str, "description", max_length=MAX_DESCRIPTION_LEN)
        
    def _validate_id(self, task_id):
        try:
            int(task_id, 36)
        except (TypeError, ValueError) as e:
            raise type(e)(f"Invalid task ID. Not a base-36 string.") from e

    def _validate_parents(self, parents):
        self._validate_base_list(parents, self._validate_id, 'parents')

    def _validate_link(self, url):
        self._validate_base_object(url, str, "link", max_length=MAX_RESOURCE_LEN, min_length=1)
        
        pass # Check if a valid URL (malformed is OK)

    def _validate_file(self, path):
        self._validate_base_object(path, str, "file", max_length=MAX_RESOURCE_LEN, min_length=1)

        if not path:
            raise ValueError("Path must contain at least one character.")

        path = os.path.abspath(path)
        if not os.path.exists(path):
            raise ValueError(f"Could not locate path: {path}")

    def _validate_files(self, files):
        self._validate_base_list(files, self._validate_file, 'files', item_type=str)

    def _validate_links(self, links):
        self._validate_base_list(links, self._validate_link, 'links', item_type=str)
        
    def _validate_status(self, status):
        self._validate_base_object(status, bool, "status")

    def _validate_subtasks(self, subtasks):
        self._validate_base_list(subtasks, self._validate_id, 'subtasks')

    def _validate_title(self, title):
        self._validate_base_object(title, str, "title", max_length=MAX_TITLE_LENGTH)

    def add_parent(self, parent_id):
        self._validate_id(parent_id)
        self._parents.add(parent_id)

    def add_subtask(self, subtask_id):
        self._validate_id(subtask_id)
        self._subtasks.add(subtask_id)

    def add_comment(self, comment):
        self._validate_comment(comment)
        self._comments.append(comment)
    
    def add_link(self, url):
        self._validate_link(url)
        self._links.append(url)

    def add_file(self, path):
        self._validate_file(path)
        self._files.append(os.path.abspath(path))

    def generate_task_id(self):
        ''' Generates a task ID based on information provided by master.
        If Task has no master generate_task_id() returns -1 (expects task
        IDs not being tracked.)

        If a master is not used to track IDs it is important to excplicitly
        pass unique task IDs for each subtask and parent, or many operations
        will not be available.
        '''

        if not self.master:
            return "-1"
        
        id = increment_id(self.master.get_current_task_id())
        self.master.set_current_task_id(id, validate_id=False)
        return id

    def generate_task_title(self):
        return "Untitled"

    def get_comments(self):
        return list(self._comments)

    def get_description(self):
        return self._description

    def get_id(self):
        return self._id

    def get_parents(self):
        return list(self._parents)

    def get_links(self):
        return list(self._links)

    def get_files(self):
        return list(self._files)

    def get_status(self):
        return self._status
    
    def get_status_symbol(self):
        return COMPLETED_SYMBOL if self.get_status() else UNCOMPLETED_SYMBOL
    
    def get_subtasks(self):
        return list(self._subtasks)

    def get_title(self):
        return self._title

    def move_parent(self, parent_id, steps):
        try:
            index = self._parents.move(parent_id, steps)
        except KeyError as e:
            raise TaskNotFoundError(task_id=parent_id, msg=f"No parent found with ID: '{parent_id}'") from e
        
        return index
    
    def move_subtask(self, subtask_id, steps):
        try:
            index = self._subtasks.move(subtask_id, steps)
        except KeyError as e:
            raise TaskNotFoundError(task_id=subtask_id, msg=f"No subtask found with ID: '{subtask_id}'") from e
        
        return index
    
    def remove_comment(self, index):
        self._comments.pop(index)
    
    def remove_file(self, index):
        self._files.pop(index)

    def remove_link(self, index):
        self._links.pop(index)

    def remove_parent(self, parent_id):
        self._parents.discard(parent_id)

    def remove_subtask(self, subtask_id):
        self._subtasks.discard(subtask_id)
    
    def replace_comment(self, index, comment):
        self._validate_comment(comment)

        try:
            self._comments[index] = comment
        except IndexError as e:
            raise type(e)(f"No comment with index: '{index}'") from e

    def replace_file(self, index, path):
        self._validate_file(path)

        try:
            self._files[index] = path
        except IndexError as e:
            raise type(e)(f"No file at index: '{index}'") from e

    def replace_link(self, index, url):
        self._validate_link(url)

        try:
            self._links[index] = url
        except IndexError as e:
            raise type(e)(f"No link at index: '{index}'") from e

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

    def summarize(self): # ! TODO: Replace resources with links, files.
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

        self._taskd[TASK_COMMENTS] = list(self._comments)
        self._taskd[TASK_DESCRIPTION] = self._description
        self._taskd[TASK_FILES] = list(self._files)
        self._taskd[TASK_LINKS] = list(self._links)
        self._taskd[TASK_STATUS] = self._status
        self._taskd[TASK_SUBTASKS] = list(self._subtasks)
        self._taskd[TASK_PARENTS] = list(self._parents)
        self._taskd[TASK_TITLE] = self._title
        
        return self._taskd