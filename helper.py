def parsePhiOperator(file_path: str):
    # takes file path phi operator input and parses it into a dictionary object

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

