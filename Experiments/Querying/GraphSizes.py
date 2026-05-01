from DBinteractions.GraphCreation import *

def get_graphsize(databasename):
    db = GraphCreation(DataBaseName=databasename)
    query = f"""
            CALL db.stats.retrieve('GRAPH COUNTS') YIELD data
            RETURN
            data.nodes[0].count AS nodes,
            data.relationships[0].count AS edges
            """

    result = db.send_query_parallel(query=query)[0]

    return result["nodes"], result["edges"]

