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
