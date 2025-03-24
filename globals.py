
COMPLETED_SYMBOL = 'x'
UNCOMPLETED_SYMBOL = '-'

# OPTION KEYWORDS
OPT_TITLE = "title"
OPT_RESOURCES = "resources"

OPTION_ALIASES = {
    "-t": OPT_TITLE,
    "title": OPT_TITLE,
    "-r": OPT_RESOURCES,
    "resources": OPT_RESOURCES
}

# FUNCTION KEYWORDS
FN_ADD = "add"
FN_REMOVE = "remove"
FN_CLEAR = "clear"
FN_EDIT = "edit"
FN_LIST = "list"
FN_STASH = "stash"

FUNCTIONS = {
    FN_ADD: {
        OPT_TITLE: "",
        OPT_RESOURCES: []
    },
    FN_REMOVE: {}, 
    FN_CLEAR: {}, 
    FN_EDIT: {}, 
    FN_LIST: {}, 
    FN_STASH: {}
}

# TASK KEYS
TSK_KEY_STATUS = "completed"
TSK_KEY_TITLE = "title"
TSK_KEY_COMMENT = "comment"
TSK_KEY_DESCRIPTION = "description"
TSK_KEY_RESOURCES = "resources"
TSK_KEY_ID = "id"

# TABLE KEYS
TBL_KEY_NAME = "name"
TBL_KEY_CONTENTS = "contents"

# CONFIGURABLES
MAX_TITLE_LENGTH = 38
MAX_RESOURCES_TO_DISPLAY = 2

## Base table
TABLE = {TBL_KEY_NAME: "", TBL_KEY_CONTENTS: []}
