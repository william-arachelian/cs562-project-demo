#William Arachelian and Marcus Hom
#I pledge my honor that I have abided by the stevens honor sytem

import re

def parseFileInput(file_path):
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
            continue
        elif line == 'HAVING_CONDITION(G):':
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
    
    for s in phi['f']:
        parts = s.split('_')

        if len(parts) == 3:
            gv, agg, attr = parts
        elif len(parts) == 2:
            gv = ''
            agg, attr = parts

        #check condition on group variable

        if gv and not eval(phi['sigma'][gv][0], {}, row):
            if agg in ('sum', 'count'):
                entry[s] = 0
            elif agg == 'min':
                entry[s] = 2**31 - 1 
            elif agg == 'max':
                entry[s] = -2**31
            elif agg == 'avg':
                sum_key = f"{gv}_sum_{attr}" if gv else f"sum_{attr}"
                count_key = f"{gv}_count_{attr}" if gv else f"count_{attr}"
                entry[sum_key] = 0
                entry[count_key] = 0
                entry[s] = 0
            else:
                entry[s] = None

            continue

        if agg == 'count':
            entry[s] = 1
        elif agg in ('sum', 'max', 'min'):
            entry[s] = row[attr]
        elif agg == 'avg':
            sum_key = f"{gv}_sum_{attr}" if gv else f"sum_{attr}"
            count_key = f"{gv}_count_{attr}" if gv else f"count_{attr}"

            if sum_key not in phi['f']:
                entry[sum_key] = row[attr]
            if count_key not in phi['f']:
                entry[count_key] = 1

            entry[s] = entry[sum_key] / entry[count_key]
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

def generateHavingClauseFilter(g):
    """
    Generates code for filtering MF_Struct based on HAVING clause.

    Args:
        g (str): Having Clause from phi operator

    Returns:
        str: Code to filter MF_Struct if g exists, else comment indicating that theres no HAVING clause.
    """

    if g is None:
        return "# No HAVING clause"

    # Compile regex patterns for reuse
    logical_ops_pattern = re.compile(r'\b(and|or|not)\b', flags=re.IGNORECASE)
    comparison_ops_pattern = re.compile(r'(==|!=|>=|<=|>|<)')

    parts = logical_ops_pattern.split(g)
    parts = [p.strip() for p in parts if p.strip()]

    rebuilt_clause = []

    for element in parts:
        # Check for logical operators using precompiled pattern
        if logical_ops_pattern.fullmatch(element):
            rebuilt_clause.append(element.lower())
            continue

        # Rewrite attributes with comparison ops
        if comparison_ops_pattern.search(element):
            tokens = re.findall(r'\b[\w]+(?:_[\w]+)+\b', element)
            for token in set(tokens):
                element = element.replace(token, f"entry['{token}']")
        
        rebuilt_clause.append(element)

    clause_str = ' '.join(rebuilt_clause)

    return f"""
    #Filter MF_Struct by HAVING clause
    MF_Struct = [entry for entry in MF_Struct if {clause_str}]
    """

def generateBody(phi):
    """
    Generates algorithm code for iterating over database and filling in MF_Struct entries

    Args:
        phi (dict): phi operator

    Returns:
        str: Algorithm code 
    """


    body = """
    for row in cur:
        # create a tuple of current row's grouping attribute values
        grouping_key = tuple(row[attr] for attr in phi['v'])

        # search MF_Struct to see if grouping_key already exists
        search_index = lookup(MF_Struct, phi['v'], grouping_key)

        # if it does not exist, create an entry in MF_Struct list
        if search_index == -1:
          
            new_entry = createMFStructEntry(phi, row)
            MF_Struct.append(new_entry)

        # if it already exists, update aggregates based on attribute values
        else:
            for s in phi['f']:
                parts = s.split('_')

                if len(parts) == 3:
                    gv, agg, attr = parts
                elif len(parts) == 2:
                    gv = ''
                    agg, attr = parts
                else:
                    raise ValueError(f"Unexpected aggregate format: {s}")
                
                if gv in phi.get('sigma', {}):
                    conditions = phi['sigma'][gv]
                    if not all(eval(cond, {}, row) for cond in conditions):
                        continue  # Skip update if condition not met
        
                if agg == 'count':
                    MF_Struct[search_index][s] += 1

                elif agg == 'sum':
                    MF_Struct[search_index][s] += row[attr]

                elif agg == 'min':
                    MF_Struct[search_index][s] = min(MF_Struct[search_index][s], row[attr])

                elif agg == 'max':
                    MF_Struct[search_index][s] = max(MF_Struct[search_index][s], row[attr])

                elif agg == 'avg':

                    sum_key = f"{gv}_sum_{attr}" if gv else f"sum_{attr}"
                    count_key = f"{gv}_count_{attr}" if gv else f"count_{attr}"

                    if sum_key not in phi['f']:
                        MF_Struct[search_index][sum_key] += row[attr]
                    if count_key not in phi['f']:
                        MF_Struct[search_index][count_key] += 1

                    MF_Struct[search_index][s] = MF_Struct[search_index][sum_key] / MF_Struct[search_index][count_key]

                else:
                    MF_Struct[search_index] = None
    """

    cleanUp = """
    #remove any attributes used for calculation and not in select clause
    for entry in MF_Struct:
        for key in list(entry.keys()):
            if key not in phi['s']:
                del entry[key]
    
    """

    havingClause= generateHavingClauseFilter(phi['g']) if 'g' in phi.keys() else ""

    return body + havingClause + cleanUp
