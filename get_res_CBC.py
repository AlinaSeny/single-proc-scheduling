import os
import sys
from re import findall


path1 = "outs/new_no_tr"
path2 = "outs/new_tr"
path3 = "outs/old_tr"
path4 = "outs/old_no_tr"
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
        tl = False
        for line in lines:
            if "time limit" in line:
                tl = True
                times[name] = 1800
            elif not tl and line.startswith("Total time"):
                nums = findall(r"\d+", line)
                times[name] = int(nums[0]) + int(nums[1]) / 100
            elif line.startswith("Objective value"):
                nums = findall(r"\d+", line)
                obj[name] = int(nums[0])
    print("path" + str(paths.index(path) + 1) + " = '" + path[5:] + "'")
    print("names" + str(paths.index(path) + 1) + " =", names)
    print("times" + str(paths.index(path) + 1) + " =", times)
