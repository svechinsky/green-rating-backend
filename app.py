from flask import Flask, jsonify, request
from tinydb import TinyDB, Query
from config import privkey, pubkey, name
import rsa
from utils import *
from flask_cors import CORS

db = TinyDB('gdata.json', indent=4)
nodes_table = db.table('nodes')
edges_table = db.table('edges')


app = Flask(__name__)
CORS(app)


# noinspection PyBroadException
def verify_rsa_key(message, signature, pubkey):
    try:
        if rsa.verify(message, signature, to_pub_pem_key(pubkey)):
            return True
    except:
        return False


def is_edge_approved(edge):
    return verify_rsa_key(
        edge['to'],
        edge['signature'],
        edge['from']
    )


def approve_edge(edge):
    edge['is_approved'] = is_edge_approved(edge)


# def rank_nodes(initial_node_pubkey):
#     nodes_table.update(set('rank', -1))
#     nodes_table.update(set('rank', 0), Query().pubkey == initial_node_pubkey)
#
#     rank = 1
#     curr_pubkeys = [initial_node_pubkey]
#     while True:
#         new_pubkeys = []
#         for pubkey in curr_pubkeys:
#             for edge in edges_table.search(
#                     Query()['from'] == pubkey
#                     and Query()['is_approved'] == True
#             ):
#                 new_pubkeys.append(edge['to'])
#
#         if not new_pubkeys:
#             break
#
#         total_updated_nodes = 0
#         for pubkey in new_pubkeys:
#             nodes_table.update(
#                 set('rank', rank),
#                 Query().pubkey == pubkey and Query().rank != -1
#             )
#             total_updated_nodes += len(nodes_table.search(Query().pubkey == pubkey and Query().rank != -1))
#         if not total_updated_nodes:
#             break
#
#         curr_pubkeys = new_pubkeys
#         rank += 1


def get_only_entities(entities_with_sig):
    return [x['entity'] for x in entities_with_sig]


@app.route('/api/v1/entities')
def entities():
    return jsonify(nodes_table.all())


@app.route('/api/v1/approved-entities')
def approved_entities():
    return jsonify(nodes_table.search(Query().rank > 0))


@app.route('/api/v1/trusted-entities')
def trusted_entities():
    return jsonify(nodes_table.search(Query().rank == 1))


@app.route('/api/v1/me')
def me():
    return jsonify(nodes_table.search(Query().rank == 0)[0])


@app.route('/api/v1/add-entity', methods=['POST'])
def add_entity():
    # receives node that signed you, and graph from its perspective
    data = request.json
    edges_ = data['graph']['edges']
    for edge in edges_:
        edges_table.upsert(
            edge,(
            (Query()['from'] == edge['from']) &
            (Query()['to'] == edge['to'])),
        )

    nodes_ = data['graph']['nodes']
    for node in nodes_:
        nodes_table.upsert(
            node,
            Query().pubkey == node['pubkey']
        )

    # rank_nodes(pubkey)
    rank_nodes_from(pubkey, nodes_table, edges_table)

    node = data['node']['pubkey']
    # returns current node
    return nodes_table.search(Query().pubkey == node)[0]

def get_edges_to_node(node, rank):
    total_edges = []
    last_gen_pubkeys = {node['pubkey']}
    for rank in range(1, rank+1):
        new_edges = []
        for pubkey in last_gen_pubkeys:
            new_edges += edges_table.search(Query().to==pubkey)
        total_edges += new_edges
        last_gen_pubkeys = {edge['from'] for edge in new_edges }
    return total_edges

@app.route('/api/v1/sign-entity', methods=['POST'])
def sign_entity():
    # receives node to sign
    data = request.json
    pubkey_to_sign = data['pubkey']
    signature = rsa.sign(pubkey_to_sign.encode(), to_priv_pem_key(privkey), 'SHA-1')
    nodes_table.upsert(data, Query().pubkey==data['pubkey'])
    edges_table.upsert(
        {'from': pubkey, 'to': pubkey_to_sign, 'message':pubkey_to_sign,
         'signature': signature.hex(), 'trusted': True},
        (Query()['from']== pubkey)& (Query()['to']== pubkey_to_sign)
    )
    rank_nodes_from(pubkey, nodes_table, edges_table)
    # return nodes and edges as they are, and current node
    return jsonify({'graph': {'edges': get_edges_to_node(data,3), 'nodes': nodes_table.all()},
                    'node': data})



if __name__ == '__main__':
    rank_nodes_from(pubkey, nodes_table, edges_table)
    app.run('0.0.0.0', 5000)
