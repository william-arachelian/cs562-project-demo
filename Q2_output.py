""" Console Output
+--------+---------+---------------+---------------+---------------+
| prod   | state   |   1_sum_quant |   2_avg_quant |   3_sum_quant |
|--------+---------+---------------+---------------+---------------|
| Ham    | PA      |         14526 |       471     |         12280 |
| Fish   | CT      |         14214 |       467.541 |          3489 |
| Apple  | CT      |         14110 |       568.113 |         11010 |
| Jelly  | NJ      |         10331 |       510.24  |          9913 |
| Ham    | NY      |          5450 |       517.887 |          8107 |
| Fish   | NJ      |          6570 |       519.66  |         11601 |
| Dates  | PA      |          7305 |       494.55  |         10136 |
| Butter | NJ      |          6988 |       482.023 |         11584 |
| Jelly  | PA      |          8767 |       524.531 |         12914 |
| Cherry | CT      |         12529 |       508.96  |         11165 |
| Apple  | NJ      |         11880 |       558.016 |         12862 |
| Butter | PA      |         11367 |       539.392 |         18027 |
| Eggs   | CT      |         15815 |       528.018 |          6659 |
| Cherry | NY      |         15966 |       558.773 |         11184 |
| Dates  | CT      |          6212 |       606.755 |         11663 |
| Dates  | NJ      |         12333 |       474.444 |          8901 |
| Grapes | CT      |          8522 |       503.105 |          4991 |
| Ham    | CT      |          7708 |       515.021 |         11944 |
| Grapes | PA      |          7493 |       522.345 |          6213 |
| Ham    | NJ      |         10574 |       556.25  |         10693 |
| Ice    | CT      |          9170 |       443.34  |         10434 |
| Jelly  | CT      |          9341 |       524.583 |          7198 |
| Ice    | NJ      |         10597 |       564.962 |         17075 |
| Apple  | PA      |         12629 |       536.5   |          7913 |
| Eggs   | PA      |         10206 |       525.122 |          9894 |
| Jelly  | NY      |         13569 |       517.712 |         12484 |
| Eggs   | NJ      |          9664 |       462.865 |          9791 |
| Ice    | PA      |          3682 |       532.327 |          7312 |
| Butter | CT      |         12046 |       497.633 |         10333 |
| Cherry | PA      |          8336 |       473.28  |         10720 |
| Dates  | NY      |         14788 |       491.277 |          7499 |
| Ice    | NY      |          7284 |       458.621 |         11167 |
| Grapes | NY      |          5606 |       513.516 |         10858 |
| Grapes | NJ      |          7668 |       449.25  |          9329 |
| Butter | NY      |         13651 |       580.295 |         10875 |
| Apple  | NY      |          9633 |       499.491 |          7015 |
| Cherry | NJ      |          6187 |       509.517 |         12255 |
| Eggs   | NY      |          6183 |       452.341 |         11151 |
| Fish   | PA      |          8216 |       533.033 |          7029 |
| Fish   | NY      |          6094 |       480.196 |         11056 |
+--------+---------+---------------+---------------+---------------+
"""


import os
import psycopg2
import psycopg2.extras
import tabulate
from dotenv import load_dotenv
from helper import inputHandler, createMFStructEntry, lookup
from collections import defaultdict
import re

# DO NOT EDIT THIS FILE, IT IS GENERATED BY generator.py

def query():
    load_dotenv()

    user = os.getenv('DB_USER')
    password = os.getenv('DB_PASSWORD')
    dbname = os.getenv('DB_NAME')

    conn = psycopg2.connect(
    dbname=dbname, user=user, password=password, host="localhost", port=5433, cursor_factory=psycopg2.extras.DictCursor)
    
    cur = conn.cursor()
    cur.execute("SELECT * FROM sales")
    
    phi = {'s': ['prod', 'state', '1_sum_quant', '2_avg_quant', '3_sum_quant'], 'n': 3, 'v': ['prod', 'state'], 'f': ['1_sum_quant', '2_avg_quant', '3_sum_quant'], 'sigma': ['1.month = 6', '2.year = 2018', '3.month = 7']}

    # convert phi from list to dictionary with keys as gv for simpler condition checking
    if 'sigma' in phi.keys():
        original_sigma_list = phi['sigma']
        phi['sigma'] = defaultdict(list)

        for cond in original_sigma_list:
            gv, expr = cond.split('.', 1)
            # Remove all gv prefixes like "1." → "cust", "quant"
            expr = re.sub(r'(?<!\w)(\d+)\.', '', expr)

            # Normalize single '=' to '==', but don't change >=, <=, !=, ==
            expr = re.sub(r'(?<![<>=!])=(?![=])', '==', expr)

            # Lowercase all standalone ANDs
            expr = re.sub(r'AND', 'and', expr, flags=re.IGNORECASE)

            # Append cleaned expression
            phi['sigma'][gv].append(expr.strip())

    MF_Struct = []
    
    
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
    
    #remove any attributes used for calculation and not in select clause
    for entry in MF_Struct:
        for key in list(entry.keys()):
            if key not in phi['s']:
                del entry[key]
    
    
    
    return tabulate.tabulate(MF_Struct,
                        headers="keys", tablefmt="psql")

def main():
    print(query())
    
if "__main__" == __name__:
    main()
    