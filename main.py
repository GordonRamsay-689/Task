import os, sys, json, copy
from task import Task
from globals import *

# TODO: adapt task.py to use master.ui and master._handle_error().
# TODO: check for success on write in write_data()

class Master:
    ''' Manages I/O operations and Task objects. '''
    def __init__(self, ui):
        self.ui = ui

        self.SCRIPT_DIR = self._get_script_dir()
        self.STORAGE_PATH = os.path.join(self.SCRIPT_DIR, "storage.json")

        self.data = {}
        self.load_data()
        self.STORAGE_BACKUP = copy.deepcopy(self.data)

    def _get_script_dir(self):
        ''' Get the directory of main.py '''
        return os.path.abspath(__file__).strip('main.py')

    def _handle_error(self, e=None, error_class=None, data=[]):

        if not error_class:
            error_class = type(e)

        if error_class == FileNotFoundError:
            self.ui.error(error=e, error_class=error_class, info=f"Could not locate file at: '{data[0]}'")
        elif error_class == PermissionError:
            self.ui.error(error=e, error_class=error_class, info=f"No permission to access file at: '{data[0]}'\n{PROGRAM_NAME} needs read and write permissions for all files located in '{self.SCRIPT_DIR}'.")
        elif error_class == GroupNotFoundError:
            self.ui.error(error_class=error_class, info=f"No group found with id: '{data[0]}'")
        elif error_class == TaskNotFoundError:
            self.ui.error(error_class=error_class, info=f"No task found with id: '{data[0]}'")
        else: # Intended for unexpected or unknown errors.
            info = "Unexpected error occured." if not data else data[0]
            self.ui.error(error=e, error_class=error_class, fatal=True, info=info)

    def create_task(self, group_id=None, subtask=False, task_kwargs={}):
        ''' Creates a Task with provided kwargs and updates data. '''
        try:
            task = Task(master=self, **task_kwargs)
        except TypeError as e:
            self._handle_error(e=e)
            return

        self.data["tasks"][task.get_id()] = task

        if not subtask:
            # Adds task to a group if not a subtask
            group_id = self.data["active_group"] if not group_id else group_id

            try:        
                self.data["groups"][group_id]["task_ids"].append(task.get_id())
            except KeyError as e:
                self._handle_error(error_class=GroupNotFoundError, data=[group_id])
                return task.get_id()

        return task.get_id()

    def create_subtask(self, parent_task_id):
        ''' Creates a Task and adds Task id to parent Task's substask set. '''
        task_id = self.create_task(subtask=True, task_kwargs={})
        
        try:
            self.load_task(parent_task_id)
        except KeyError as e:
            self.ui.relay("Aborting subtask creation.")
            self.remove_task(task_id)
            print(master.data["tasks"])
            return

        self.data["tasks"][task_id].add_parent(parent_task_id)
        self.data["tasks"][parent_task_id].add_subtask(task_id)
              
        return task_id
    
    def init_storage_file(self):    
        # IDs are in base 36, hence strings
        storage = {
            "current_id": "0",
            "active_group": "0",
            "groups": {"0": {"task_ids": ["0"], "name": ''}},
            "tasks": {"0": copy.deepcopy(TASKD_TEMPLATE)} 
        }

        with open(self.STORAGE_PATH, "w") as f:
            f.write(json.dumps(storage, ensure_ascii=False))

        with open(self.STORAGE_PATH, "r") as f:
            written = json.loads(f.read())

            if written == storage:
                self.ui.relay(f"Succesfully initialized storage file at '{self.STORAGE_PATH}'.")
            else:
                info = f"Expected: {storage}\nActual: {written}\nFailed to dump or read dumped file"
                self.ui.error(info=info, fatal=True)

    def load_data(self):
        ''' Loads data (tasks and groups) from storage file to self.data. '''

        data = {}

        try:
            with open(self.STORAGE_PATH, mode='r') as f:
                data = json.loads(f.read())
        except json.JSONDecodeError as e:
            self.ui.error(error=e, error_class=type(e), fatal=True, info=f"The stored data at '{self.STORAGE_PATH}' is CORRUPTED.")
        except (FileNotFoundError, PermissionError) as e:
            self._handle_error(e=e, data=[self.STORAGE_PATH])
        except Exception as e:
            self._handle_error(e=e, data=[f"An error occured while reading data from file at '{self.STORAGE_PATH}'."])

        if data:
            self.data = data
        else:
            self.ui.error(info=f"No data loaded from storage at {self.STORAGE_PATH}.")

            kwargs = {"request_type": bool, 
                      "message": "Do you wish to create create an empty storage file?"}
            if self.ui.request(**kwargs) == True:
                self.init_storage_file()
            else:
                self.ui.error(fatal=True, info="Cannot continue without a storage file.")

            self.load_data()

    def write_data(self):
        ''' Writes data (tasks and groups) to storage file. '''

        data = copy.deepcopy(self.data)
        for task_id, task in self.data["tasks"].items():
            if isinstance(task, Task):
                data["tasks"][task_id] = task.write_dict()
        try:
            with open(self.STORAGE_PATH, mode='w') as f:
                json.dump(data, f) # ? Is ensure_ascii=True necessary?
        except (FileNotFoundError, PermissionError) as e:
            self._handle_error(e=e, data=[self.STORAGE_PATH])
        except Exception as e:
            self._handle_error(e=e, data=[f"An error occured while writing data to storage file at: '{self.STORAGE_PATH}'"])

        pass # Todo: check for write success
        # if success, create a new backup with self.STORAGE_BACKUP = copy.deepcopy(data)

    def _is_Task(self, task_id):
        try:
            if isinstance(self.data["tasks"][task_id], Task):
                return True
            else:
                return False
        except KeyError:
            self._handle_error(error_class=TaskNotFoundError, data=[task_id])
            raise

    def load_group(self, group_id):
        ''' Inside self.data: Converts task dicts to Task objects for tasks with matching group_id. '''        
        try:
            task_ids_list = self.data["groups"][group_id]["task_ids"]
        except KeyError:
            self._handle_error(error_class=GroupNotFoundError, data=[group_id])
            raise
        
        for task_id in task_ids_list:
            try:
                self.load_task(task_id)
            except KeyError:
                pass # data corruption warning to self??
                
    def load_task(self, task_id):
        ''' Inside self.data: Converts task dict to Task object for task with matching task_id. '''
        try:
            if self._is_Task(task_id):
                return
        except KeyError:
            raise

        task = Task(self, taskd=self.data["tasks"][task_id])

        self.data["tasks"][task_id] = task
        
        for subtask_id in self.data["tasks"][task_id].get_subtasks():
            try:
                self.load_task(subtask_id)
            except KeyError:
                raise 

        for parent_id in self.data["tasks"][task_id].get_parents():
            try:
                self.load_task(parent_id)
            except KeyError:
                raise 

    def remove_task(self, task_id):
        ''' 
        Removes a task and all of it's subtasks recursively from data["tasks"]. Deletes task from groups and parents' subtasks lists. 
        '''

        for group_id in self.data["groups"].keys():
            self.remove_task_from_group(task_id, group_id)

        try:
            self.load_task(task_id)
        except KeyError:
            self._deep_remove_task(task_id) # A slower method of removal.
            return

        self.orphan_task(task_id)

        for subtask_id in self.data["tasks"][task_id].get_subtasks():
            self.remove_task(subtask_id)

        self.data["tasks"].pop(task_id)

    def _deep_remove_task(self, task_id):
        ''' Goes through all tasks attempting to remove task_id from any substasks and parents lists. If a subtask is found, 
        performs the same operation for it recursively. '''
        for _task_id, task in self.data["tasks"].items():
            
            if not _task_id in self.data["tasks"].keys(): # ! If a subtask has been removed in a deeper recursion layer
                continue

            if self._is_Task(_task_id):
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
        for parent_id in self.data["tasks"][task_id].get_parents():
            self.data["tasks"][parent_id].remove_subtask(task_id)

    def remove_task_from_group(self, task_id, group_id):
        ''' Removes a task from a group. '''
        try:
            self.data["groups"][group_id]["task_ids"].remove(task_id)
        except KeyError as e:
            self._handle_error(e=e, error_class=GroupNotFoundError, data=[group_id])
            return
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
    try:
        master.load_group(master.data["active_group"])
    except KeyError: # ! Later, GroupNotFoundError
        raise