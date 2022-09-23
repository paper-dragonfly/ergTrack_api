import json 
from apps.api.tests import conftest as c
from apps.api.src.logic import add_new_user, db_connect, add_workout, add_interval, get_users
from pydantic import BaseModel
import pdb
from apps.api.post_classes import NewUser, NewInterval, NewWorkout


def test_01_users_GET(client):
    """
    GIVEN a flask app
    WHEN a GET request is submitted to /users
    THEN assert return dict includes body key with all user info
    """
    try:
        #populate db with two users
        conn, cur= db_connect('testing', True)
        cur.execute("INSERT INTO team(team_id,team_name) VALUES (%s,%s),(%s,%s) ON CONFLICT DO NOTHING", (1,'utah crew', 2, 'tumbleweed'))
        cur.execute("INSERT INTO users(user_id, user_name, dob, sex, team) VALUES(%s,%s,%s,%s,%s),(%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING", (1,'kaja','1994-12-20','Female',1,2,'moonshine','1991-01-01','Male',2))
        # mak
        # send GET request for user_id 
        response = client.get("/users")
        assert response.status_code == 200        
        data_dict = json.loads(response.data.decode("ASCII"))
        assert data_dict['body']['user_name'] == ['kaja','moonshine']
    finally:
        c.clear_test_db
        cur.close()
        conn.close()


def test_users_POST(client):
    """
    GIVEN a flask app
    WHEN POST submits new user information 
    THEN assert returns user_id and 200 status code
    """
    response = client.post("/users", data=json.dumps({"user_name":'nico', "dob":"1991-12-01", "sex":'Male',"team_id":'2'}), content_type='application/json') 
    assert response.status_code == 200
    c.clear_test_db()


def test_workoutlog_GET(client):
    """
    GIVEN a flask app
    WHEN GET submits user_id
    THEN assert returns all workouts for that user_id 
    """
    # populate db with user and workouts
    try:
        conn, cur = db_connect('testing',True)
        # add user
        cur.execute("INSERT INTO users(user_id, user_name) VALUES(%s,%s)",(4,'lizzkadoodle'))
        # add workout
        cur.execute("INSERT INTO workout_log(workout_id, user_id, workout_date, distance, time_sec,split,sr,hr,intervals,comment) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(1,4,'2022-01-01', 2000,480,120,30,155,1,'PR'))
        conn.commit()
        # send GET request with user_id to /workoutlog and capture response
        response = client.get("/workoutlog?user_id=4") 
        # confirm request was successful
        assert response.status_code == 200
        # Confirm content is as expected
        assert 'PR' in response.data.decode("ASCII")
    finally:
        conn.close()
        cur.close()   
        # clear db
        c.clear_test_db()

def test_workoutlog_POST(client):
    """
    GIVEN a flask app 
    WHEN POST with workout info submitted to /addworkout
    THEN assert workout is added to db and workout_id is returned
    """
    try:
        # populate db - user
        conn, cur = db_connect('testing',True)
        sql = "INSERT INTO users(user_id, user_name) VALUES(%s,%s)"
        subs = (1,'sam')
        cur.execute(sql, subs)
        POST_dict = {'user_id':1,'date':'2022-06-14','distance':500,'time_sec':110, 'split':110, 'intervals':4,'comment':'4x500m'}
        # pass POST to flask func
        response = client.post("/workoutlog", data=json.dumps(POST_dict), content_type='application/json')
        data_dict = json.loads(response.data.decode("ASCII")) # status_code, workout_id
        assert response.status_code == 200
        assert type(data_dict['workout_id']) == int
    finally:
        cur.close()
        conn.close()
        c.clear_test_db()


def test_addinterval(client):
    """
    GIVEN a flask app 
    WHEN POST with interval info submitted to /addinterval
    THEN interval is added to db and True is returned
    """
    try:
        # populate db - user
        conn, cur = db_connect('testing',True)
        sql = "INSERT INTO users(user_id, user_name) VALUES(%s,%s)"
        subs = (1,'sam')
        cur.execute(sql, subs)
        cur.execute("INSERT INTO workout_log(workout_id) VALUES(1)")
        # create interval data POST
        POST_dict = {'workout_id':1,'interval_wo':'True','distance':510,'time_sec':120.0,'split':125.9,'rest':60}
        # pass POST to flask func
        response = client.post("/addinterval", data=json.dumps(POST_dict), content_type='application/json')
        data_dict = json.loads(response.data.decode("ASCII")) # status_code, message, success
        assert response.status_code == 200
        assert data_dict['success'] == True
    finally:
        cur.close()
        conn.close()
        c.clear_test_db()


def test_details(client):
    """
    GIVEN a flask app
    WHEN GET submits workout_id
    THEN assert returns interval and summary stas for that workout_id 
    """ # NOTE: not actually asserting info is correct...just that length is as expected and status_code == 200
    try: 
        # populate db: workout_log
        conn, cur = db_connect('testing',True)
        cur.execute("INSERT INTO workout_log(workout_id,distance,time_sec,split,intervals) VALUES(1,1000,440,110,2)")
        # populate db: interval_log
        cur.execute("INSERT INTO interval_log(workout_id,interval_wo,distance,time_sec,split) VALUES(1,True,1000,224,112),(1,True,1000,216,108)")
        # sent GET requ with workout_id to /details capture result
        response = client.get("/details?workout_id=1")
        assert response.status_code == 200
        data_dict = json.loads(response.data.decode("ASCII"))
        assert len(data_dict['intervals'])==2 and len(data_dict['workout_summary'])==10 #num cols in wo_log
    finally:
        cur.close()
        conn.close()
        c.clear_test_db()


def test_userstats(client):
    """
    GIVEN a flask app
    WHEN GET request submits user_id
    THEN assert returns summary data for user
    """
    try:
        # populate db with team, user, three matching workouts, one not matching
        conn, cur = db_connect('testing',False)
        cur.execute("INSERT INTO team(team_id, team_name) VALUES(1, 'UtahCrew')")
        cur.execute("INSERT INTO users(user_id, user_name, team) VALUES(%s,%s,%s)",(1,'kaja',1))
        cur.execute("INSERT INTO users(user_id, user_name, team) VALUES(%s,%s,%s)",(2,'Nico',1))
        cur.execute("INSERT INTO workout_log(workout_id, user_id, workout_date, distance, time_sec, split,intervals,comment) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)",(1,1,'2022-01-01', 2000,480,120,1,'2k PR'))
        cur.execute("INSERT INTO workout_log(workout_id, user_id, workout_date, distance, time_sec, split,intervals,comment) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)",(2,1,'2022-01-02', 2000,488,122,1,'2k'))
        cur.execute("INSERT INTO workout_log(workout_id, user_id, workout_date, distance, time_sec,split,intervals,comment) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)",(3,1,'2022-01-05', 18000,1800,130,3,'3x30min'))
        cur.execute("INSERT INTO workout_log(workout_id, user_id, workout_date, distance, time_sec, split, intervals,comment) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)",(4,2,'2022-01-01', 2000,484,121,1,'Nico 2k'))
        conn.commit() 

        # pass GET to flask func
        response = client.get("/userstats?user_id=1")
        data_dict = json.loads(response.data.decode("ASCII"))
        # check for expected results
        assert response.status_code == 200
        assert data_dict['distance'] == 22000
        assert data_dict['user_team'] == ['UtahCrew']
    finally:
        cur.close()
        conn.close()
        c.clear_test_db()













    
    