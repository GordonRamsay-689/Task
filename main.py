import os, sys, json, copy
from task import Task
from id_gen import increment_id
from globals import *

# ? check for success on write in write_data()
# ? relay failure for each failed task when loading group.

class CustomException(Exception):
    def _construct_error_str(self, desc, msg):
        text = f"Error: {desc}"
        
        if msg:
            text += f"\nInfo: {msg}"

        return text

    def __str__(self):
        return self._construct_error_str(self.desc, self.msg)

class DataError(CustomException): # ? On DataError, restore master.STORAGE_BACKUP 
    ''' Data is corrupted or otherwise unexpected. '''
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

class Master:
    ''' Manages I/O operations and Task objects. '''
    def __init__(self, ui):
        self.ui = ui

        self.SCRIPT_DIR = self._get_script_dir()
        self.STORAGE_PATH = os.path.join(self.SCRIPT_DIR, "storage.json")

        self.data = {}

    def _deep_remove_task(self, task_id):
        ''' Goes through all tasks attempting to remove task with ID task_id
        from any substasks and parents lists. Recursively performs the same 
        operation for any subtasks found.
         
        This is a slow operation, prefer self.remove_task(). 
        '''
        for _task_id, task in self.data["tasks"].items():
            
            if not _task_id in self.data["tasks"].keys(): # ! If a subtask has been removed in a deeper recursion layer
                continue

            if self._is_Task(_task_id): # Potentially put in try-except TaskNotFoundError
                try:
                    task.remove_subtask(task_id)
                    self.deep_remove_task(_task_id)
                except ValueError:
                    pass

                try:
                    task.remove_parent(task_id)
                except ValueError:
                    pass
            else:
                try:
                    task[TSK_SUBTASKS].remove(task_id)
                    self.deep_remove_task(_task_id)
                except ValueError:
                    pass
    
                try:
                    task[TSK_PARENTS].remove(task_id)
                except ValueError:
                    pass
        try:
            self.data["tasks"].pop(task_id)
        except ValueError:
            pass

    def _get_script_dir(self):
        ''' Get the directory of the file that Master object is created from. '''
        dirname, _ = os.path.split(__file__)
        return os.path.abspath(dirname)

    def _is_Task(self, task_id):
        ''' Confirms if task ID is a Task object. '''
        try:
            if isinstance(self.data["tasks"][task_id], Task):
                return True
            else:
                return False
        except KeyError as e:
            raise TaskNotFoundError(task_id=task_id, e=e)

    def add_task_to_group(self, task_id, group_id): 
        ''' Adds an existing task ID to a group. '''
        error_message = f"Failed to add task with ID '{task_id}' to group with ID '{group_id}'."

        if not task_id in self.data["tasks"]:
            raise TaskNotFoundError(task_id=task_id, 
                                    msg=error_message)
        
        try:        
            self.data["groups"][group_id]["task_ids"].append(task_id)
        except KeyError as e:
            raise GroupNotFoundError(group_id=group_id, 
                                     task_id=task_id, 
                                     msg=error_message, 
                                     e=e)

    def create_subtask(self, parent_task_id, task_kwargs={}):
        ''' Creates a Task object and adds task ID to subtask 
        attribute of Task object with ID parent_task_id. 
        
        Returns task ID on completion.
        '''
        try:
            task_id = self.create_task(subtask=True, task_kwargs=task_kwargs)
        except TaskCreationError:
            raise

        try:
            self.load_task(parent_task_id)
        except TaskNotFoundError as e:
            e.msg = f"Could not assign task with ID '{task_id}' a subtask of task with ID '{parent_task_id}'.\nAttempting to remove task with ID: '{task_id}'."
            self.remove_task(task_id)        
            raise

        self.data["tasks"][task_id].add_parent(parent_task_id)
        self.data["tasks"][parent_task_id].add_subtask(task_id)

        return task_id

    def create_task(self, group_id=None, subtask=False, task_kwargs={}):
        ''' Creates a Task object with args in task_kwargs and returns task ID on success. '''
        if group_id and subtask:
            raise TaskCreationError(task_id=increment_id(self.get_current_id()), 
                                    e=TypeError, 
                                    msg="Argument Error: A task cannot be both a subtask and part of a group.")

        try:
            task = Task(master=self, **task_kwargs)
        except (TypeError, ValueError) as e:
            raise TaskCreationError(task_id=increment_id(self.get_current_id()), 
                                    e=e,
                                    msg=f"Error with argument passed to Task.__init__(): '{task_kwargs}'.")

        task_id = task.get_id()
        self.data["tasks"][task_id] = task

        if group_id:
            try:
                self.add_task_to_group(task_id, group_id)
            except GroupNotFoundError as e:
                e.msg += f"\nTask with ID '{task_id}' was created but not succesfully added to any group."
                raise
            
        return task_id

    def get_active_group(self):
        return self.data["active_group"]
    
    def get_current_id(self):
        return self.data["current_id"]

    def get_group_task_ids(self, group_id):
        ''' Returns a list of task IDs in group. '''
        try:
            task_ids = self.data["groups"][group_id]["task_ids"]
        except KeyError as e:
            raise GroupNotFoundError(group_id=group_id, e=e)
        
        return task_ids

    def get_groups(self):
        ''' Returns a list of group IDs. '''
        return list(self.data["groups"].keys())
    
    def get_task(self, task_id):
        ''' Loads and returns Task object with ID task_id. '''
        try:
            self.load_task(task_id)
        except TaskNotFoundError:
            raise
        
        return self.data["tasks"][task_id]

    def get_tasks(self):
        ''' Returns a list of all task IDs. '''
        return list(self.data["tasks"].keys())

    def init_storage_file(self):
        group = copy.deepcopy(GROUP_TEMPLATE)
        group["title"] = "General"

        storage = {
            "current_id": "0", # IDs are in base 36, hence strings
            "active_group": "0",
            "groups": {"0": group},
            "tasks": {} 
        }
        try:
            with open(self.STORAGE_PATH, "w") as f:
                f.write(json.dumps(storage, ensure_ascii=False))
        except FileNotFoundError as e:
            raise FSError(e=e, path=self.STORAGE_PATH, msg="A file system error occured during creation of storage file.")
        except PermissionError as e:
            raise FSError(e=e, path=self.STORAGE_PATH, msg=f"No permission to create storage file. Inspect file permissions for: '{self.STORAGE_PATH}'")

        with open(self.STORAGE_PATH, "r") as f:
            try:
                written = json.loads(f.read())
            except json.JSONDecodeError as e:
                raise DataError(path=self.STORAGE_PATH, 
                                msg="An error occured while creating storage file.",
                                e=e)

            if written == storage:
                self.ui.relay(f"Succesfully initialized storage file at '{self.STORAGE_PATH}'.")
            else:
                raise DataError(path=self.STORAGE_PATH, msg=f"Expected: {storage}\nActual: {written}")

    def load_data(self):
        ''' Loads from storage file to self.data. '''

        data = {}

        try:
            with open(self.STORAGE_PATH, mode='r') as f:
                data = json.loads(f.read())
        except FileNotFoundError as e:
            self.ui.relay(f"Storage file at '{self.STORAGE_PATH}' not found.")
        except json.JSONDecodeError as e:
            raise DataError(e=e, path=self.STORAGE_PATH, msg="The data in storage file could not be interpreted.")
        except PermissionError as e:
            raise FSError(e=e, path=self.STORAGE_PATH, msg=f"No permission to access storage file. Inspect file permissions for: '{self.STORAGE_PATH}'")
        except Exception as e:
            raise FSError(e=e, path=self.STORAGE_PATH, msg="An unexpected error occurred while loading data.")

        if data:
            self.data = data
            self.STORAGE_BACKUP = copy.deepcopy(self.data)
        else:
            self.ui.relay(message=f"No data loaded from storage file at: '{self.STORAGE_PATH}'.")
            self.ui.relay(message="Attempting to create a new storage file...")

            try:
                self.init_storage_file()
            except (DataError, FSError):
                raise
            
            try:
                self.load_data()
            except (FSError, DataError):
                raise

    def load_group(self, group_id):
        ''' Converts task dicts to Task objects for tasks in group with ID group_id. '''        
        
        try:
            task_ids = self.get_group_tasks(group_id)
        except GroupNotFoundError:
            raise

        for task_id in task_ids:
            try:
                self.load_task(task_id)
            except TaskNotFoundError as e:
                self.remove_task_from_group(task_id, group_id)
                continue

    def load_task(self, task_id):
        ''' Converts task dict to Task object for task with ID task_id. 
        
        Recursively loads parent and subtasks.
        '''
        try:
            if self._is_Task(task_id):
                return
        except TaskNotFoundError:
            raise

        task = Task(self, 
                    task_id=task_id, 
                    taskd=self.data["tasks"][task_id])

        self.data["tasks"][task_id] = task
        
        for subtask_id in self.data["tasks"][task_id].get_subtasks():
            try:
                self.load_task(subtask_id)
            except TaskNotFoundError:
                raise 

        for parent_id in self.data["tasks"][task_id].get_parents():
            try:
                self.load_task(parent_id)
            except TaskNotFoundError:
                raise 

    def orphan_task(self, task_id):
        ''' Removes a task from all parents' subtask attribute. '''
        try:
            self.load_task(task_id)
        except TaskNotFoundError:
            raise

        for parent_id in self.data["tasks"][task_id].get_parents():
            self.data["tasks"][parent_id].remove_subtask(task_id)

    def remove_task(self, task_id):
        ''' Removes a task from all groups, orphans the task 
        and recursively removes all of its subtaskts.
        '''

        for group_id in self.data["groups"].keys():
            self.remove_task_from_group(task_id, group_id)

        try:
            self.load_task(task_id)
        except TaskNotFoundError:
            try:
                self._deep_remove_task(task_id) # A slower method of removal.
            except:
                pass
            
            raise

        self.orphan_task(task_id)
        
        for subtask_id in self.data["tasks"][task_id].get_subtasks():
            try:
                self.remove_task(subtask_id)
            except TaskNotFoundError:
                pass

        self.data["tasks"].pop(task_id)
    
    def remove_task_from_group(self, task_id, group_id):
        ''' Removes a task from a group. '''
        try:
            self.data["groups"][group_id]["task_ids"].remove(task_id)
        except KeyError as e:
            raise GroupNotFoundError(group_id=group_id, e=e)
        except ValueError: # task is not in group
            return

    def update_current_id(self, id):
        ''' Set current ID to id. '''
        self.data["current_id"] = id

    def write_data(self): 
        ''' Writes self.data to storage file. '''

        data = copy.deepcopy(self.data)
        for task_id, task in self.data["tasks"].items():
            if self._is_Task(task_id):    
                data["tasks"][task_id] = task.write_dict()
        
        try:
            with open(self.STORAGE_PATH, mode='w') as f:
                json.dump(data, f) # ? Is ensure_ascii=True necessary?
        except FileNotFoundError as e:
            raise FSError(e=e, path=self.STORAGE_PATH, msg=f"No file found at: '{self.STORAGE_PATH}'")
        except PermissionError as e:
            raise FSError(e=e, path=self.STORAGE_PATH, msg=f"No permission to write to storage file. Inspect file permissions for: '{self.STORAGE_PATH}'")
        except Exception as e:
            raise FSError(e=e, path=self.STORAGE_PATH, msg=f"An unexpected error occured during attempt to write data to storage file at: '{self.STORAGE_PATH}'")

        pass # Todo: check for write success
        # if success, create a new backup with self.STORAGE_BACKUP = copy.deepcopy(data)
        
if __name__ == '__main__':
    class DevUI:
        ''' Simple frontend for development purposes. 
        
        Serves as example for other frontends. Frontends must define the function headers defined here.   
        '''

        def relay(self, message=''):
            ''' Relays a message to the user. '''
            print(message)
        
        def request(self, request_type=bool, message=''):
            ''' Requests information from the user. '''
            def prompt_user(prompt):
                u_in = ''
                while not u_in:
                    u_in = input(prompt)
                return u_in

            print("Please provide:", message)

            if request_type is bool:
                if prompt_user("(Y/n)> ").lower().startswith('y'):
                    return True
                else:
                    return False
            elif request_type is str:                
                return prompt_user("> ")
            elif request_type is int:
                u_in = ''
                while not u_in.isdecimal():
                    u_in = prompt_user("> ")
                return int(u_in)

        def error(self, error='', error_class=None, info='', fatal=False): # ! Currently unused.
            ''' Provides information about an error. 
            
            If fatal=True the error is so severe that the program cannot continue.
            '''

            if error_class:
                print("Class: ", end='')
                print(error_class)

            if error:
                print("Error: ", end='')
                print(error)
            
            if info:
                print("Info: ", end='')
                print(info)

            if fatal:
                print("A fatal error has occured. Exiting without updating storage file.")
                sys.exit()

    master = Master(DevUI())
    
    # Dev ---------------
    try:
        master.load_data()
    except (DataError, FSError) as e:
        print(e)
        sys.exit()
        
    master.write_data()