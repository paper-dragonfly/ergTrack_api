from flask import Flask, request 
from pydantic import ValidationError 
from ergtrack_api.post_classes import NewInterval, NewUser, NewWorkout
import json
from ergtrack_api import logic as l
import pdb
import os

ENV = os.getenv('ENVIRONMENT')

def create_app(db):
    app = Flask(__name__) 

    @app.route('/', methods=['GET'])
    def home():
        return 'HOME REACHED'

    @app.route('/users', methods=['GET', 'POST'])
    def users():
        if request.method == 'GET': #get user info
            status_code, users_dict = l.get_users(db)
            return json.dumps({'status_code':status_code, 'body':users_dict})
        # POST new_user info, return: user_id
        elif request.method == 'POST':
            try:
                resp_newuser = NewUser.parse_obj(request.get_json())
            except ValidationError() as e:
                return json.dumps({'status_code': 400, 'message': e, 'body':None})
            user_id = l.add_new_user(db, resp_newuser)
            return json.dumps({'status_code': 200, 'body': user_id})


    @app.route("/workoutlog", methods = ['GET', 'POST']) #list all workouts for user
    def workoutlog():
        if request.method == 'GET':
            user_id = request.args["user_id"]
        # submit GET request with user_id -> all workouts listed by date for specific user. Fields: date, distance, time, av split, intervals
            try:
                conn, cur=l.db_connect(db)
                user_id = int(user_id)
                sql = "SELECT * FROM workout_log WHERE user_id=%s ORDER BY workout_date"
                subs = (user_id,)
                cur.execute(sql, subs)
                user_workouts = cur.fetchall() #[(v1,v2,v3),(...)]
            except ValueError:
                return json.dumps({'status_code':400, 'message':'user_id must be integer'})
            finally:
                conn.close()
                cur.close()
                return json.dumps({'status_code':200, 'message':user_workouts}, default=str) #datetime not json serializable so use defualt=str to convert non-serializable values to strings
        elif request.method == 'POST':
                # POST user_id, date, distance, time_sec, split, intervals, comment | return: workout_id
            try:
                workout_inst = NewWorkout.parse_obj(request.get_json())
            except ValidationError() as e:
                return json.dumps({'status_code': 400, 'message': e})
            workout_id = l.add_workout(db, workout_inst)
            return json.dumps({'status_code': 200, 'workout_id': workout_id})


    @app.route('/addinterval', methods=['POST'])
    def addinterval():
        #POST workout_id, interval_type, distance, time_sec, split, rest
        try:
            interval_inst = NewInterval.parse_obj(request.get_json())
        except ValidationError() as e:
            return json.dumps({'status_code': 400, 'message': e})
        add_successful:bool = l.add_interval(db, interval_inst) 
        return json.dumps({'status_code': 200, 'message':None, 'success':add_successful})    
            

    @app.route("/details", methods=['GET']) #list summary stats + all interval_log data for a specific workout_id
    def details():
        # retrieve workout_id
        workout_id = request.args["workout_id"]
        # List all intervals with workout_id 
        try:
            conn, cur = l.db_connect(db)
            cur.execute("SELECT * FROM workout_log WHERE workout_id=%s",(workout_id,))
            workout_summary = cur.fetchone()
            sbool = False
            if workout_summary[8]==1:
                sbool = True
            cur.execute("SELECT * FROM interval_log WHERE workout_id=%s",(workout_id,))
            intervals = cur.fetchall()
        finally:
            cur.close()
            conn.close() 
            return json.dumps({'status_code':200, 'single': sbool, 'intervals':intervals, 'workout_summary':workout_summary},default=str) 


    @app.route("/userstats", methods=['GET'])# display summary of all workouts for user
    def total():
        #POST user_id | return status_code, total_distance, total_time, total_workouts, user_info fm users, user's team
        user_id = request.args['user_id']
        try:
            conn,cur = l.db_connect(db)
            cur.execute("SELECT * FROM users WHERE user_id=%s",(user_id,))
            user_info = cur.fetchone()
            cur.execute("SELECT team_name FROM team WHERE team_id=(SELECT team FROM users WHERE user_id=%s)",(user_id,))
            user_team = cur.fetchone()
            cur.execute("SELECT distance, time_sec, intervals FROM workout_log WHERE user_id=%s",(user_id,))
            workouts = cur.fetchall()
            distance = 0
            time = 0
            count = len(workouts)
            # calculate total distance and time
            for i in range(len(workouts)):
                distance += (workouts[i][0])
                time += workouts[i][1]    
        finally:
            cur.close()
            conn.close()
            return json.dumps({'status_code':200, 'distance':distance, 'time':time, 'count':count, "user_info": user_info, "user_team":user_team})

    @app.route('/teams', methods=['GET','POST'])
    def teams(): ##need updatte test
        if request.method == 'GET':
            try:
                conn,cur = l.db_connect(db)
                cur.execute("SELECT * FROM team")
                team_lt = cur.fetchall() #[(t1id,t1nm),(t2id,t2nm)]
            finally:
                cur.close()
                conn.close()
                return json.dumps({'status_code': 200, 'body': team_lt})
        elif request.method == 'POST':
            newteam = request.get_json()['name']
            try:
                conn,cur = l.db_connect(db)
                # add team to team table if not already in db
                cur.execute("INSERT INTO team(team_name) VALUES(%s) ON CONFLICT DO NOTHING",(newteam,))
                conn.commit()
                cur.execute("SELECT team_id FROM team WHERE team_name=%s",(newteam,))
                newteam_id = cur.fetchone()[0] 
            finally:
                cur.close()
                conn.close()
                return json.dumps({'status_code': 200, 'body': newteam_id})




    @app.route("/teamlog", methods=['POST'])
    def teamlog():
        pass
        #return all workout descriptions (interval type, distance time num intervals) 
        # this might be hard. 
        # members = SELECT user_id FROM users WHERE team_id = x
        # SELECT * FROM workout_log WHERE user_id in members

# def boilerplate():
#     post_dict = request.get_json()
#     try:
#         conn, cur=l.db_connect(db)
#         sql = ""
#         subs = ()
#         cur.execute(sql, subs)
#         db_result=cur.fetchall()
#     finally:
#         conn.close()
#         cur.close()
#         return json.dumps({'status_code':200, 'message':None})
    print('I am running!')
    return app 

if ENV != 'testing':
    app = create_app(ENV)

if __name__ == '__main__':
    if ENV=='dev_local' or ENV=='dev_hybrid' or ENV =='dev_docker':
        host = l.config(ENV)['host']
        print(host)
        app.run(host='0.0.0.0', debug=True)



