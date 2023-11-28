from numpy import random

# configuration for random number generation
generator = random.Generator(random.PCG64())
rand = lambda : str(round(generator.random()*100000000))
size = 1000000

# generation of random numbers in file
with open("numbers.txt","w") as numbers:
    numbers.write(rand())
    for i in range(size-1):
        numbers.write("," + rand())