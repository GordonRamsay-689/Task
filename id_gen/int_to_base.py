import sys

def int_to_base(n, base):
    ''' Converts positive int 'n' to string in given 'base' between 10 and 36 inclusive.

    Tested for positive integers between 0 and 200000 inclusive.
    '''

    if base > 36 or base < 10:
        pass #sys.exit()

    alphabet = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
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

print("\nLOOP")
print(int_to_base("1461931500", 36))
print("\nNO ERRORS")
