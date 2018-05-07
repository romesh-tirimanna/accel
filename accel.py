import sqlite3
import csv
import math
import matplotlib.pyplot as plt
import numpy as np

dbcon = sqlite3.connect('nonweartest.cwa.sqlite') #makes a connection with the sqlite database in the directory
dbcurs = dbcon.cursor()

def read_all_from_db():
    for rows in dbcurs.execute("SELECT * FROM acc "): #iterates through all the rows in the database
        print(rows)

def read_x_from_db():
    x_list = []
    for rows in dbcurs.execute("SELECT x FROM acc "): #iterates through only the values of x in the rows of the database
        x_list.append(rows)
    return x_list

def read_y_from_db():
    y_list = []
    for rows in dbcurs.execute("SELECT y FROM acc "): #iterates through only the values of y in the rows of the database
        y_list.append(rows)
    return y_list

def read_z_from_db():
    z_list = []
    for rows in dbcurs.execute("SELECT z FROM acc "): #iterates through only the values of z in the rows of the database
        z_list.append(rows)
    return z_list

def read_temp_from_db():
    temp_list = []
    for rows in dbcurs.execute("SELECT temperature FROM acc "):
        temp_list.append(rows)
    return temp_list

def euclidean_norm(x,y,z): #Function to calculate the resultant acceleration from the 3 axis
    total = (x ** 2) + (y ** 2) + (z ** 2)
    resultant1 = math.sqrt(total)
    return resultant1

def read_resultant():
    resultant_list = []
    for rows in dbcurs.execute("SELECT resultant FROM acc "): #iterates through only the values of x in the rows of the database
        resultant_list.append(rows)
    return resultant_list

def get_time():
    time_list = []
    for rows in dbcurs.execute("SELECT timesample FROM acc"):
        time_list.append(rows)
    return time_list

def moving_average(values,window):
    weights = np.repeat(1.0, window)/window
    smas = np.convolve(values, weights, 'valid')
    return smas

def compliancescore(nonwear):
    if nonwear <= 10:
        return "excellent"
    elif nonwear <= 30:
        return "good"
    elif nonwear <= 56:
        return "average"
    elif 57 <= nonwear <= 100:
        return "poor"
    else:
        return "error"

a = list(read_x_from_db())
b = list(read_y_from_db())
c = list(read_z_from_db())
d = list(read_temp_from_db())
f = list(get_time())
resultant = [euclidean_norm(*x,*y,*z) for x,y,z in zip(a, b, c)] #list comprehension that creates a new list by applying the euclidean_norm function to the list of x,y,z tuples


''' Calculates the total nonwear in percent by dividing the sum of all the entries below the temperature threshold by the total number of entries'''
oldlist = read_temp_from_db()
newlist = [x[0] for x in oldlist] #list comprehension that formats the list of tuples so that it only takes every 1st element and makes a list of integers.
#e = get_highest_time()
len_oldlist=len(oldlist)
x = [int(t <= 23) for t in newlist] #list comprehension that iterates through the list temperature and returns 1 or 0.
total = sum(x)
totalNonwear = round((total/len_oldlist)*100,2)

'''calculates the total number of steps '''
f = read_resultant()
newf = [x[0] for x in f]
s = moving_average(newf, 41.35)
z = [int(t >= 2) for t in s]
steps = sum(z)/2

'''CSV writer'''
patiententry = [{"patientID": 12345, "age": 32, "sex": "m", "total steps": steps, "average daily steps": 123, "" "non-wear time": 30, "compliance score": "good"}]

with open("patientoutput.csv", "w") as infile:
    fieldnames = ["patientID", "age", "sex", "total steps", "average daily steps", "non-wear time", "compliance score"]
    patients = csv.DictWriter(infile, fieldnames=fieldnames)
    patients.writeheader()
    patients.writerows(patiententry)

print(steps)
print(totalNonwear,'%')
print(compliancescore(totalNonwear))

plt.plot(f,resultant)
plt.show()

dbcurs.close()
dbcon.close()
