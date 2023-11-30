import random

# configuration for random number generation
maxN = 1000000000
rand = lambda min,max : random.SystemRandom().randint(min,max)
size = 1000000

# generate random numbers
values = []
for i in range(size):
    pivot = rand(0,1) # used to obtain high stdev
    if pivot:
        values.append(rand(1,round(maxN/6)))
    else:
        values.append(rand(round(5*maxN/6),maxN))

# generation of random numbers in file
with open("numbers.txt","w") as numbers:
    numbers.write(str(values[0]))
    for i in range(1,size):
        numbers.write("," + str(values[i]))