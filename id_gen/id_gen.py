import csv

def get_settings():
    ''' Return settings from data.csv as a dict. '''

    with open("data.csv", "r") as f:
        dreader = csv.DictReader(f)
        data = dreader.__next__()
    return data

def write_settings(d):
    ''' Write to settings file data.csv from dict. '''
    with open("data.csv", "w") as f:
        writer = csv.DictWriter(f, fieldnames=d.keys())

        writer.writeheader()
        writer.writerow(d)

def generate_id():
    ''' Reads current ID and generates next ID, write as current and return. '''

    data = get_settings()

    try:
        data["CURRENT_ID"] = increment_id(data["CURRENT_ID"])
    except KeyError:
        pass # set ID to 0 or fatal system exit

    pass # if data["CURRENT_ID"] in STORAGE["CONTENTS"].keys(), then an error has occured

    write_settings(data)
    return data["CURRENT_ID"]

def int_to_base(n, base):
    ''' Converts positive int 'n' to string in given 'base' between 10 and 36 inclusive.

    Tested for positive integers between 0 and 200000 inclusive.
    '''

    if base > 36 or base < 10:
        pass #sys.exit()

    alphabet = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
    base_str = ''

    # Decompose the number 'n' into its digits in the given base.
    ## This is similar to repeatedly dividing by 10 to extract digits in base-10,
    ## but generalized to any base between 10 and 36.
    for _ in range(0, (n // base) + 1):
        x = n % base

        if x < 10:
            base_str = str(x) + base_str
        else:
            x = x - 10
            base_str = alphabet[x] + base_str

        n = n // base
        if n < 1:
            break

    # Remove leading '0' unless it is the only char in 'base_str'.
    if len(base_str) > 1:
        base_str = base_str.lstrip('0')

    return base_str

def increment_id(id):
    ''' Increments id string in base-36 by one. '''

    n = int(id, 36) + 1
    id = int_to_base(n, 36)
    return id

for _ in range(0, 2000):
    id = generate_id()
    print(id)
