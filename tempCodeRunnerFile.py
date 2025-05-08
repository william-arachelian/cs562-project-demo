 conn = psycopg2.connect(
    dbname=dbname, user=user, password=password, host="localhost", port=5433, cursor_factory=psycopg2.extras.DictCursor)
    