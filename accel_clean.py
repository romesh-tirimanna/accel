#! /usr/bin/env python
# -*- coding: utf-8 -*-

#CWA accelerometer data analysis program

#Imperial College London

#Romesh Tirimanna
#<rst114 [at] ic.ac.uk>

"""This program was designed to be able to perform analysis of raw accelerometer data
of the CWA filetype."""

# Modules/ packages imported
import csv
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import sqlite3
import statistics
from cwa1 import *
import subprocess as sp #to use python2 for the cwa1.py file


#Functions
def read_temp_from_db():
    """Function that reads the SQLite database and returns the temperature collumn"""
    dbcurs.execute("SELECT temperature FROM acc ")
    temperature_list = dbcurs.fetchall()
    return temperature_list


def get_ordered_temp():
    """Function that reads the SQLite database and returns the temperature collumn in order"""
    ordered_temp = dbcurs.execute("SELECT temperature FROM acc ORDER BY temperature")
    return ordered_temp


def compliancescore(nonwear):
    """Function that uses the percentage non-wear to calculate a compliance score"""
    if nonwear <= 10:
        score = "excellent"
    elif nonwear <= 30:
        score = "good"
    elif nonwear <= 56:
        score = "average"
    elif 57 <= nonwear <= 100:
        score = "poor"
    else:
        score = "error"
    return score


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
                #print("line: ", i, "steps: ", steps)
            samestep = True
    return steps


def chunks(l, n):
    """Function that generates successive n-sized chunks from a list"""
    for items in range(0, len(l), n):
        yield l[items:items + n]


# While the file doesn't exist, keep asking the question
cwa_exists = False
db_exists = False
while db_exists == False:
    name = str(input("What is the name of your file/database? (don't need the extension) "))
    name_db = name + ".cwa.sqlite"
    name_cwa = name + ".cwa"

    my_cwa = Path(name_cwa)
    if my_cwa.is_file():
        cwa_exists = True
    else:
        cwa_exists = False

    # Checks that the database exists
    my_db = Path(name_db)
    if my_db.is_file():
        db_exists = True
    else:
        db_exists = False

    # When the file does exist, the code can begin
    if db_exists == True and cwa_exists == True:
        dbcon = sqlite3.connect(name_db) #makes a connection with the sqlite database in the directory
        dbcurs = dbcon.cursor()


        # While loop checks that the patient ID is not empty
        bool_patientid = False
        while bool_patientid == False:
            patientID = input("Enter patient ID ")
            if patientID == "":
                print("Patient ID cannot be empty")
                bool_patientid = False
            else:
                bool_patientid = True

        # While loop to check age input
        bool_age = False
        while bool_age == False:
            age = input("Enter patient age: ")
            try:
                age = int(age)
                if age <= 0 or age >= 130:
                    print("Age is out of range")
                    bool_age = False
                else:
                    bool_age = True
            except ValueError:
                print("Enter a number")
                bool_age = False

        #while loop to check sex input
        bool_sex = False
        while bool_sex == False:
            sex = input("Enter patient sex (M/F): ")
            if sex.upper() in ["M", "F"]:
                bool_sex = True
            else:
                print("invalid input! Please input M for male or F for female")
                bool_sex == False


        ''' Calculates the total nonwear in percent by dividing the sum of all the entries below the temperature threshold by the total number of entries'''
        ###### Calculate median and take that as the threshold

        ordered_temp_list_tuples = get_ordered_temp()
        temp_integers = [x[0] for x in ordered_temp_list_tuples]

        # Distribution of the data: Min, Q1, Median, mean, mode, Q3, Max
        minimum = min(temp_integers)
        q1 = np.percentile(temp_integers, 25)
        median = statistics.median(temp_integers)
        mean = np.mean(temp_integers)
        mode = statistics.mode(temp_integers)
        q3 = np.percentile(temp_integers, 75)
        maximum = max(temp_integers)

        # print the above results
        print("Minimum value: ", minimum, "\n1st quartile: ", q1, "\nMedian: ", median, "\nMean: ", mean, "\nMode: ", mode, "\n3rd quartile: ", q3, "\nMaximum value: ", maximum)

        # ask the user what threshold he would like:
        bool_stats = False
        while bool_stats == False:
            answer = input("Based on the results displayed above, please choose a threshold? ")
            try:
                threshold = int(answer)
                if threshold < 0 or threshold > 50:
                    print("temperature is out of range")
                    bool_stats = False
                else:
                    bool_stats = True
            except ValueError:
                print("Enter a number")
                bool_stats = False

        '''calculates the total non-wear and compliance score'''
        temp_list_tuples = read_temp_from_db()                #The function returns a list of tuples
        newlist = [x[0] for x in temp_list_tuples]            #list comprehension that formats the list of tuples so that it only takes every 1st element and makes a list of integers.
        len_list = len(newlist)
        binary_list = [int(t <= threshold) for t in newlist]              #list comprehension that iterates through the list temperature and returns 1 or 0.
        total = sum(binary_list)                              #calculates the total number of entries which were below the non-wear temperature threshold
        totalNonwear = round((total/len_list)*100,2)          #calculates the total non-wear as a fraction of device recording time
        compliancescore = compliancescore(totalNonwear)


        '''calculates the total number of steps '''
        resultant_list = read_resultant()
        newf = [round(float(x[0]),0) for x in resultant_list] #converts the list of tuples to a list of integers
        steps = count_steps(newf, 3)
        l = newf
        n = 86400001                                          #the number of ms per day +1 because the last value is not included when slicing
        chunks = [l[i:i + n] for i in range(0, len(l), n)]    #uses slicing in a list comprehension to make sub lists after each day
        # print(chunks)

        # For loop to count steps for xxxx days and record the number of steps into a dictionary (list starts at 0)
        steps_list = []
        for i in chunks:
            steps_list.append(count_steps(i,3)) #applies the step counting function to every chunk and adds this total to a list

        combined = list(enumerate(steps_list))  #indexes the steps e.g day:steps i:value  0:2343
        days = [x[0] for x in combined]         #gets just the index from this list to get a list of days only
        steps = [x[1] for x in combined]        #gets just the values from this list to get a list of steps only

        dictionary_steps = dict(enumerate(steps_list))

        '''CSV writer'''
        patiententry = [{"patientID": patientID, "age": age, "sex": sex, "total steps": steps, "daily steps": dictionary_steps, "" "percentage non-wear": totalNonwear, "compliance score": compliancescore}]

        with open("patientoutput.csv", "a") as infile:
            fieldnames = ["patientID", "age", "sex", "total steps", "daily steps", "percentage non-wear", "compliance score"]
            patients = csv.DictWriter(infile, fieldnames=fieldnames)
            patients.writeheader()
            patients.writerows(patiententry)


        plt.stem(days, steps)
        plt.show()

        dbcurs.close()
        dbcon.close()

    elif db_exists == False and cwa_exists == True:
        print("creating database.... please wait for the program to restart")
        sp.call(["python2", "cwa1.py", name + ".cwa"])

    else:
        print("Database not found, please check the name: ", name)
