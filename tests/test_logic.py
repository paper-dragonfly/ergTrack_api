from apps.api.src.logic import add_new_user, db_connect, add_workout, add_interval, get_users
from pydantic import BaseModel
from apps.api.post_classes import NewUser, NewInterval, NewWorkout
import json
import pdb
from apps.api.tests import conftest as c


def test_add_new_user():
    """
    GIVEN an attempt to make a new user
    WHEN a NewUser instance is passed to add_new_user(db, NewUser)
    THEN assert there is a singel entry in the db that matches that new user
    """
    #create NewUser instance
    test_user = NewUser(user_name='nico', dob='1991-12-01', sex='Male',team_id='1')
    try: 
        conn, cur = db_connect('testing')
        # populate team table with team
        cur.execute("INSERT INTO team(team_id, team_name) VALUES(%s,%s) ON CONFLICT DO NOTHING",('1','tumbleweed'))
        conn.commit()
    finally:
        cur.close()
        conn.close()
    #pass to add_new_user()
    user_id = add_new_user('testing',test_user)
    try:
        conn, cur = db_connect('testing')
        # get test_user data from db 
        cur.execute("SELECT * FROM users WHERE user_name = %s",('nico',))
        nico_data = cur.fetchall()
        assert len(nico_data) == 1
    finally:
        cur.close()
        conn.close()
        c.clear_test_db()


def test_get_users():
    pass # covered in app.py tests 


def test_add_workout():
    """
    GIVEN a POST request has been sumbitted to /addworkout 
    WHEN add_workout function is called with POST data
    THEN workout is added to workout_log table and workout_id is returned
    """
    try:
        # populate db - add user
        conn, cur = db_connect('testing',True)
        sql = "INSERT INTO users(user_id, user_name) VALUES(%s,%s)"
        subs = (1,'sam')
        cur.execute(sql, subs)
        # pass test NewWorkout instance to function
        test_newworkout = NewWorkout(user_id=1,date='2022-06-10',distance=2000,time_sec=600,split=150,intervals=1,comment='slow 2k')
        workout_id = add_workout('testing',test_newworkout)
        # assert workout_id returned - check is int
        assert type(workout_id) == int  
    finally:
        cur.close()
        conn.close()
        c.clear_test_db()

def test_add_interval():
    """
    GIVEN a POST request has been sumbitted to /addinterval 
    WHEN add_interval function is called with POST data
    THEN affirm True is returned indicating interval was added to interval_log table
    """
    try:
        # populate db - add user and partial workout 
        conn, cur = db_connect('testing',True)
        sql = "INSERT INTO users(user_id, user_name) VALUES(%s,%s)"
        subs = (1,'sam')
        cur.execute(sql, subs)
        cur.execute("INSERT INTO workout_log(workout_id) VALUES(1)")
        # create test_intervals data
        test_newinterval = NewInterval(workout_id=1,interval_wo=True, distance=6000,time_sec=1800,split=130,rest=180)
        # pass test_POST data to function
        added_successfully = add_interval('testing',test_newinterval)
        # assert result
        assert added_successfully == True 
        cur.execute("SELECT distance FROM interval_log WHERE workout_id=1") 
        distance = cur.fetchone()[0]
        assert distance == 6000
    finally:
        cur.close()
        conn.close()
        c.clear_test_db()  
