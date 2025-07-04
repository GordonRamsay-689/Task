import os, sys, json, copy
from task import Task
from globals import *

# Custom "errors"
GroupNotFoundError = "GroupNotFound"
TaskNotFoundError = "TaskNotFound"

# TODO: adapt task.py to use master.ui and master.handle_error().
# TODO: check for success on write in write_data()

class Master:
    def __init__(self, ui):
        self.ui = ui

        self.SCRIPT_DIR = self.get_script_dir()
        self.STORAGE_PATH = os.path.join(self.SCRIPT_DIR, "storage.json")

        self.data = {}
        self.load_data()
        self.STORAGE_BACKUP = copy.deepcopy(self.data)

        self.load_group(self.data["active_group"])

        self.main()

    def load_data(self):
        ''' Loads data (tasks and groups) from storage file to self.data. '''

        data = {}

        try:
            with open(self.STORAGE_PATH, mode='r') as f:
                data = json.loads(f.read())
        except FileNotFoundError as e:
            self.handle_error(e, error_type=FileNotFoundError, data=[self.STORAGE_PATH])
        except PermissionError as e:
            self.handle_error(e, error_type=PermissionError, data=[self.STORAGE_PATH])
        except json.JSONDecodeError as e:
            self.ui.error(error=e, fatal=True, info=f"The stored data at '{self.STORAGE_PATH}' is CORRUPTED.")
        except Exception as e:
            self.handle_error(e)

        if data:
            self.data = data
        else:
            self.ui.error(info=f"No data loaded from storage at {self.STORAGE_PATH}.")
            u_in = self.ui.request("Do you wish to create create an empty storage file? (Y/n)")
            if u_in.upper() == 'Y':
                self.init_storage_file()
            self.load_data()

    def write_data(self):
        ''' Writes data (tasks and groups) to storage file. '''

        data = copy.deepcopy(self.data)
        for key, task in self.data["tasks"].items():
            if isinstance(task, Task):
                data["tasks"][key] = task.write_dict()
        try:
            with open(self.STORAGE_PATH, mode='w') as f:
                json.dump(data, f) # ? Is ensure_ascii=True necessary?
        except FileNotFoundError as e:
            self.handle_error(e, error_type=FileNotFoundError, data=[self.STORAGE_PATH])
        except PermissionError as e:
            self.handle_error(e, error_type=PermissionError, data=[self.STORAGE_PATH])
        except Exception as e:
            self.ui.error(error=e, fatal=True, info=f"An error occured while writing data to storage file at: '{self.STORAGE_PATH}'")

        pass # Todo: check for write success
        # if success, create a new backup with self.STORAGE_BACKUP = copy.deepcopy(data)

    def group_name_to_group_id(group_name): # ! TODO
        ''' Transforms group_name to group_id. '''
        pass 

    def load_group(self, group_id):
        ''' Inside self.data: Converts task dicts to Task objects for tasks with matching group_id. '''        
        try:
            task_ids_list = self.data["groups"][group_id]["task_ids"]
        except KeyError:
            self.handle_error(e=None, error_type=GroupNotFoundError, data=[group_id])
            return

        for task_id in task_ids_list:
            self.load_task(task_id)

    def load_task(self, task_id):
        ''' Inside self.data: Converts task dict to Task object for task with matching task_id. '''
        try:
            if isinstance(self.data["tasks"][task_id], Task):
                return
        except KeyError:
            self.handle_error(e=None, error_type=TaskNotFoundError, data=[task_id])
            return
        
        self.data["tasks"][task_id] = Task(self, taskd=self.data["tasks"][task_id])

    def init_storage_file(self):
        from init_storage import init_storage
        init_storage(self.SCRIPT_DIR)

    def get_script_dir(self):
        ''' Get the directory of main.py '''
        return os.path.abspath(__file__).strip('main.py')

    def handle_error(self, e, error_type=None, data=[]):
        if not error_type:
            self.ui.error(error=e, fatal=True, info="Unexpected error occured.")
        elif error_type == FileNotFoundError:
            self.ui.error(error=e, info=f"Could not locate file at: '{data[0]}'")
        elif error_type == PermissionError:
            self.ui.error(error=e, info=f"No permission to access file at: '{data[0]}'/n{PROGRAM_NAME} needs read and write permissions for all files located in '{self.SCRIPT_DIR}'.")
        elif error_type == GroupNotFoundError:
            self.ui.error(info=f"No group found with id: '{data[0]}'")
        elif error_type == TaskNotFoundError:
            self.ui.error(info=f"No task found with id: '{data[0]}'")

    def main(self):
        task = Task(self)
        self.data["tasks"][task.get_id()] = task
        self.write_data()

if __name__ == '__main__':
    class UI:
        ''' Simple frontend for development purposes. 
        
        Serves as example for other frontends. Frontends must define the function headers defined here.   
        '''

        def relay(self, message=''):
            ''' Relays a message to the user. '''
            print(message)
        
        def request(self, message=''):
            ''' Requests information from the user. '''

            print("Please provide:", message)
            u_in = input("> ")
            return u_in

        def error(self, error='', info='', fatal=False):
            ''' Provides information about an error. 
            
            If fatal=True the error is so severe that the program cannot continue. It is recommended for a UI to exit in this situation. 
            '''

            if error:
                print("Error: ", end='')
                print(error)

            if info:
                print("Info: ", end='')
                print(info)

            if fatal:
                print("A fatal error has occured. Exiting without updating storage file.")
                sys.exit()

    ui = UI()

    master = Master(ui)