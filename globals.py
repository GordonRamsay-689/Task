# Configurable variables.
MAX_TITLE_LENGTH = 38
MAX_RESOURCES_TO_DISPLAY = 2

# Option Keywords
OPT_DETAILED = "detailed"
OPT_ID = "id"
OPT_RESOURCES = "resources"
OPT_TITLE = "title"

OPTION_ALIASES = {
    "-t": OPT_TITLE,
    "-title": OPT_TITLE,
    "-r": OPT_RESOURCES,
    "-resources": OPT_RESOURCES,
    "-id": OPT_ID
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
        OPT_RESOURCES: []
    },
    FN_REMOVE: {
        OPT_TITLE: "",
        OPT_ID: 0
    }, 
    FN_CLEAR: {}, 
    FN_EDIT: {}, 
    FN_LIST: {
        OPT_DETAILED: True
    }, 
    FN_STASH: {}
}

# Task
TSK_STATUS = "completed"
TSK_TITLE = "title"
TSK_COMMENT = "comment"
TSK_DESCRIPTION = "description"
TSK_RESOURCES = "resources"
TSK_ID = "id"

COMPLETED_SYMBOL = 'x'
UNCOMPLETED_SYMBOL = '-'

# Table
TBL_NAME = "name"
TBL_CONTENTS = "contents"

TABLE = {TBL_NAME: "", TBL_CONTENTS: []}