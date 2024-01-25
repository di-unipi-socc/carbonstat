import random

# configuration for random number generation
maxN = 10000
rand = lambda min,max : random.SystemRandom().randint(min,max)
size = 1000000

# generate random numbers
values = []
for i in range(size):
    if i%20 == 0:
        values.append(rand(1,round(maxN/4)))
    else:
        values.append(rand(round(3*maxN/4),maxN))

# generation of random numbers in file
with open("numbers.txt","w") as numbers:
    numbers.write(str(values[0]))
    for i in range(1,size):
        numbers.write("," + str(values[i]))