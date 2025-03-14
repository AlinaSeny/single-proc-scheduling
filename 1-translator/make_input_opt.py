from re import findall
import os
import argparse
from sort_input import tier_sort
from copy import deepcopy
from pathlib import Path
from typing import List, Dict, Set


parser = argparse.ArgumentParser()
parser.add_argument(
    '-tr',
    '--transitive',
    action='store_true',
    help='set m_i_j=1 for transitive edges'
)
parser.add_argument(
    '-r',
    '--reduce',
    type=str,
    default='new',
    help='set reduce "new" or "old"'
)
parser.add_argument(
    '-o',
    '--output',
    type=str,
    default=None,
    help='output directory for .lp files'
)
parser.add_argument(
    '-i',
    '--input',
    required=True,
    type=str,
    help='path to input file or directory'
)
args = parser.parse_args()

solver_tasks = []


def read_pars_input(file_path: str, sort: str) -> (Set[str], Dict[str, str], Dict[str, List[str]], List[str]):
    f = open(file_path, "r")
    nodes = set()
    sizes = {}
    children = {}
    nodes_with_par = set()
    lines = f.readlines()
    if sort == "up_right":
        lines.reverse()
    for line in lines:
        nums = findall(r"\d+", line)
        if not nums:
            continue
        nodes.add(nums[0])
        sizes[nums[0]] = nums[1]
        children[nums[0]] = nums[2:]
        for node in nums[2:]:
            nodes_with_par.add(node)
        if sort == "down_left":
            children[nums[0]].reverse()
    f.close()
    if sort == "tiers":
        nodes, children = tier_sort(nodes, sizes, children)
    elif sort == "reverse_tiers":
        nodes, children = tier_sort(nodes, sizes, children, True)
    parents = list(set(nodes) - nodes_with_par)
    return nodes, sizes, children, parents


def find_all_children(i: str, children: Dict[str, List[str]], visited: Dict[str, bool]):
    for j in children[i]:
        if not visited[j]:
            visited[j] = True
            find_all_children(j, children, visited)
        for transit_child in children[j]:
            if transit_child not in children[i]:
                children[i].append(transit_child)


def define_m(children: Dict[str, List[str]], nodes: List[str], parents: List[str]) -> (List[str], List[str], List[str]):
    m_bounds = []
    m_binary = []
    m_subj = []
    all_children = deepcopy(children)
    visited = {}
    for node in nodes:
        visited[node] = False
    for node in parents:
        visited[node] = True
        find_all_children(node, all_children, visited)
    for i in nodes:
        for j in nodes:
            if args.transitive:
                if i == j or j in all_children[i]:
                    m_bounds.append("m_" + str(i) + "_" + str(j) + " = 1")
            else:
                if i == j or j in children[i]:
                    m_bounds.append("m_" + str(i) + "_" + str(j) + " = 1")
            if i != j:
                m_subj.append(
                    "m_"
                    + str(i)
                    + "_"
                    + str(j)
                    + " + "
                    + "m_"
                    + str(j)
                    + "_"
                    + str(i)
                    + " = 1"
                )
            m_binary.append("m_" + str(i) + "_" + str(j))
    return m_bounds, m_binary, m_subj


def define_s(nodes: List[str]) -> (List[str], List[str], List[str], List[str]):
    s_int = []
    s_subj_1 = []
    s_subj_4 = []
    s_subj_5 = []
    for i in nodes:
        s1 = "s_" + str(i)
        s_int.append(s1)
        for j in nodes:
            s1 += " - m_" + str(j) + "_" + str(i)
            if int(i) < int(j):
                s_subj_4.append(
                    "s_"
                    + str(i)
                    + " + "
                    + str(len(nodes))
                    + " m_"
                    + str(i)
                    + "_"
                    + str(j)
                    + " - s_"
                    + str(j)
                    + " <= "
                    + str(len(nodes) - 1)
                )
                # s_subj_5.append(f's_{j} - s_{i} - {n} m_{i}_{j} <= -1')
                s_subj_5.append(
                    "s_"
                    + str(j)
                    + " - s_"
                    + str(i)
                    + " - "
                    + str(len(nodes))
                    + " m_"
                    + str(i)
                    + "_"
                    + str(j)
                    + " <= -1"
                )
        s1 += " = 0"
        s_subj_1.append(s1)
    return s_int, s_subj_1, s_subj_4, s_subj_5


def define_f(sizes: Dict[str, str], nodes: List[str]) -> List[str]:
    f_subj = []
    var = " w_"
    if args.reduce == "new":
        var = " y_"
    for k in nodes:
        s = "F"
        for i in nodes:
            s += " - " + str(sizes[i]) + var + str(i) + "_" + str(k)
        s += " >= 0"
        f_subj.append(s)
    return f_subj


def define_l_w(children: Dict[str, List[str]], nodes: List[str]) -> (List[str], List[str], List[str], List[str], List[str]):
    l_bounds = []
    l_subj = []  # (8)
    w_subj = []  # (10)
    l_binary = []
    w_binary = []
    for i in nodes:
        l_bounds.append("l_" + str(i) + "_" + str(i) + " = 1")
        for k in nodes:
            for j in children[i]:
                l_subj.append(
                    "l_"
                    + str(i)
                    + "_"
                    + str(k)
                    + " - m_"
                    + str(k)
                    + "_"
                    + str(j)
                    + " >= 0"
                )
            w_subj.append(
                "w_"
                + str(i)
                + "_"
                + str(k)
                + " - l_"
                + str(i)
                + "_"
                + str(k)
                + " - m_"
                + str(i)
                + "_"
                + str(k)
                + " >= -1"
            )
            l_binary.append("l_" + str(i) + "_" + str(k))
            w_binary.append("w_" + str(i) + "_" + str(k))
    return l_bounds, l_subj, w_subj, l_binary, w_binary


def define_y(children: Dict[str, List[str]], nodes: List[str]) -> (List[str], List[str], List[str]):
    y_bounds = []
    y_subj = []
    y_binary = []
    subj10, subj11, subj12 = 0, 0, 0
    for i in nodes:
        for k in nodes:
            y_binary.append("y_" + str(i) + "_" + str(k))
            if i == k:
                # все y_i_i = 1
                y_bounds.append("y_" + str(i) + "_" + str(k) + " = 1")
                continue

            if k in children[i]:
                # для всех ребер y_i_k = 1
                y_bounds.append("y_" + str(i) + "_" + str(k) + " = 1")
                continue
            else:
                y_subj.append(
                    "y_"
                    + str(i)
                    + "_"
                    + str(k)
                    + " - "
                    + "m_"
                    + str(i)
                    + "_"
                    + str(k)
                    + " <= 0"
                )
                subj10 += 1
                y = "y_" + str(i) + "_" + str(k)
                ys = y
                for j in children[i]:
                    ys += " - m_" + str(k) + "_" + str(j)
                    y_subj.append(
                        y
                        + " - m_"
                        + str(k)
                        + "_"
                        + str(j)
                        + " - m_"
                        + str(i)
                        + "_"
                        + str(k)
                        + " >= -1"
                    )
                    subj12 += 1
                if ys != y:
                    y_subj.append(ys + " <= 0")
                    subj11 += 1
    print(subj10, subj11, subj12)
    return y_bounds, y_subj, y_binary


def write_solver_input(file_path: str, children: Dict[str, List[str]], sizes: Dict[str, str], nodes: List[str], parents: List[str]):
    l_bounds = []
    l_subj = []
    w_subj = []
    l_binary = []
    w_binary = []
    y_binary = []
    y_subj = []
    y_bounds = []

    # m  (2)(3)(6)
    m_bounds, m_binary, m_subj = define_m(children, nodes, parents)
    # s  (1)(4)(5)
    s_int, s_subj_1, s_subj_4, s_subj_5 = define_s(nodes)
    # F  (7б) F >= P_k
    f_subj = define_f(sizes, nodes)
    if args.reduce == "old":
        # l w (8)(9)(10)
        l_bounds, l_subj, w_subj, l_binary, w_binary = define_l_w(children, nodes)
    else:
        # y
        y_bounds, y_subj, y_binary = define_y(children, nodes)
    print(file_path)

    f = open(file_path, "w+")

    f.write("Minimize\n")
    f.write("    F\n")

    f.write("Subject to\n")
    for i in m_subj:
        f.write("    " + i + "\n")
    for i in s_subj_1:
        f.write("    " + i + "\n")
    for i in s_subj_4:
        f.write("    " + i + "\n")
    for i in s_subj_5:
        f.write("    " + i + "\n")
    for i in l_subj:
        f.write("    " + i + "\n")
    for i in w_subj:
        f.write("    " + i + "\n")
    for i in f_subj:
        f.write("    " + i + "\n")
    for i in y_subj:
        f.write("    " + i + "\n")

    # try adding bounds for F and s
    f.write("Bounds\n")
    # f.write('    F = 1\n')
    for i in m_bounds:
        f.write("    " + i + "\n")
    for i in l_bounds:
        f.write("    " + i + "\n")

    for i in y_bounds:
        f.write("    " + i + "\n")

    f.write("Integer\n")
    f.write("    F\n")
    for i in s_int:
        f.write("    " + i + "\n")

    f.write("Binary\n")
    for i in m_binary:
        f.write("    " + i + "\n")
    for i in l_binary:
        f.write("    " + i + "\n")
    for i in w_binary:
        f.write("    " + i + "\n")

    for i in y_binary:
        f.write("    " + i + "\n")

    f.write("End\n")
    f.close()


def parse(sort: str):
    files = []
    input_path = args.input
    if os.path.isdir(args.input):
        files = os.listdir(args.input)
    else:
        files.append(args.input[args.input.rfind("/")+1:])
        input_path = args.input[:args.input.rfind("/")+1]
    for file_name in files:
        nodes, sizes, children, parents = read_pars_input(input_path + file_name, sort)
        if file_name.find(".") != -1:
            file_name = file_name[:file_name.rfind(".")]
        solver_tasks.append(file_name)
        path = args.output + file_name + "_" + sort + "_input.lp"
        write_solver_input(path, children, sizes, nodes, parents)


if __name__ == "__main__":
    curpath = os.getcwd()
    if args.reduce != "old" and args.reduce != "new":
        print('Please, use only "new" or "old" for reduce flag')
        exit(1)
    if args.output is None:
        if args.transitive:
            args.output = curpath + "/" + "inputs/" + args.reduce + "_tr/order/"
        else:
            args.output = curpath + "/" + "inputs/" + args.reduce + "_no_tr/order/"
    else:
        if curpath not in args.output:
            args.output = curpath + "/" + args.output
        if args.output[:-1] != '/':
            args.output += '/'
    Path.mkdir(Path(args.output), parents=True, exist_ok=True)
    if curpath not in args.input:
        args.input = curpath + "/" + args.input
    if not os.path.isfile(args.input) and not os.path.isdir(args.input):
        print("Received input path isn't a directory or file. Try to enter absolute path")
        exit(1)
    parse("default")
    parse("tiers")
    parse("reverse_tiers")
    parse("up_right")
    parse("down_left")
