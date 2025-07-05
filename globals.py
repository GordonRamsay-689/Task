PROGRAM_NAME = "ctd"

# Configurable variables.
MAX_TITLE_LENGTH = 38
MAX_RESOURCES_TO_DISPLAY = 2

# Option Keywords
OPT_DETAILED = "detailed"
OPT_GROUP = "group"
OPT_ID = "id"
OPT_INDEX = "index"
OPT_RESOURCES = "resources"
OPT_TITLE = "title"

OPTION_ALIASES = {
    "-t": OPT_TITLE,
    "-title": OPT_TITLE,
    "-r": OPT_RESOURCES,
    "-resources": OPT_RESOURCES,
    "-id": OPT_ID,
    "-n": OPT_INDEX,
    "-g": OPT_GROUP
}

# Function Keywords
FN_ADD = "add"
FN_REMOVE = "rm"
FN_CLEAR = "clear"
FN_EDIT = "edit"
FN_LIST = "list"
FN_STASH = "stash"

FUNCTIONS = {
    FN_ADD: {
        OPT_TITLE: "",
        OPT_RESOURCES: [],
        OPT_GROUP: ""
    },
    FN_REMOVE: {
        OPT_TITLE: "",
        OPT_ID: "0",
        OPT_INDEX: 0,
    }, 
    FN_CLEAR: {}, 
    FN_EDIT: {}, 
    FN_LIST: {
        OPT_DETAILED: True
    }, 
    FN_STASH: {}
}

# Task
TSK_COMMENTS = "comment"
TSK_DESCRIPTION = "description"
TSK_RESOURCES = "resources"
TSK_STATUS = "completed"
TSK_SUBTASKS = "subtasks"
TSK_TITLE = "title"

TASKD_TEMPLATE = {
    TSK_COMMENTS: [], 
    TSK_DESCRIPTION: "", 
    TSK_RESOURCES: [],
    TSK_STATUS: False, 
    TSK_SUBTASKS: [],
    TSK_TITLE: ""
}

COMPLETED_SYMBOL = 'x'
UNCOMPLETED_SYMBOL = '-'

# Custom "errors"
GroupNotFoundError = "GroupNotFound"
TaskNotFoundError = "TaskNotFound"