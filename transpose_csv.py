import os
import csv

data = []
# with open("puaj2wth.csv", newline='\n') as _file:
# with open("02x38doe.csv", newline='\n') as _file:
with open("sez8ur5j.csv", newline='\n') as _file:
    readCSV = csv.reader(_file, delimiter=',', quotechar='|')
    for row in readCSV:
        data.append(row)

transpose_data = []
x = len(data)
y = len(data[0])
for j in range(0, y):
    temp = []
    for i in range(0, x):
        temp.append(data[i][j])
    transpose_data.append(temp)

with open("test_2.csv", "w+", newline="\n") as fp:
    fpwriter = csv.writer(fp, delimiter=",", quotechar='|', quoting=csv.QUOTE_MINIMAL)
    for i in range(0, y):
        fpwriter.writerow(transpose_data[i])