import psycopg2 as data

def write_data(query, params):
    conn = data.connect("dbname=tic-tac-toe user=pi")
    cur = conn.cursor()
    cur.execute(query , params)
    conn.commit()
    cur.close()
    conn.close()

def fetch_data(query):
    conn = data.connect("dbname=tic-tac-toe user=pi")
    cur = conn.cursor()
    cur.execute(query)
    result = cur.fetchall()
    cur.close()
    conn.close()
    return result

def fetch_data_with_param(query , param):
    conn = data.connect("dbname=tic-tac-toe user=pi")
    cur = conn.cursor()
    cur.execute(query, param)
    result = cur.fetchall()
    cur.close()
    conn.close()
    return result

    