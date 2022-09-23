import json
import yaml
import psycopg2 
from apps.api.post_classes import NewInterval, NewUser, NewWorkout
import pdb 
import os
from dotenv import load_dotenv

load_dotenv() 

# get database parameters
def config(db:str='dev_local', config_file:str='apps/api/config/config.yaml')-> dict:
    with open(f'{config_file}', 'r') as f:
        config_dict = yaml.safe_load(f) 
    db_params = config_dict[db]
    return db_params 


# connect to database
def db_connect(db:str, autocommit:bool = False):
    if db == 'production':
        conn = psycopg2.connect(os.getenv('DB_CONN_STR_INT'))    
    elif db == 'dev_hybrid':
        conn = psycopg2.connect(os.getenv('DB_CONN_STR_EXT'))
    else:
        params = config(db)
        conn = psycopg2.connect(**params)
    cur = conn.cursor()
    conn.autocommit = autocommit
    return conn, cur


# add new user to db
def add_new_user(db:str, resp_newuser:NewUser)->int:
    user_id = 0
    try:
        conn, cur = db_connect(db)
        #check if user already exists
        cur.execute('SELECT user_name FROM users')
        usernames = cur.fetchall()
        for i in range(len(usernames)):
            if usernames[i][0] == resp_newuser.user_name: 
                return 0
        # add user 
        cur.execute("INSERT INTO users(user_name, dob, sex, team) VALUES(%s,%s,%s,%s)",(resp_newuser.user_name, resp_newuser.dob, resp_newuser.sex,resp_newuser.team_id))
        cur.execute("SELECT user_id FROM users WHERE user_name=%s",(resp_newuser.user_name,))
        user_id = cur.fetchone()[0]
        conn.commit()
    finally: 
        conn.close()
        cur.close()
        return user_id


#Get user info given ID
def get_users(db:str)->tuple:
    user_dict={'user_id':[], 'user_name':[], 'dob':[],'sex':[],'team':[]}
    try:
        conn, cur = db_connect(db)
        cur.execute("SELECT * FROM users")
        uinfo = cur.fetchall()
        # if no user_name maches given user_id
        if not uinfo:
            status_code = 404
        else:  
            for i in range(len(uinfo)): 
                user_dict['user_id'].append(uinfo[i][0])
                user_dict['user_name'].append(uinfo[i][1])
                user_dict['dob'] .append(str(uinfo[i][2]))
                user_dict['sex'].append(uinfo[i][3])
                user_dict['team'].append(uinfo[i][4])
            status_code = 200
    finally:
        cur.close()
        conn.close()
        return status_code, user_dict


# add workout to workout_log
def add_workout(db:str, workout_inst:NewWorkout)->int:
    try:
        # connect to db
        conn, cur = db_connect(db, True)
        # add workout data to workout_log table
        sql = "INSERT INTO workout_log(user_id, workout_date, distance, time_sec, split, sr, hr, intervals, comment) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        subs = (workout_inst.user_id, workout_inst.workout_date, workout_inst.distance, workout_inst.time_sec, workout_inst.split, workout_inst.sr, workout_inst.hr, workout_inst.intervals, workout_inst.comment) 
        cur.execute(sql, subs)
        cur.execute("SELECT MAX(workout_id) from workout_log")
        workout_id = cur.fetchone()[0]
    finally:
        cur.close()
        conn.close()
        return workout_id  


# add interval to interval_log 
def add_interval(db:str, interval_inst:NewInterval)->bool:
    added = False
    try:
        # connect to db
        conn, cur = db_connect(db, True)
        # add interval data to interval_log table
        sql = "INSERT INTO interval_log(workout_id, time_sec, distance, split, sr, hr, rest, comment, interval_wo) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        subs = (interval_inst.workout_id, interval_inst.time_sec, interval_inst.distance, interval_inst.split, interval_inst.sr, interval_inst.hr, interval_inst.rest, interval_inst.comment, interval_inst.interval_wo) 
        cur.execute(sql, subs)
        added = True
    finally:
        cur.close()
        conn.close()
        return added  

        


