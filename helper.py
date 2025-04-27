def parseFileInput(file_path: str):
    """
    Parses a file containing phi operator input into a dictionary.

    Args:
        file_path (str): Path to the input file.

    Returns:
        dict: A dictionary with the following structure:
            {
                's': list[str],
                'n': int,
                'v': list[str],
                'f': list[str],
                'sigma': list[str],
                'g': str
            }
    """
    phi = dict()

    with open(file_path, 'r') as f:
        contents = [line.strip() for line in f if line.strip()]

    i = 0
    while i < len(contents):
        line = contents[i]
        if line == 'SELECT ATTRIBUTE(S):':
            phi['s'] = contents[i + 1].split(', ')
            i += 1
        elif line == 'NUMBER OF GROUPING VARIABLES(n):':
            phi['n'] = int(contents[i + 1])
            i += 1
        elif line == 'GROUPING ATTRIBUTES(V):':
            phi['v'] = contents[i + 1].split(', ')
            i += 1
        elif line == 'F-VECT([F]):':
            phi['f'] = contents[i + 1].split(', ')
            i += 1
        elif line == 'SELECT CONDITION-VECT([σ]):':
            phi['sigma'] = []
            i += 1
            while i < len(contents) and contents[i] != 'HAVING_CONDITION(G):':
                phi['sigma'].append(contents[i])
                i += 1
        elif line == 'HAVING_CONDITION(G):':
            if i + 1 < len(contents):
                phi['g'] = contents[i + 1]
                i += 1
        i += 1

    return phi

def inputHandler():
    """
    handles whether user chooses to input a file containing phi operator or manually enter phi operator 

    Args:
        None

    Returns:
        dict: A dictionary with the following structure:
            {
                's': list[str],
                'n': int,
                'v': list[str],
                'f': list[str],
                'sigma': list[str],
                'g': str
            }
    """
    choice = 'invalid'
    while choice == 'invalid':
        choice = input("How would you like to handle input?\n\t[f]: file input\n\t[m]: manual input\n")
        if (choice != 'f') and (choice != 'm'):
            print(choice," is not a valid input.")
            choice = 'invalid'

    if choice == 'f':
        fpath = input("enter file path:")
        return parseFileInput(fpath)

    if choice == 'm':
        phi = dict()
        print("Enter [list] inputs by separating by a ', '. Enter aggregates in the form [group_var]_[aggregate]_[attribute]:")
        phi['s'] = input("SELECT ATTRIBUTE(S) [list]: ").split(', ')
        phi['n'] = int(input("NUMBER OF GROUPING VARIABLES(n): "))
        phi['v'] = input("GROUPING ATTRIBUTES(V) [list]: ").split(', ')
        phi['f'] = input("F-VECT([F]) [list]: ").split(', ')
        phi['sigma'] = input("SELECT CONDITION-VECT([σ]) [list]: ").split(', ')
        phi['g'] = input("HAVING_CONDITION(G) [list]: ")

        return phi