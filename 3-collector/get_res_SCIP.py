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
    nodes = {}
    status = {}
    for file in dags:
        name = file[:-9]
        names.append(name)
        nodes[name] = 0
        status[name] = False
        file = open(path + "/" + file, "r")
        lines = file.readlines()
        for line in lines:
            if line.startswith("SCIP Status"):
                if "solving was interrupted" in line:
                    status[name] = False
                elif "optimal solution found" in line:
                    status[name] = True
                else:
                    status[name] = line[12:]
            if line.startswith("Total Time"):
                nums = findall(r"\d+", line)
                times[name] = int(nums[0]) + int(nums[1]) / 100
            elif line.startswith("s_"):
                nodes[name] += 1
            elif "obj:1" in line:
                nums = findall(r"\d+", line)
                obj[name] = int(nums[0])
    print("path" + str(paths.index(path) + 1) + " = '" + path[5:] + "'")
    print("names" + str(paths.index(path) + 1) + " =", names)
    print("times" + str(paths.index(path) + 1) + " =", times)
    print("nodes" + str(paths.index(path) + 1) + " =", nodes)
    print("status" + str(paths.index(path) + 1) + " =", status)
