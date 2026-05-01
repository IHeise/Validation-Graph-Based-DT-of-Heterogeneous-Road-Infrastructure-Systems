from DBinteractions.GraphCreation import *



def get_Bridge_CountingPoint_Pairs(databasename):

    infranet = GraphCreation(DataBaseName=databasename)

    query = f"""
            MATCH (bridge:Bridge:RoadInfrastructureElement)-[loc1:located_at]->(l1:Localization)-[s1:starts_at]->(ref:ReferenceElement),
            (cp:CountingPoint:RoadInfrastructureElement)-[loc2:located_at]->(l2:Localization)-[s2:starts_at]->(ref)
            
            WHERE s1 <> s2 AND l1<>l2 AND loc1 <> loc2
            AND bridge.RoadInfrastructureElement_ID < cp.RoadInfrastructureElement_ID
            
            RETURN 
            bridge.RoadInfrastructureElement_ID as Bridge, 
            cp.RoadInfrastructureElement_ID as CountingPoint
            
            """
    result = infranet.send_query_parallel(query=query)


    data = [
            {"Bridge_ID": row["Bridge"], "CountingPoint_ID": row["CountingPoint"]}
            for row in result
        ]
    return data