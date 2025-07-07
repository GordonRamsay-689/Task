import os, sys, json, copy
from task import Task
from id_gen import increment_id
from globals import *

# TODO: check for success on write in write_data()

def _construct_error_str(desc, msg):
    text = f"Error: {desc}"
    
    if msg:
        text += f"\nInfo: {msg}"

    return text

class GroupNotFoundError(Exception):
    def __init__(self, group_id, task_id=None, e=None, msg=""):
        self.e = e
        self.group_id = group_id
        self.task_id = task_id
        self.msg = msg
        super().__init__(self.msg)

    def __str__(self):
        return _construct_error_str(f"No group id found with id: '{self.group_id}'", self.msg)

class TaskNotFoundError(Exception):
    def __init__(self, task_id, e=None, msg=""):
        self.e = e
        self.task_id = task_id
        self.msg = msg
        super().__init__(self.msg)

    def __str__(self):
        return _construct_error_str(f"No task found with id: '{self.task_id}'", self.msg)

class TaskCreationError(Exception):
    ''' An error occured during task creation. '''
    def __init__(self, task_id, e=None, msg=""):
        self.e = e
        self.task_id = task_id
        self.msg = msg
        super().__init__(self.msg)

    def __str__(self):
        return _construct_error_str(f"Failed to create task with id: '{self.task_id}'", self.msg)
    
class DataError(Exception): # ? On DataError, restore master.STORAGE_BACKUP 
    ''' Data is corrupted or otherwise unexpected. '''
    def __init__(self, path=None, task_id=None, e=None, msg=""):
        self.path = path
        self.e = e
        self.task_id = task_id
        self.msg = msg
        super().__init__(self.msg)

    def __str__(self):
        return _construct_error_str(f"Data is corrupt.", self.msg)

class FSError(Exception):
    ''' A filesystem error occured. '''
    def __init__(self, path, task_id=None, e=None, msg=""):
        self.path = path
        self.e = e
        self.task_id = task_id
        self.msg = msg
        super().__init__(self.msg)

    def __str__(self):
        return _construct_error_str(f"An error occured while accessing file at: '{self.path}'.", self.msg)

class Master:
    ''' Manages I/O operations and Task objects. '''
    def __init__(self, ui):
        self.ui = ui

        self.SCRIPT_DIR = self._get_script_dir()
        self.STORAGE_PATH = os.path.join(self.SCRIPT_DIR, "storage.json")

        self.data = {}

    def _get_script_dir(self):
        ''' Get the directory of main.py '''
        return os.path.abspath(__file__).strip('main.py')

    def _handle_error(self, e=None, error_class=None, data=[]): # TODO: replace with raise

        if not error_class:
            error_class = type(e)

        if error_class == FileNotFoundError:
            self.ui.error(error=e, error_class=error_class, info=f"Could not locate file at: '{data[0]}'")
        elif error_class == PermissionError:
            self.ui.error(error=e, error_class=error_class, info=f"No permission to access file at: '{data[0]}'\n{PROGRAM_NAME} needs read and write permissions for all files located in '{self.SCRIPT_DIR}'.")
        else: # Intended for unexpected or unknown errors.
            info = "Unexpected error occured." if not data else data[0]
            self.ui.error(error=e, error_class=error_class, fatal=True, info=info)

    def create_task(self, group_id=None, subtask=False, task_kwargs={}):
        ''' Creates a Task with provided kwargs and updates data. '''
        if group_id and subtask:
            raise TaskCreationError(task_id=None, e=TypeError, msg="Argument Error: A task cannot be both a subtask and part of a group.")

        try:
            task = Task(master=self, **task_kwargs)
        except (TypeError, ValueError) as e:
            task_id = increment_id(self.data["current_id"])
            raise TaskCreationError(task_id=task_id, e=e,
                                    msg=f"Error with argument passed to Task.__init__(): '{task_kwargs}'.")

        task_id = task.get_id()
        
        self.data["tasks"][task_id] = task

        if group_id:
            try:
                self.add_task_to_group(task_id, group_id)
            except GroupNotFoundError as e:
                e.msg += f"\nTask with id '{task_id}' was created but not succesfully added to any group or given a parent task."
                raise
            
        return task_id

    def add_task_to_group(self, task_id, group_id): 
        error_message = f"Failed to add task with id '{task_id}' to group with id '{group_id}'."

        if not task_id in self.data["tasks"]:
            raise TaskNotFoundError(task_id=task_id, msg=error_message)
        
        try:        
            self.data["groups"][group_id]["task_ids"].append(task_id)
        except KeyError as e:
            raise GroupNotFoundError(group_id=group_id, task_id=task_id, msg=error_message, e=e)

    def create_subtask(self, parent_task_id):
        ''' Creates a Task and adds Task id to parent Task's substask set. '''
        task_id = self.create_task(subtask=True)
         
        try:
            self.load_task(parent_task_id)
        except TaskNotFoundError as e:
            e.msg = f"Could not make task with id '{task_id}' a subtask of task with id '{parent_task_id}'. Removing task with id '{task_id}'."
            self.remove_task(task_id)            
            raise

        self.data["tasks"][task_id].add_parent(parent_task_id)
        self.data["tasks"][parent_task_id].add_subtask(task_id)
    
    def init_storage_file(self):
        # IDs are in base 36, hence strings
        storage = {
            "current_id": "0",
            "active_group": "0",
            "groups": {"0": {"task_ids": ["0"], "name": ''}},
            "tasks": {"0": copy.deepcopy(TASKD_TEMPLATE)} 
        }

        try:
            with open(self.STORAGE_PATH, "w") as f:
                f.write(json.dumps(storage, ensure_ascii=False))
        except FileNotFoundError as e:
            raise FSError(e=e, path=self.STORAGE_PATH, msg="A file system error occured during creation of storage file.")
        except PermissionError as e:
            raise FSError(e=e, path=self.STORAGE_PATH, msg=f"No permission to create storage file. Inspect file permissions for: '{self.STORAGE_PATH}'")

        with open(self.STORAGE_PATH, "r") as f:
            written = json.loads(f.read())

            if written == storage:
                self.ui.relay(f"Succesfully initialized storage file at '{self.STORAGE_PATH}'.")
            else:
                raise DataError(path=self.STORAGE_PATH, msg=f"Expected: {storage}\nActual: {written}\n")

    def load_data(self):
        ''' Loads data (tasks and groups) from storage file to self.data. '''

        data = {}

        try:
            with open(self.STORAGE_PATH, mode='r') as f:
                data = json.loads(f.read())
        except FileNotFoundError as e:
            self.ui.relay(f"Storage file at '{self.STORAGE_PATH}' not found.")
        except json.JSONDecodeError as e:
            raise DataError(e=e, path=self.STORAGE_PATH, msg=f"The data in storage file could not be interpreted.")
        except PermissionError as e:
            raise FSError(e=e, path=self.STORAGE_PATH, msg=f"No permission to access storage file. Inspect file permissions for: '{self.STORAGE_PATH}'")
        except Exception as e:
            raise FSError(e=e, path=self.STORAGE_PATH, msg="An unexpected error occurred while loading data.")

        if data:
            self.data = data
            self.STORAGE_BACKUP = copy.deepcopy(self.data)
        else:
            self.ui.relay(message=f"No data loaded from storage at: '{self.STORAGE_PATH}'.")
            self.ui.relay(message=f"Attempting to create a new storage file...")

            try:
                self.init_storage_file()
            except (DataError, FSError):
                raise
            
            self.load_data()

    def write_data(self): 
        ''' Writes data (tasks and groups) to storage file. '''

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

    def _is_Task(self, task_id):
        try:
            if isinstance(self.data["tasks"][task_id], Task):
                return True
            else:
                return False
        except KeyError as e:
            raise TaskNotFoundError(task_id=task_id, e=e)

    def load_group(self, group_id):
        ''' Inside self.data: Converts task dicts to Task objects for tasks with matching group_id. '''        
        
        try:
            task_ids = self.get_group_tasks(group_id)
        except GroupNotFoundError:
            raise

        failed = []
        for task_id in task_ids:
            try:
                self.load_task(task_id)
            except TaskNotFoundError as e:
                failed.append(e)
                continue
        
        if failed:
            pass # Todo: raies them all or raise one and pass along their ids

    def get_group_tasks(self, group_id):
        try:
            task_ids = self.data["groups"][group_id]["task_ids"]
        except KeyError as e:
            raise GroupNotFoundError(group_id=group_id, e=e)
        
        return task_ids
        
    def get_active_group(self):
        return self.data["active_group"]
    
    def get_current_id(self):
        return self.data["current_id"]
    
    def load_task(self, task_id):
        ''' Inside self.data: Converts task dict to Task object for task with matching task_id. '''
        try:
            if self._is_Task(task_id):
                return
        except TaskNotFoundError:
            raise

        task = Task(self, taskd=self.data["tasks"][task_id])

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

    def remove_task(self, task_id):
        ''' 
        Removes a task and all of it's subtasks recursively from data["tasks"]. Deletes task from groups and parents' subtasks lists. 
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

    def _deep_remove_task(self, task_id):
        ''' Goes through all tasks attempting to remove task_id from any substasks and parents lists. If a subtask is found, 
        performs the same operation for it recursively. '''
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

    def orphan_task(self, task_id):
        ''' Removes a task from all parents' subtask lists. '''
        try:
            self.load_task(task_id)
        except TaskNotFoundError:
            raise

        for parent_id in self.data["tasks"][task_id].get_parents():
            self.data["tasks"][parent_id].remove_subtask(task_id)

    def remove_task_from_group(self, task_id, group_id):
        ''' Removes a task from a group. '''
        try:
            self.data["groups"][group_id]["task_ids"].remove(task_id)
        except KeyError as e:
            raise GroupNotFoundError(group_id=group_id, e=e)
        except ValueError: # task is not in group
            return

    def update_current_id(self, id):
        ''' Set current id to id. Called by Task. '''
        self.data["current_id"] = id

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

        def error(self, error='', error_class=None, info='', fatal=False):
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