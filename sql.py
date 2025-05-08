import os
import psycopg2
import psycopg2.extras
import tabulate
from dotenv import load_dotenv


def query():
    """
    Used for testing standard queries in SQL.
    """
    load_dotenv()

    user = os.getenv('DB_USER')
    password = os.getenv('DB_PASSWORD')
    dbname = os.getenv('DB_NAME')

    conn = psycopg2.connect(
    dbname=dbname, user=user, password=password, host="localhost", port=5433, cursor_factory=psycopg2.extras.DictCursor)
    
    cur = conn.cursor()
    cur.execute("SELECT cust, max(quant) FROM sales GROUP BY cust")

    return tabulate.tabulate(cur.fetchall(),
                             headers="keys", tablefmt="psql")


def main():
    print(query())


if "__main__" == __name__:
    main()
