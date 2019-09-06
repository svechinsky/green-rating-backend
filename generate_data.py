from tinydb import TinyDB, Query
from tinydb.operations import set as set_
from app import get_rsa_pair, to_priv_pem_key
import random, rsa
from utils import rank_nodes_from
import names

db = TinyDB('gdata.json', indent=4)
nodes_table = db.table('nodes')
edges_table = db.table('edges')





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
rank_nodes_from(nodes[0]['pubkey'], nodes_table, edges_table)

print('Generating config file...')
cfg_node_index = 0
config_file_content = f'''# keys are in hexadecimal DER format
pubkey = '{pubkeys[cfg_node_index]}'
privkey = '{privkeys[cfg_node_index]}'
name = '{nodes[cfg_node_index]['name']}'
node = {nodes[cfg_node_index]}
'''
print('Printing config file...')
with open('config.py', 'w') as f:
    f.write(config_file_content)
print('Config file generated!')

