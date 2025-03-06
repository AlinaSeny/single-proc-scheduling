import os
from re import findall

files = (["mylayered" + "/" + file for file in os.listdir("mylayered")]
         + ["rand" + "/" + file for file in os.listdir("rand")]
         + ["triang_simple" + "/" + file for file in os.listdir("triang_simple")])

res_d = {}
alt_res_d = {}
for file in files:
    f = open(file, "r")
    lines = f.readlines()
    nodes = set()
    for line in lines:
        nums = findall(r"\d+", line)
        if len(nums) >= 2:
            nodes.add(nums[0])
    alt_res_d[file[file.find("/") + 1: -4]] = len(nodes)
    res_d[file[file.find("/") + 1: -4] + "_default"] = len(nodes)
    res_d[file[file.find("/") + 1: -4] + "_tiers"] = len(nodes)
    res_d[file[file.find("/") + 1: -4] + "_reverse_tiers"] = len(nodes)
    res_d[file[file.find("/") + 1: -4] + "_up_right"] = len(nodes)
    res_d[file[file.find("/") + 1: -4] + "_down_left"] = len(nodes)

