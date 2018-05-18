#! /usr/bin/env python
# -*- coding: utf-8 -*-

#CWA accelerometer data analysis program

#Imperial College London

#Romesh Tirimanna
#<rst114 [at] ic.ac.uk>

"""This program was designed to be able to perform analysis of raw accelerometer data
of the CWA filetype."""

# Modules/ packages imported
import sqlite3
import csv
import statistics
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from cwa1 import *
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

# namefunction function

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


        ########
        #resultant = [euclidean_norm(*x,*y,*z) for x,y,z in zip(a, b, c)] #list comprehension that creates a new list by applying the euclidean_norm function to the list of x,y,z tuples


        ''' Calculates the total nonwear in percent by dividing the sum of all the entries below the temperature threshold by the total number of entries'''
        ###### Calculate median and take that as the threshold

        ordered_temp_list_tuples = get_ordered_temp()
        temp_integers = [x[0] for x in ordered_temp_list_tuples]
        #print(temp_integers)

        # Distribution of the data: Min, Q1, Median, Q3, Max
        minimum = min(temp_integers)
        q1 = np.percentile(temp_integers, 25)
        median = statistics.median(temp_integers)
        mean = np.mean(temp_integers)
        mode = statistics.mode(temp_integers)
        q3 = np.percentile(temp_integers, 75)
        maximum = max(temp_integers)

        # print the above results
        print("Minimum value: ", minimum, "\n1st quartile: ", q1, "\nMedian: ", median, "\nMean: ", mean, "\n3rd quartile: ", q3, "Maximum value: ", maximum)

        # ask the user what threshold he would like:
        answer = int(input("From the results displayed above, what value would you like as a threshold? \n1: minimum value \n2: q1 \n3: median \n4: mean \n5: q3 \n6: maximum value"))

        if answer == 1:
            chosen_option = minimum
        elif answer == 2:
            chosen_option = q1
        elif answer == 3:
            chosen_option = median
        elif answer == 4:
            chosen_option = mean
        elif answer == 5:
            chosen_option = q3
        elif answer == 6:
            chosen_option = maximum
        else:
            print("Please choose an option 1-6")

        # def namefunction(chosen_option):
        temp_list_tuples = read_temp_from_db()                #The function returns a list of tuples
        newlist = [x[0] for x in temp_list_tuples]            #list comprehension that formats the list of tuples so that it only takes every 1st element and makes a list of integers.
        len_list = len(newlist)
        binary_list = [int(t <= chosen_option) for t in newlist]              #list comprehension that iterates through the list temperature and returns 1 or 0.
        total = sum(binary_list)                              #calculates the total number of entries which were below the non-wear temperature threshold
        totalNonwear = round((total/len_list)*100,2)          #calculates the total non-wear as a fraction of device recording time
        compliancescore = compliancescore(totalNonwear)
            # return compliancescore

        # if answer == 1:
        #     compliancescore = namefunction(minimum)
        # elif answer == 2:
        #     compliancescore = namefunction(q1)
        # elif answer == 3:
        #     compliancescore = namefunction(median)
        # elif answer == 4:
        #     compliancescore = namefunction(mean)
        # elif answer == 5:
        #     compliancescore = namefunction(q3)
        # elif answer == 6:
        #     compliancescore = namefunction(maximum)
        # else:
        #     print("Please choose an option 1-6")

        '''calculates the total number of steps '''
        resultant_list = read_resultant()
        newf = [round(float(x[0]),0) for x in resultant_list] #converts the list of tuples to a list of integers
        steps = count_steps(newf, 3)
        l = newf
        n = 200
        chunks = [l[i:i + n] for i in range(0, len(l), n)]    #uses slicing in a list comprehension to make sub lists after each day
        # print(chunks)

        # For loop to count steps for xxxx days and record the number of steps into a dictionary (list starts at 0)
        steps_list = []
        for i in chunks:
            steps_list.append(count_steps(i,3))

        combined = list(enumerate(steps_list))
        days = [x[0] for x in combined]
        steps = [x[1] for x in combined]

        dictionary_steps = dict(enumerate(steps_list))

        '''CSV writer'''
        patiententry = [{"patientID": patientID, "age": age, "sex": sex, "total steps": steps, "daily steps": dictionary_steps, "" "percentage non-wear": totalNonwear, "compliance score": compliancescore}]

        with open("patientoutput.csv", "a") as infile:
            fieldnames = ["patientID", "age", "sex", "total steps", "daily steps", "percentage non-wear", "compliance score"]
            patients = csv.DictWriter(infile, fieldnames=fieldnames)
            patients.writeheader()
            patients.writerows(patiententry)


        plt.stem(days, steps)
        # plt.plot(days,steps, '-o')
        plt.show()

        dbcurs.close()
        dbcon.close()
    else:
        print("Database unknown, please check the name: ", namedb)
