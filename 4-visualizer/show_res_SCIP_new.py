import numpy as np
import matplotlib.pyplot as plt
import re

import nodes_counter
nodes1 = nodes_counter.alt_res_d


class SolverResults:
    sorts = ["default", "reverse_tiers", "tiers", "down_left", "up_right"]
    path1 = 'new_no_tr'
    names1 = []
    times1 = {}
    status1 = {}
    path2 = 'new_tr'
    names2 = []
    times2 = {}
    status2 = {}
    path3 = 'old_tr'
    names3 = []
    times3 = {}
    status3 = {}
    path4 = 'old_no_tr'
    names4 = []
    times4 = {}
    status4 = {}
    reduces = [path1, path2, path3, path4]

    def __init__(self):
        self.res_d = {}

        for node in nodes1:
            count_optsol = 0
            min_time = 3600
            min_reduce = None
            min_sort = None
            fl_test = False
            for sort in self.sorts:
                if "test_" + node + "_" + sort not in self.status1 or "test_" + node + "_" + sort not in self.status2:
                    break
                fl_test = True
                if type(self.status1["test_" + node + "_" + sort]) == str:
                    print(f"WARNING: unexpected status: {self.path1, self.status1['test_' + node + '_' + sort]}")
                elif self.status1['test_' + node + "_" + sort]:
                    print(self.path1 + 'test_' + node + "_" + sort, end=' ')
                    count_optsol += 1
                    if self.times1['test_' + node + "_" + sort] < min_time:
                        min_reduce = self.path1
                        min_sort = sort
                        min_time = self.times1['test_' + node + "_" + sort]
                if type(self.status2['test_' + node + "_" + sort]) == str:
                    print(f"WARNING: unexpected status: {self.path2, self.status2['test_' + node + '_' + sort]}")
                elif self.status2['test_' + node + "_" + sort]:
                    print(self.path2 + 'test_' + node + "_" + sort, end=' ')
                    count_optsol += 1
                    if self.times2['test_' + node + "_" + sort] < min_time:
                        min_reduce = self.path2
                        min_sort = sort
                        min_time = self.times2['test_' + node + "_" + sort]
            if min_time < 100:
                min_time = 100
            if min_sort is None:
                min_sort = "default"
            if min_reduce is None:
                min_reduce = 'TIMELIMIT'
            if fl_test:
                self.res_d["test_" + node] = (min_time, min_sort, min_reduce, nodes1[node])
            print()
            if count_optsol == 1:
                print("correct")
            else:
                print(count_optsol)

            '''if node in self.status1 and node in self.status2:
                i
            else:
                continue
            m = re.search(r'(\d)[^\d]*$', node)
            name = node[:m.start() + 1]
            if name in self.res_d or name.startswith('triang_'):
                continue
            best_time = None
            best_sort = ''
            reduce = ''
            for sort in self.sorts:
                cur_name = name + '_' + sort
                times_list = [self.times1[cur_name], self.times2[cur_name]]
                cur_best_time = min(times_list)
                if best_time is None or best_time > cur_best_time:
                    if cur_best_time >= 3600:
                        best_time = 3600
                        best_sort = 'default'
                        reduce = 'new_no_tr'
                    else:
                        best_sort = sort
                        reduce = self.reduces[times_list.index(cur_best_time)]
                        best_time = cur_best_time
            if best_time < 50:
                best_time = 50
            self.res_d[name] = (best_time, best_sort, reduce, nodes1[node])'''


class SCIP(SolverResults):
    import SCIP_restest
    path1 = SCIP_restest.path1
    names1 = SCIP_restest.names1
    times1 = SCIP_restest.times1
    status1 = SCIP_restest.status1
    path2 = SCIP_restest.path2
    names2 = SCIP_restest.names2
    times2 = SCIP_restest.times2
    status2 = SCIP_restest.status2
    path3 = SCIP_restest.path3
    names3 = SCIP_restest.names3
    times3 = SCIP_restest.times3
    status3 = SCIP_restest.status3
    path4 = SCIP_restest.path4
    names4 = SCIP_restest.names4
    times4 = SCIP_restest.times4
    status4 = SCIP_restest.status4

    def __init__(self):
        super().__init__()


colors = {'new_no_tr': 'blue', 'new_tr': 'orange', 'TIMELIMIT': 'darkgray'}
#hatchs = {'new_no_tr': '', 'new_tr': '', 'old_tr': '', 'old_no_tr': '', 'TIMELIMIT': '//'}
edgecolors = {'new_no_tr': 'blue', 'new_tr': 'orange', 'old_tr': 'green', 'old_no_tr': 'firebrick', 'TIMELIMIT': 'darkgray'}
border = {"default": 'red', "reverse_tiers": 'aqua', "tiers": 'yellow', "down_left": 'lime', "up_right": 'fuchsia'}
scip = SCIP()
names = set(scip.res_d.keys())

cat_par = []
names = sorted(names)
for name in names:
    if name.startswith("test"):
        cat_par.append(str(scip.res_d[name][3]) + ' ' + name)
cat_par = sorted(cat_par)
print(cat_par)
x_tick = []
for name in cat_par:
    x_tick.append(name[name.find(' ') + 1:])
s, s_border, s_colors, s_hatch = [], [], [], []
for name in x_tick:
    s.append(scip.res_d[name][0])
    if scip.res_d[name][0] == 3600:
        s_colors.append('darkgray')
        s_border.append('darkgray')
        s_hatch.append('')
    else:
        s_colors.append(colors[scip.res_d[name][2]])
        s_border.append(border[scip.res_d[name][1]])
        s_hatch.append('')

width = 0.2

x = np.arange(len(cat_par))

fig, ax = plt.subplots()
rects3 = ax.bar(x, s, width, color=s_colors, edgecolor=s_border, hatch=s_hatch, linewidth=2)



ax.set_title('SCIP')
ax.set_xticks(x)
ax.set_xticklabels(x_tick, rotation=60, fontsize=8)
labels = list(colors.keys())
handles = [plt.Rectangle((0, 0), 1, 1, color=colors[label], edgecolor=edgecolors) for label in labels]
labels_bor = list(border.keys())
handles_bor = [plt.Rectangle((0, 0), 1, 1, color=border[label]) for label in labels_bor]
legend1 = plt.legend(handles, labels)
#plt.legend(handles + handles_bor, labels + labels_bor)
plt.legend(handles_bor, labels_bor, loc=6)
plt.gca().add_artist(legend1)
plt.ylim(top=3700)
plt.show()
