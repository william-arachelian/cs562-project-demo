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

def createMFStructEntry(phi, row):
    """
    Creates a new MF_Struct row (dict) initialized with grouping attributes and default aggregate values.

    Args:
        phi (dict): The parsed phi operator input.
        row (dict): The current database row being processed.

    Returns:
        dict: Initialized entry for MF_Struct.
    """
    entry = {}

    for attr in phi['v']:
        entry[attr] = row[attr]

    for s in phi['s']:
        if s in phi['v']: 
            continue

        _gv, func, attr = s.split('_')
        if func == 'count':
            entry[s] = 0
        elif func in ('sum', 'avg'):
            entry[s] = 0
        elif func == 'max':
            entry[s] = float('-inf')
        elif func == 'min':
            entry[s] = float('inf')
        else:
            entry[s] = None

    return entry



def lookup(MF_Struct, grouping_attrs, grouping_key):
    """
    Finds the index of the entry in mf_struct that matches the given grouping key.

    Args:
        MF_Struct (list[dict]): The MF_Struct list of grouping entries.
        grouping_attrs (list[str]): List of grouping attribute names (phi['v']).
        grouping_key (tuple): Tuple of grouping attribute values.

    Returns:
        int: Index of the matching entry if found, else -1.
    """

    for i, entry in enumerate(MF_Struct):
        if all(entry[attr] == val for attr, val in zip(grouping_attrs, grouping_key)):
            return i
    return -1

def generateBody():
    body = """
    phi = inputHandler()

    MF_Struct = []

    for row in cur:
        #create a tuple of current rows grouping attribute values
        grouping_key = tuple(row[attr] for attr in phi['v'])

        #search MF_Struct to see if grouping_key already exists
        search = lookup(MF_Struct, phi['v'], grouping_key)

        if search == -1:
            new_entry = createMFStructEntry(phi, row)
            MF_Struct.append(new_entry)
            
        
        #[TODO: if already in MF_Struct, update aggregate function]
    print(MF_Struct)
    """

    return body