#! /usr/bin/env python
# -*- coding: utf-8 -*-

#CWA accelerometer data analysis program

#Imperial College London

#Romesh Tirimanna
#<rst114 [at] ic.ac.uk>

"""This program was designed to be able to perform analysis of raw accelerometer data
"""

# Modules/ packages imported
import sqlite3
import csv
import math
import matplotlib.pyplot as plt
from pathlib import Path


### FUNCTIONS

def read_temp_from_db():
    """Function that reads the SQLite database and returns the temperature collumn"""
    dbcurs.execute("SELECT temperature FROM acc ")
    temperature_list = dbcurs.fetchall()
    return temperature_list


def get_ordered_temp():
    """Function that reads the SQLite database and returns the temperature collumn in order"""
    ordered_temp = dbcurs.execute("SELECT temperature FROM acc ORDER BY temperature")
    return ordered_temp


def get_time():
    """Function that reads the SQLite database and returns the time sample collumn"""
    time_list = []
    for rows in dbcurs.execute("SELECT timesample FROM acc"):
        time_list.append(rows)
    return time_list


def compliancescore(nonwear):
    """Function that uses the percentage non-wear to calculate a compliance score"""
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


def read_resultant():
    """Function that reads the SQLite database and returns the resultant collumn"""
    dbcurs.execute("SELECT resultant FROM acc ")
    resultant_2list = dbcurs.fetchall()
    return resultant_2list


def count_steps(list_days, cutoff):
    """Function that calculates the step counts"""
    samestep = False
    Nconseq = 0
    steps = 0
    threshold = cutoff
    for i, value in enumerate(list_days):
        if value == 0:
            Nconseq += 1
            if Nconseq > threshold:
                samestep = False
            else:
                samestep = True
        else:
            Nconseq = 0
            if not samestep:
                steps += 1
                print("line: ", i, "steps: ", steps)
            samestep = True

    return(steps)


def chunks(l, n):
    """Function that generates successive n-sized chunks from a list"""
    for i in range(0, len(l), n):
        yield l[i:i + n]


file_exists = False

# While the file doesn't exist, keep asking the question
while file_exists == False:
    namedb = str(input("What is the name of your database? (don't need the extension) "))
    namedb = namedb + ".cwa.sqlite"

    # Check that the database exists
    my_file = Path(namedb)
    if my_file.is_file():
        file_exists = True
    else:
        file_exists = False

    # When the file does exist, the code can begin
    if file_exists == True:
        dbcon = sqlite3.connect(namedb) #makes a connection with the sqlite database in the directory
        dbcurs = dbcon.cursor()


        # While loop to Check that the patient id is not empty
        bool_patientid = False
        while bool_patientid == False:
            patientID = input("Enter patient ID ")
            if patientID == "":
                print("Patient ID cannot be empty")
                bool_patientid = False
            else:
                bool_patientid = True
        #######
        # While loop to check age input
        bool_age = False
        while bool_age == False:
            age = int(input("Enter patient age: "))
            if age == str():
                print("Age must be a number")
                bool_age = False
            elif age <= 0:
                print("Age is out of range")
                bool_age = False
            elif age >= 130:
                print("Age is out of range")
                bool_age = False
            else:
                bool_age = True

        #while loop to check sex input
        bool_sex = False
        while bool_sex == False:
            sex = input("Enter patient sex (M/F): ")
            if sex == "M":
                bool_sex = True
            elif sex == "F":
                bool_sex = True
            elif sex == "m":
                bool_sex = True
            elif sex == "f":
                bool_sex = True
            else:
                print("invalid input! Please input M for male or F for female")
                bool_sex == False


        ########
        #resultant = [euclidean_norm(*x,*y,*z) for x,y,z in zip(a, b, c)] #list comprehension that creates a new list by applying the euclidean_norm function to the list of x,y,z tuples


        ''' Calculates the total nonwear in percent by dividing the sum of all the entries below the temperature threshold by the total number of entries'''
        ###### Calculate median and take that as the threshold

        ordered_temp_list_tuples = get_ordered_temp()
        temp_integers = [x[0] for x in ordered_temp_list_tuples]
        #print(temp_integers)
        median_possition = (len(temp_integers)+1)/2           #finds the position of the median in the list
        rounded = round(median_possition)                     #rounds the possition so its an integer
        temp_threshold = temp_integers[rounded]               #finds the value of the median
        #print(temp_threshold)

        temp_list_tuples = read_temp_from_db()                #The function returns a list of tuples
        newlist = [x[0] for x in temp_list_tuples]            #list comprehension that formats the list of tuples so that it only takes every 1st element and makes a list of integers.
        len_list = len(newlist)
        binary_list = [int(t <= temp_threshold) for t in newlist]              #list comprehension that iterates through the list temperature and returns 1 or 0.
        total = sum(binary_list)                              #calculates the total number of entries which were below the non-wear temperature threshold
        totalNonwear = round((total/len_list)*100,2)          #calculates the total non-wear as a fraction of device recording time
        compliancescore = compliancescore(totalNonwear)


        '''calculates the total number of steps '''
        resultant_list = read_resultant()
        newf = [round(float(x[0]),0) for x in resultant_list] #converts the list of tuples to a list of integers
        steps = count_steps(newf, 3)
        l = newf
        n = 86400001
        chunks = [l[i:i + n] for i in range(0, len(l), n)]    #uses slicing in a list comprehension to make sub lists after each day
        #print(chunks)

        #For loop to count steps for xxxx days and record the number of steps into a dictionary (list starts at 0)
        steps_list = map(count_steps(chunks, 3)) #applies the step counting function to every day chunk in the list with a cut off of 3. Creates a list of step counts per day
        #print(steps_list)

        # def step_dictionary(list):
        #     for i, value in enumerate(list_steps):
        #         daily_steps = {}
        #         daily_steps["day" i] = value
        #         return daily_steps
        #
        # dictionary_steps = map(step_dictionary(steps_list))

        '''CSV writer'''
        patiententry = [{"patientID": patientID, "age": age, "sex": sex, "total steps": steps, "daily steps": 123, "" "percentage non-wear": totalNonwear, "compliance score": compliancescore}]

        with open("patientoutput.csv", "a") as infile:
            fieldnames = ["patientID", "age", "sex", "total steps", "average daily steps", "percentage non-wear", "compliance score"]
            patients = csv.DictWriter(infile, fieldnames=fieldnames)
            patients.writeheader()
            patients.writerows(patiententry)
        #
        # # plt.plot(f,resultant_list)
        # # plt.show()

        dbcurs.close()
        dbcon.close()
    else:
        print("Database unknown, please check the name: ", namedb)
