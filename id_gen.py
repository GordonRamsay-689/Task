def generate_id(current_id):
    ''' Reads current ID and generates next ID, write as current and return. '''

    try:
        id  = increment_id(current_id)
    except KeyError:
        pass # set ID to 0 or fatal system exit

    return id

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

