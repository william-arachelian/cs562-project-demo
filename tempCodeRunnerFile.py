dbname=dbname,
    user=user,
    password=password,
    host="localhost",  # important to force TCP
    port=5432,
    cursor_factory=psycopg2.extras.DictCursor