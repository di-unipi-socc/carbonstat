import random
import numpy as np

# configuration for random number generation
maxN = 10000
rand = lambda min,max : random.SystemRandom().randint(min,max)
size = 1000000

# generate random numbers
values = []
for i in range(size):
    chunks = 4 # used to obtain high stdev
    pivot = rand(0,chunks)**(i%5)%chunks 
    start = round(pivot*maxN/chunks)
    end = round((pivot+1)*maxN/chunks) 
    values.append(rand(start,end))

print(np.average(values),np.std(values))

# generation of random numbers in file
with open("numbers.txt","w") as numbers:
    numbers.write(str(values[0]))
    for i in range(1,size):
        numbers.write("," + str(values[i]))