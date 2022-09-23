from logic import db_connect
import pdb
from dotenv import load_dotenv
import os 

print('Env vars loaded:', load_dotenv())

def create_erg_db():
    conn, cur = db_connect('create_dbs', True)
    cur.execute("SELECT datname FROM pg_database")
    db_list = cur.fetchall()
    if ('erg',) in db_list:
        print('db exists')
    else:
        cur.execute("""CREATE DATABASE erg""")
    cur.close()
    conn.close()


def create_test_db():
    conn, cur = db_connect('create_dbs', True)
    cur.execute("SELECT datname FROM pg_database")
    db_list = cur.fetchall()
    # pdb.set_trace()
    if ('erg_test',) in db_list:
        print('erg_tests db already exists')
    else:
        cur.execute("""CREATE DATABASE erg_test""")
    cur.close()
    conn.close()

# create db tables
def create_team_table(cur):
    cur.execute("""CREATE TABLE IF NOT EXISTS team(
        team_id SERIAL PRIMARY KEY,
        team_name VARCHAR(50) UNIQUE 
        ) """)


def create_users_table(cur):
    cur.execute("""CREATE TABLE IF NOT EXISTS users(
        user_id SERIAL PRIMARY KEY,
        user_name VARCHAR(25) NOT NULL UNIQUE,
        dob DATE,
        sex VARCHAR(8),
        team INTEGER,
        FOREIGN KEY (team) REFERENCES team(team_id)
        )""")
    

def create_workout_log_table(cur):
    cur.execute("""CREATE TABLE IF NOT EXISTS workout_log(
        workout_id SERIAL PRIMARY KEY,
        user_id INTEGER, 
        workout_date DATE,
        time_sec DECIMAL(6,1),
        distance INTEGER,
        split DECIMAL(6,1),
        sr INTEGER,
        hr INTEGER,
        intervals INTEGER,
        comment VARCHAR(255),
        FOREIGN KEY (user_id) REFERENCES users(user_id)
        )""")


def create_interval_log_table(cur):
    cur.execute("""CREATE TABLE IF NOT EXISTS interval_log(
        interval_id SERIAL PRIMARY KEY,
        workout_id INTEGER,
        time_sec DECIMAL(6,1),
        distance INTEGER,
        split DECIMAL(6,1),
        sr INTEGER,
        hr INTEGER,
        rest INTEGER,
        comment VARCHAR(255),
        interval_wo BOOLEAN, 
        FOREIGN KEY (workout_id) REFERENCES workout_log(workout_id))"""
    )


def initialize(db):
    try:
        conn, cur = db_connect(db,True)
        create_team_table(cur)
        create_users_table(cur)
        create_workout_log_table(cur)
        create_interval_log_table(cur)
        print(f'{db} tables created') 
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    create_erg_db()
    create_test_db()
    initialize('dev_local')
    initialize('testing') 
    #populate remote db fm local terminal
    initialize('dev_hybrid') 

