def tier_sort(nodes, sizes, children, reverse_nodes=False):
    # print(nodes)
    tiers = {}
    node_tier = {}
    sort_nodes = []
    lvl = 0
    count = 0
    parents = {}
    connections = children
    for node in nodes:
        parents[node] = []
    if reverse_nodes:
        for node in nodes:
            for child in children[node]:
                parents[child].append(node)
        connections = parents

    while count != len(nodes):
        tiers[lvl] = []
        if lvl == 0:
            for i in range(len(nodes)):
                flag = True
                for group in connections.values():
                    if nodes[i] in group:
                        flag = False
                        break
                if flag and nodes[i] not in sort_nodes:
                    tiers[lvl].append(nodes[i])
                    node_tier[nodes[i]] = lvl
                    sort_nodes.append(nodes[i])
                    count += 1
        else:
            for node in tiers[lvl - 1]:
                for child in connections[node]:
                    if child not in sort_nodes:
                        tiers[lvl].append(child)
                        node_tier[child] = lvl
                        sort_nodes.append(child)
                        count += 1
        lvl += 1
    # print("sorted =", sort_nodes)
    # print(node_tier)
    sort_children = {}
    for node in sort_nodes:
        prev = None
        # print(children[node])
        tmp_node_tier = {}
        sort_children[node] = children[node]
        for child in children[node]:
            tmp_node_tier[child] = node_tier[child]
        # print(tmp_node_tier)
        if sort_children[node] is not None:
            tmp_node_tier = dict(
                sorted(tmp_node_tier.items(), key=lambda item: item[1])
            )
            # print(tmp_node_tier)
            sort_children[node] = list(tmp_node_tier.keys())
    return sort_nodes, sort_children
