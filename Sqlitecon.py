import sqlite3
import math
#import matplotlib.pyplot as plt
#import sys #need this for (sys.argv[1] + '.sqlite')

#dbcon = sqlite3.connect(sys.argv[1] + '.sqlite')
dbcon = sqlite3.connect('x.cwa.sqlite') #makes a connection with the sqlite database in the directory
dbcurs = dbcon.cursor()

def read_all_from_db():
    for rows in dbcurs.execute("SELECT * FROM acc "): #iterates through all the rows in the database
        print(rows)

def read_x_from_db():
    x_list = []
    for rows in dbcurs.execute("SELECT x FROM acc "): #iterates through only the values of x in the rows of the database
        x_list.append(rows)
    return x_list

#dbcurs.execute("SELECT x FROM acc ")
#while True:
    #batch = dbcurs.fetchmany(100)
    #if not batch:
        #break
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

def euclidean_norm(x,y,z): #Function to calculate the resultant acceleration from the 3 axis
    total = (x ** 2) + (y ** 2) + (z ** 2)
    resultant1 = math.sqrt(total)
    return resultant1


a = list(read_x_from_db())
b = list(read_y_from_db())
c = list(read_z_from_db())

resultant = [euclidean_norm(*x,*y,*z) for x,y,z in zip(a, b, c)] #function that creates a new list by applying the euclidean_norm function to the list of x,y,z tuples

print(resultant)

#plt.plot(resultant_list)

#dbcurs.execute("ALTER TABLE acc ADD COLUMN resultant INTEGER")
for i in range(len(resultant)):
    print(resultant[i])
    resultant_i=resultant[i]
    dbcurs.execute("INSERT INTO acc (resultant) VALUES (1)")



dbcurs.close()
dbcon.close()
