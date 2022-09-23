from datetime import datetime
from pydantic import BaseModel

# QUESTION: why are the variables class vars not instance vars for pydantic? 
class NewUser(BaseModel):
    user_name:str
    dob:str
    sex:str='Female'
    team_id:str

class IntervalWorkout(BaseModel):
    user_id:str = 'guest'
    distance:int = 0
    time:float = 0
    rest:int = 0
    intervals:int = 1
    date = '2000-01-01'
    userid:int = 0

class NewWorkout(BaseModel):
    user_id:int
    workout_date:str = '2000-01-01'
    time_sec:float = 0.0
    distance:int = 0
    split:float = 0.0
    sr:int = 0
    hr:int = 0
    intervals:int = 1
    comment:str = ""

class NewInterval(BaseModel):
    workout_id:int 
    time_sec:float
    distance:int 
    split:float=0.0
    sr:int=0
    hr:int=0
    rest:int=0
    comment:str=""
    interval_wo:bool


