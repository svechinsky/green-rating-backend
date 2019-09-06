from tinydb import TinyDB, Query
from tinydb.operations import set as set_
from app import get_rsa_pair, to_priv_pem_key
import random, rsa
import names

db = TinyDB('gdata.json', indent=4)
nodes_table = db.table('nodes')
edges_table = db.table('edges')

# nodes.insert_multiple([
#     {'name': 'A', 'pubkey': 'puba', 'rank': 0},
#     {'name': 'B', 'pubkey': 'pubb', 'rank': 1},
#     {'name': 'C', 'pubkey': 'pubb', 'rank': 1},
#     {'name': 'D', 'pubkey': 'pubb', 'rank': 1},
#     {'name': 'E', 'pubkey': 'pubb', 'rank': 1},
#     {'name': 'F', 'pubkey': 'pubb', 'rank': 1},
#     {'name': 'G', 'pubkey': 'pubb', 'rank': 1},
#     {'name': 'H', 'pubkey': 'pubb', 'rank': 1},
#     {'name': 'I', 'pubkey': 'pubb', 'rank': 1},
#     {'name': 'J', 'pubkey': 'pubb', 'rank': 1},
#
# ])
#
# edges.insert_multiple([
#     {'from': 'puba', 'to': 'pubb', 'is_approved': True, 'signature': 'ghjgyu67'}
# ])

def rank_nodes_from(initial_node_pubkey):
    nodes_table.update(set_('rank', -1))
    nodes_table.update(set_('rank', 0), Query().pubkey == initial_node_pubkey)

    rank = 1
    last_ranked_pubkeys = {initial_node_pubkey}
    while True:
        print("Last ranked")
        print(last_ranked_pubkeys)
        pubkeys_to_be_ranked = set()
        for pubkey in last_ranked_pubkeys:
            for edge in edges_table.search(
                    Query()['from'] == pubkey
                    and Query()['trusted'] == True
            ):
                if edge['from'] == pubkey and edge['trusted'] == True:
                    pubkeys_to_be_ranked.add(edge['to'])

        if not pubkeys_to_be_ranked:
            break
        print("Now Ranking:")
        print(pubkeys_to_be_ranked)
        total_updated_nodes = 0
        for pubkey in pubkeys_to_be_ranked:
            nodes_table.update(
                set_('rank', rank),
                (Query()['pubkey'] == pubkey) & (Query()['rank'] == -1)
            )
            # asdf = nodes_table.search(Query().pubkey == pubkey and Query().rank != -1)
            # total_updated_nodes += len(asdf)
        # if not total_updated_nodes:
        #     break

        last_ranked_pubkeys = pubkeys_to_be_ranked
        rank = rank + 1


nodes = []
privkeys = []
pubkeys = []
for x in range(0, 10):
    (pubkey, privkey) = get_rsa_pair()
    name = names.get_full_name()
    node = {'name': name, 'pubkey': pubkey, 'rank': 0, 'location': "Tel Aviv", 'shopId': 'TG' + name.split()[0]}
    nodes.append(node)
    privkeys.append(privkey)
    pubkeys.append(pubkey)
print(nodes)

def generate_edge(target, source):
    signature = rsa.sign(pubkeys[target].encode(), to_priv_pem_key(privkeys[source]), 'SHA-1')
    edge = {"from": nodes[source]["pubkey"],
            "to": nodes[target]["pubkey"],
            "trusted": True,
            "message": pubkeys[target]}
    return edge
edges = []
for sigTarget in range(1, 4):
    edges.append(generate_edge(sigTarget, 0))

edges += [generate_edge(target, 1) for target in [2,4,5]]
edges += [generate_edge(target, 2) for target in [7,5]]
edges += [generate_edge(target, 4) for target in [6,7]]
edges += [generate_edge(target, 5) for target in [9]]
edges += [generate_edge(target, 6) for target in [8,9]]



# for x in range(0, 10):
#     y = 1
#     Targets = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
#     while y < 8:
#         sigTarget = random.randint(0, 9)
#         print(sigTarget)
#         if sigTarget == x or \
#                 Targets[sigTarget] == 1:
#             continue
#         else:
#             Targets[sigTarget] = 1
#             signature = rsa.sign(pubkeys[sigTarget].encode(), to_priv_pem_key(privkeys[x]), 'SHA-1')
#             edge = {"from": nodes[x]["pubkey"],
#                     "to": nodes[sigTarget]['pubkey'],
#                     "trusted": True,
#                     "message": pubkeys[sigTarget]}
#             edges.append(edge)
#         y += 1

print("Loop done")
print(edges)
nodes_table.insert_multiple(nodes)
edges_table.insert_multiple(edges)
print("Ranking nodes")
rank_nodes_from(nodes[0]['pubkey'])
