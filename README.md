# Hapoel Jerusalem Football Club - Internship

The Football club uses [Titan Sensors](https://www.titansensor.com/) to collect data about the players' performance in games.
During this internship I was assigned the task of cleaning and analyzing the data, to create a presentable, summarized report for the team's coaches.

The repo contains exmaples for the data received from one game:[1st Half](https://github.com/rotemarie/HJFC/blob/master/1st_Half.xlsx) and [2nd Half](https://github.com/rotemarie/HJFC/blob/master/2nd_Half.xlsx).
As well as the final report: [report](https://github.com/rotemarie/HJFC/blob/master/reportExample.pdf)

The initial data comes separated to the 2 halves of the game and include many attributes that are not useful for the team.
I read and combined all the data into one dataframe while verifying that no players' data is being overwritten or erased in case they only played one half.

```bash
def string_to_float(data):
#converts numerical strings to floats
    warnings.filterwarnings('ignore')
    for n in data.index:
        for p in data.keys():
            if p!=CLASS and p!=CATEGORY and p!=TYPE:
                data.loc[n][p]=float(data.loc[n][p])

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
```

Then, to find the relevant data for the game, each attribute had to be treated differently as per the team's instructions: for some attributes only a maximum value had to be found, for others, averages or sums, etc.
Here are some examples to the processing of the data:

```bash
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
  ```

lastly, the data was written into a new excel file and plotted using MatPlotLib and these products were presented to the coaches.
```bash
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
```

Short example of the final data after processing:
![](https://github.com/rotemarie/HJFC/blob/master/summary.png)

Example graphs:
![](https://github.com/rotemarie/HJFC/blob/master/g1.png)
![](https://github.com/rotemarie/HJFC/blob/master/g2.png)

