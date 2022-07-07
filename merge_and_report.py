#WORK_DIR = r"C:\Users\HP\Desktop\jjj\Rotem_Report"
#DB_PATH = r"C:\Users\HP\Desktop\jjj\Rotem_Report\DB.xlsx"
WORK_DIR = '/Users/rotemarie/Desktop/report'
DB_PATH = '/Users/rotemarie/Desktop/report/DB.xlsx'
COMP_SESSION = 'complete_session.xlsx'
SUMMERY_SESSION = 'summery.xlsx'

import pandas as pd
import matplotlib.pyplot as plt
import copy
import openpyxl
import sys
import os
import warnings
import numpy
import glob

ADD_LST = ['Distance (km)', 'Active Time (min)', 'Session Time (min)', 'GPS Load', 'Inertial Load', 'Sprint Count', 'Sprint Total Distance (m)', 'Band1 (1.0 - 3.0 m/s) (km)', 'Explosive Effort Count', 'Impact Zone >= 7.5Gs', 'Impact Zone >= 10Gs', 'Impact Zone >= 12.5Gs',
           'SpeedZone >=3m/s (km)', 'SpeedZone >=4m/s (km)', 'SpeedZone >=5m/s (km)', 'SpeedZone >=6m/s (km)', 'SpeedZone >=7m/s (km)',  'Accel/Decel Zone >= 3m/s²']
MAX_LST = ['Top Speed (m/s)', 'Peak Acceleration (m/s/s)', 'Sprint Top Speed (m/s)']
MEAN_LST = ['Sprint Mean Distance (m)', 'Sprint Mean Duration (s)', 'Sprint Mean Speed (m/s)']
PER_MIN_LST = ['Distance per Minute (m/min)', 'Load per Minute (load/min)', 'Load per Minute (load/min)', 'Sprints per Minute (count/min)', 'Impacts per Minute (count/min)']
NAME = 'Name'
CLASS = 'Class'
GAME_DAY = 'GameDay'
CATEGORY = 'Category'
TYPE = 'Type'
FULL_GAME = 'complete'
GAME_COUNT = 'Game Count'
SPRINT_COUNT = 'Sprint Count'
SPRINT_DISTANCE = 'Sprint Total Distance (m)'
SPRINT_MEAN_DISTANCE = 'Sprint Mean Distance (m)'
SPRINT_MEAN_DURATION = 'Sprint Mean Duration (s)'
SPRINT_MEAN_SPEED = 'Sprint Mean Speed (m/s)'
SESSION_TIME = 'Session Time (min)'
GPS_LOAD = 'GPS Load'
INER_LOAD = 'Inertial Load'
DISTANCE = 'Distance (km)'
DIS_PER_MIN = 'Distance per Minute (m/min)'
GPS_LOAD_PER_MIN = 'GPS Load per Minute (load/min)'
INER_LOAD_PER_MIN = 'Inertial Load per Minute (load/min)'
SPRINT_PER_MIN = 'Sprints per Minute (count/min)'
IMPACT_ZONE_75 = 'Impact Zone >= 7.5Gs'
LOAD_PER_MIN = 'Load per Minute (load/min)'
LOAD_PER_MIN_1 = 'Load per Minute (load/min).1'
TOP_SPEED_M_S = 'Top Speed (m/s)'
TOP_SPEED_KM_H = 'Top Speed (km/h)'
SPRINT_TOP_S = 'Sprint Top Speed (m/s)'
SPEED_ZONE_5 = 'SpeedZone >=5m/s (km)'
SPEED_ZONE_7 = 'SpeedZone >=7m/s (km)'
SPEED_ZONE_18 = 'SpeedZone >=18km/h (m)'
ACCEL_DECEL_3 = 'Accel/Decel Zone >= 3m/s²'
ACCEL_DECEL_PER_MIN = 'Accel/Decel Zone >= 3m/s² per minute'
SET_NUMBER = 'Set Number'
RENAME_DICT = {LOAD_PER_MIN: GPS_LOAD_PER_MIN, LOAD_PER_MIN_1: INER_LOAD_PER_MIN}
SUMMERY_LIST = [DIS_PER_MIN, TOP_SPEED_KM_H, SPEED_ZONE_18, ACCEL_DECEL_PER_MIN, DISTANCE, ACCEL_DECEL_3]
AVG_LIST = [DIS_PER_MIN, ACCEL_DECEL_PER_MIN]
RELEVANT_FIELDS_ADDITIVE = [SESSION_TIME, DISTANCE, DIS_PER_MIN, SPEED_ZONE_5, SPEED_ZONE_7, ACCEL_DECEL_3]
RELEVANT_FIELDS_MAXIMUM = [TOP_SPEED_M_S]
RELEVANT_FIELDS_PLOTTING = RELEVANT_FIELDS_ADDITIVE[1:] + RELEVANT_FIELDS_MAXIMUM

def change_duplicates(df, names_dict):
#changes identical column names
    return df.rename(columns=names_dict)

def read_xl(input1, name=NAME):
#reads xl into df
    data = pd.read_excel(input1, index_col=name)
    return data

def safe_div(n,m):
    if n == 0 or m == 0:
        return 0
    else:
        return 1.0 * n / m
    
def check_players(lst):
#makes sure that all players appear in all data frames
    players = set(lst[0].index)
    for l in lst[1:]:
        players = players.union(set(l.index))
    for i in range(len(lst)):
        dif = players.difference(set(lst[i].index))
        if dif != set():
            n_players = len(dif)
            new_dict = {x: [0 for j in range(n_players)] for x in lst[i].keys()}
            new_dict[NAME] = list(dif)
            new_dict[CLASS] = [lst[i].iloc[0][CLASS] for j in range(n_players)]
            new_dict[TYPE] = [lst[i].iloc[0][TYPE] for j in range(n_players)]
            new_dict[CATEGORY] = [lst[i].iloc[0][CATEGORY] for j in range(n_players)]
            new_players = pd.DataFrame(data=new_dict)
            new_players = new_players.set_index(NAME)
            lst[i] = pd.concat([lst[i], new_players])
    return lst

def verify_players(DB, lst):
#makes sure that all players appear in the DB
    db_new = None
    players = set(DB.index)
    for l in lst:
        players = players.union(set(l.index))
    for i in range(len(lst)):
        dif = players.difference(set(lst[i].index))
        if dif != set():
            n_players = len(dif)
            new_dict = {x: [0 for j in range(n_players)] for x in lst[i].keys()}
            new_dict[NAME] = list(dif)
            new_players = pd.DataFrame(data=new_dict)
            new_players = new_players.set_index(NAME)
            db_new = pd.concat([DB, new_players])
    if db_new is None:
        return DB
    return db_new

def string_to_float(data):
#converts numerical strings to floats
    warnings.filterwarnings('ignore')
    for n in data.index:
        for p in data.keys():
            if p!=CLASS and p!=CATEGORY and p!=TYPE:
                data.loc[n][p]=float(data.loc[n][p])

def deep_copy(data):
#copies a df
    new_data=copy.deepcopy(data)
    return new_data

def nullify(new_data):
#nullifies all values in the copied df
    for n in new_data.index:
        for p in new_data.keys():
            if p!=CLASS and p!=CATEGORY and p!=TYPE:
                new_data.at[n,p]=0

def add_values_to_db(db, newData):
#adds new game values to the calculated average
    for n in newData.index:
        for p in newData.keys():
            if p in RELEVANT_FIELDS_ADDITIVE:
                db.at[n, p] += newData.at[n, p]
            if p in RELEVANT_FIELDS_MAXIMUM:
                    db.at[n, p] = round(max(db.at[n, p], newData.at[n, p]), 1)

def additive_values(lst, new_data):
#adds values of all data frames into the new df
    warnings.filterwarnings('ignore')
    for l in lst:
        for n in new_data.index:
            for p in new_data.keys():
                if p in ADD_LST and n in l.index:
                    new_data.at[n,p]+=l.at[n,p]

def maxi_values(lst, new_data):
#finds maximum value
    warnings.filterwarnings('ignore')
    for l in lst:
        for n in new_data.index:
            for p in new_data.keys():
                if p in MAX_LST and n in l.index:
                    if l.at[n,p]>new_data.at[n,p]:
                        new_data.at[n,p] = l.at[n,p]

def avg_values(lst, new_data):
#calculates average from all data frames
    warnings.filterwarnings('ignore')
    for n in new_data.index:
        sprintCount = new_data.at[n,SPRINT_COUNT]
        sumDis = new_data.at[n,SPRINT_DISTANCE]
        sumDur=0
        sumSpeed=0
        for l in lst:
            if n in l.index:
                sumDur+= l.at[n,SPRINT_MEAN_DURATION] * l.at[n,SPRINT_COUNT]
                sumSpeed+= l.at[n,SPRINT_MEAN_SPEED] * l.at[n,SPRINT_COUNT] * l.at[n,SPRINT_MEAN_DURATION]
        new_data.at[n,SPRINT_MEAN_DISTANCE] = safe_div(sumDis, sprintCount)
        new_data.at[n,SPRINT_MEAN_DURATION] = safe_div(sumDur, sprintCount)
        new_data.at[n,SPRINT_MEAN_SPEED] = safe_div(sumSpeed, sumDur)

def reCalc_values (new_data):
#calculates remaining values for the new data frame 
    warnings.filterwarnings('ignore')
    for n in new_data.index:
        sprintCount = new_data.at[n,SPRINT_COUNT]
        sessTime = new_data.at[n,SESSION_TIME]
        gpsLoad = new_data.at[n, GPS_LOAD]
        inerLoad = new_data.at[n, INER_LOAD]
        impZone75 = new_data.at[n, IMPACT_ZONE_75]
        new_data.at[n, DIS_PER_MIN] = int(safe_div(new_data.at[n,DISTANCE], sessTime) * 1000)
        new_data.at[n, GPS_LOAD_PER_MIN] = safe_div(gpsLoad, sessTime)
        new_data.at[n, INER_LOAD_PER_MIN] = safe_div(inerLoad, sessTime)
        new_data.at[n, SPRINT_PER_MIN] = safe_div(sprintCount, sessTime)
        new_data.at[n, IMPACT_ZONE_75] = safe_div(impZone75, sessTime)

def change_type(new_data, fullGame = FULL_GAME):
#changes half type to full game
    for n in new_data.index:
        for p in new_data.keys():
            if p==SET_NUMBER:	
                new_data.at[n,p]=fullGame
                
def combine_data(lst, new_data):
#combines all data frames into one
    frames=[]
    for l in lst:
        frames.append(l)
    frames.append(new_data)
    complete_data = pd.concat(frames)
    return complete_data

def new_columns_end(data):
    data[TOP_SPEED_KM_H] = data[TOP_SPEED_M_S] * 3.6
    data[SPEED_ZONE_18] = data[SPEED_ZONE_5] * 1000
    warnings.filterwarnings('ignore')
    data[ACCEL_DECEL_PER_MIN] = 0.0
    for n in data.index:
        sessTime = data.at[n,SESSION_TIME]
        acc_dec = data.at[n,ACCEL_DECEL_3]
        d = safe_div(acc_dec, sessTime)
        d = float_short(d)
        data.at[n, ACCEL_DECEL_PER_MIN] = d

def new_columns_begin(lst):
    warnings.filterwarnings('ignore')
    new_lst = []
    for i in range(len(lst)):
        df = lst[i]
        df[SET_NUMBER] = str(i+1)
        cols = df.columns.tolist()
        cols = cols[:3] + cols[-1:] + cols[3:-1]
        new_df = df[cols]
        new_lst.append(new_df)
    return new_lst

def create_summery(df):
    df = df[SUMMERY_LIST]
    write_and_save(df, SUMMERY_SESSION)

def write_and_save(data, path):
#writes df to xlsx
    writer = pd.ExcelWriter(path)
    data.to_excel(writer, 'DataFrame')
    writer.save()

def print_avg(lst, keys2print = AVG_LIST):
    warnings.filterwarnings('ignore')
    for i in range(len(lst)):
        print("Session number " + str(i+1))
        n_players = 0.0
        sum_lst = [0 for k in range(len(keys2print))]
        for n in lst[i].index:
            n_players += 1
            for j in range(len(keys2print)):
                sum_lst[j] += lst[i].at[n, keys2print[j]]
        avg_lst = [sum_lst[j] / n_players for j in range(len(keys2print))]
        for j in range(len(keys2print)):
            print(keys2print[j] + " : " + str(avg_lst[j]))

def float_short(f, n=2):
#returns a short
    return int(f * 10**n) * 1.0 / 10**n

def isGame(df):
#checks if a df represents a game
    if (df.iloc[0][CLASS]==GAME_DAY):
        return True
    return False

def plot(db, newData, field, highBar, lowBar):
#this fucntion plots all the relevant values
    barWidth = 0.25
    players = list(newData.index)
    first_names = [st.split(' ')[0]+st.split(' ')[1][0] for st in players]
    vals1 = []
    vals2 = []
    vals3 = []
    for n in newData.index:
        vals1.append(round(newData.loc[n][field], 1))
        if field in RELEVANT_FIELDS_MAXIMUM:
            vals2.append(round(db.loc[n][field], 1))
        if field in RELEVANT_FIELDS_ADDITIVE[1:]:
            vals2.append(round(safe_div(db.loc[n][field],db.loc[n][SESSION_TIME])*90, 1))
    for i in range(len(vals1)):
        vals3.append(round(safe_div(vals1[i], vals2[i])*100, 1))
    fig = plt.figure(figsize =(150, 10))
    X_axis = numpy.arange(len(players))
    y1 = plt.bar(X_axis, vals1, width = barWidth, color = 'royalblue', label = field)
    y2 = plt.bar(X_axis + barWidth, vals2, width = barWidth, color = 'cornflowerblue', label = 'Game Average')
    plt.xticks(X_axis, first_names)
    plt.title(newData.iloc[0][TYPE]+" - "+field)
    for i, v in enumerate(vals1):
        plt.text(i-0.25, v+.25, str(v), color='royalblue', fontWeight='bold', size=8)
    for i, v in enumerate(vals2):
        plt.text(i, v+.25, str(v), color='cornflowerblue', fontWeight='bold', size=8)
    plt.axhline(y=highBar, color='r', linestyle='--')
    plt.axhline(y=lowBar, color='r', linestyle='--') 
    ax2 = plt.twinx() #initiating a second y-axis that shares the same x-axis
    y3 = ax2.bar(X_axis + barWidth*2 , vals3, color='skyblue', width = barWidth, label = 'Proportion')
    ax2.tick_params(axis='y', labelcolor='black')
    for i, v in enumerate(vals3):
        plt.text(i+0.25, v+.25, str(v), color='skyblue', fontWeight='bold', size=8)
    plt.legend(handles=[y1, y2, y3])
    plt.show()

def getHighAndLowBars():
#this function takes high and low bars as input
    high = input("Enter high bar\n")
    low = input("Enter low bar\n")
    return high, low

def main_plotify (newData, db):
#main plotting function
    db_new = verify_players(db, newData)
    if db_new is not None:
        db = db_new
    high, low = getHighAndLowBars()
    for f in RELEVANT_FIELDS_PLOTTING:
        for d in newData:
            plot(db, d, f, high, low)
    
def update_db(db, newData):  
#updates db by calling add_values_to_db and incrementing GAME_COUNT
    for p in db.keys:
        db[GAME_COUNT][p]+=1
    add_values_to_db(db, newData)
        
def main_merge(lst): 
    os.chdir(WORK_DIR)
    lstdf=[]
    try:
        for x in lst:
            lstdf.append(read_xl(x))
    except:
        print("This is not the right file:"+x)
        return
    lstdf = [change_duplicates(x, RENAME_DICT) for x in lstdf]
    for h in lstdf:
        string_to_float(h)
    lstdf = new_columns_begin(lstdf)
    new_data = deep_copy(lstdf[0])
    new_data = verify_players(new_data, lstdf)
    nullify(new_data)
    additive_values(lstdf, new_data)
    maxi_values(lstdf, new_data)
    avg_values(lstdf, new_data)
    reCalc_values(new_data)
    change_type(new_data)
    for df in lstdf:
        new_columns_end(df)
    print_avg(lstdf)
    new_columns_end(new_data)
    complete_data = combine_data(lstdf, new_data)
    write_and_save(complete_data, COMP_SESSION)
    create_summery(new_data)
    lstdf.append(complete_data)
    return (lstdf)

def main(lst, DB = DB_PATH):
    lstdf = main_merge(lst)
    if (isGame(lstdf[0])):
        db = read_xl(DB)
        string_to_float(db)
        main_plotify(lstdf, db)
        update_db(db, lstdf[-1])
        write_and_save(db, DB)
    else:
        main_plotify(lstdf[-1])
    #SAVE THE OUTPUT
    
'''
if __name__ == "__main__":
    if len(sys.argv) == 1:
        params = glob.glob(WORK_DIR + r"\*")
        main(params)
    else:
        main(sys.argv[1:])'''
