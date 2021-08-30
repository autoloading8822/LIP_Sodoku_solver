#!/usr/bin/env python
# coding: utf-8

# In[5]:


import random

import os

import csv

path = os.getcwd()
name = input("file name")

csv_reader = csv.reader(
    open(path + "\\" + name,
         encoding='utf-8'))
a = [row for row in csv_reader]
l = random.sample(range(1, len(a)), 1000)
with open(path + "\\" + "Random select_" + name, "w", newline="") as dataCsv:
    csvW = csv.writer(dataCsv, dialect=("excel"))
    csvW.writerow(['quizzes', 'solutions'])
    for num in l:
        csvW.writerow(a[num])
print("Success.   Random Lists：", end="")
print(l)


# In[ ]:




