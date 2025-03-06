import os
import sys
from re import findall

d = {}
path1 = "times/new_no_tr"
path2 = "times/new_tr"
path3 = "times/old_tr"
path4 = "times/old_no_tr"
paths = [path1, path2, path3, path4]

for path in paths:
    dags = os.listdir(path)
    names = []
    times = {}
    obj = {}
    for file in dags:
        name = file[:-9]
        names.append(name)
        file = open(path + "/" + file, "r")
        lines = file.readlines()
        for line in lines:
            if line.startswith("real"):
                line = line.split()
                rl = line[1]
                m = rl.find("m")
                dot = rl.find(",")
                rl_t = int(float(rl[:m])) * 60 + int(float(rl[m + 1 : dot]))
                times[name] = rl_t
    print("path" + str(paths.index(path) + 1) + " = '" + path[6:] + "'")
    print("names" + str(paths.index(path) + 1) + " =", names)
    print("times" + str(paths.index(path) + 1) + " = ", times)
