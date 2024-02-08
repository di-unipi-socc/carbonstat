from os import listdir

files = listdir(".")

for f_name in files:
    if f_name.startswith("assign"):
        f = open(f_name,"r")
        new_f = open("x"+f_name,"w")
        for line in list(f):
            data = line.split(",")
            new_f.write(data[0] + "," + data[1] + "\n")
    f.close()
    new_f.close()
