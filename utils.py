import rsa
from tinydb import Query
from tinydb.operations import set as set_


def to_hex_der(pem_key):
    return pem_key.save_pkcs1('DER').hex()


def to_priv_pem_key(hex_der):
    return rsa.PrivateKey.load_pkcs1(bytes.fromhex(hex_der), 'DER')


def to_pub_pem_key(hex_der):
    return rsa.PublicKey.load_pkcs1(bytes.fromhex(hex_der), 'DER')


def get_rsa_pair():
    return tuple(to_hex_der(key) for key in rsa.newkeys(512))


def rank_nodes_from(initial_node_pubkey, nodes_table, edges_table):
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