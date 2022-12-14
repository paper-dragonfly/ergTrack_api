import pytest
from src.api_ergTrack.app import create_app
from src.api_ergTrack.logic import db_connect
import pdb

app = create_app('testing')

@pytest.fixture
def client():
    return app.test_client()

    
def clear_test_db():
    try: 
        conn, cur = db_connect('testing', True)
        cur.execute("DELETE FROM interval_log *")
        cur.execute("DELETE FROM workout_log *")
        cur.execute("DELETE FROM users *")
        cur.execute("DELETE FROM team *")
    finally:
        cur.close()
        conn.close()
        
   
def clear_game_db(cur): 
    try:
        conn, cur = db_connect('testing', True)
        cur.execute("DELETE FROM interval_log *")
        cur.execute("DELETE FROM workout_log *")
        cur.execute("DELETE FROM users *")
        cur.execute("DELETE FROM team *")
    finally:
        cur.close()
        conn.close() 


def delete_test_db():
    conn, cur = db_connect('testing',True)
    cur.execute("""DROP DATABASE "erg_test" """)
    cur.close()
    conn.close()
