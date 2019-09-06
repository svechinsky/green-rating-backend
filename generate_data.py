from tinydb import TinyDB, Query
from tinydb.operations import set as set_
from app import get_rsa_pair, to_priv_pem_key
import random, rsa

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

def rank_nodes(initial_node_pubkey):
    nodes_table.update(set_('rank', -1))
    nodes_table.update(set_('rank', 0), Query().pubkey == initial_node_pubkey)

    rank = 1
    last_ranked_pubkeys = {initial_node_pubkey}
    while True:
        pubkeys_to_be_ranked = set()
        for pubkey in last_ranked_pubkeys:
            for edge in edges_table.search(
                    Query()['to'] == pubkey
                    and Query()['trusted'] == True
            ):
                if edge['to'] == pubkey and edge['trusted'] == True:
                    pubkeys_to_be_ranked.add(edge['from'])

        if not pubkeys_to_be_ranked:
            break

        total_updated_nodes = 0
        for pubkey in pubkeys_to_be_ranked:
            nodes_table.update(
                set_('rank', rank),
                Query().pubkey == pubkey and Query().rank != -1
            )
            asdf = nodes_table.search(Query().pubkey == pubkey and Query().rank != -1)
            total_updated_nodes += len(asdf)
        if not total_updated_nodes:
            break

        last_ranked_pubkeys = pubkeys_to_be_ranked
        rank += 1


nodes = []
privkeys = []
pubkeys = []
for x in range(0, 10):
    (pubkey, privkey) = get_rsa_pair()
    node = {'name': chr(x + 65), 'pubkey': pubkey, 'rank': 0}
    nodes.append(node)
    privkeys.append(privkey)
    pubkeys.append(pubkey)
print(nodes)

edges = []
for x in range(0, 10):
    y = 1
    Targets = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    while y < 8:
        sigTarget = random.randint(0, 9)
        if sigTarget == x or \
                Targets[sigTarget] == 1:
            pass
        else:
            Targets[sigTarget] = 1
            signature = rsa.sign(pubkeys[sigTarget].encode(), to_priv_pem_key(privkeys[x]), 'SHA-1')
            edge = {"from": nodes[x]["pubkey"],
                    "to": nodes[sigTarget]['pubkey'],
                    "trusted": True,
                    "message": pubkeys[sigTarget]}
            edges.append(edge)
        y += 1


nodes_table.insert_multiple(nodes)
edges_table.insert_multiple(edges)

rank_nodes(nodes[0]['pubkey'])
