from DBinteractions.GraphCreation import *

def get_Bridge_CountingPoint(databasename):
    #print("1 reached")

    infranet=DBinteraction(database=f"sos-infranet-{databasename}")

    query = f"""
                MATCH (bridge:Bridge:RoadInfrastructureElement)-[loc1:located_at]->(l1:Localization)-[s1:starts_at]->(ref:ReferenceElement),
                (cp:CountingPoint:RoadInfrastructureElement)-[loc2:located_at]->(l2:Localization)-[s2:starts_at]->(ref)


                RETURN 
                bridge.RoadInfrastructureElement_ID as Bridge_ID, 
                cp.RoadInfrastructureElement_ID as CountingPoint_ID

                """

    results = infranet.send_query(query=query)

    records = [dict(record) for record in results]

    print(len(records))

    return records

def get_Bridge_CountingPoint_mono(databasename):
    #print("1 reached")

    infranet=DBinteraction(database=f"mono-complete-{databasename}")

    query = f"""
                MATCH (bridge:Bridge:RoadInfrastructureElement)-[loc1:located_at]->(l1:Localization)-[s1:starts_at]->(ref:ReferenceElement),
                (cp:CountingPoint:RoadInfrastructureElement)-[loc2:located_at]->(l2:Localization)-[s2:starts_at]->(ref)

                WHERE s1 <> s2 AND l1<>l2 AND loc1 <> loc2
                AND bridge.RoadInfrastructureElement_ID < cp.RoadInfrastructureElement_ID

                RETURN 
                bridge.RoadInfrastructureElement_ID as Bridge_ID, 
                cp.RoadInfrastructureElement_ID as CountingPoint_ID

                """

    results = infranet.send_query(query=query)

    records = [dict(record) for record in results]

    print(len(records))

    return records

def get_Bridge_CountingPoint_red(databasename):
    #print("1 reached")

    infranet=DBinteraction(database=f"mono-red-{databasename}")

    query = f"""
                MATCH (bridge:Bridge:RoadInfrastructureElement)-[loc1:located_at]->(l1:Localization)-[s1:starts_at]->(ref:ReferenceElement),
                (cp:CountingPoint:RoadInfrastructureElement)-[loc2:located_at]->(l2:Localization)-[s2:starts_at]->(ref)

                WHERE s1 <> s2 AND l1<>l2 AND loc1 <> loc2
                AND bridge.RoadInfrastructureElement_ID < cp.RoadInfrastructureElement_ID

                RETURN 
                bridge.RoadInfrastructureElement_ID as Bridge_ID, 
                cp.RoadInfrastructureElement_ID as CountingPoint_ID

                """

    results = infranet.send_query(query=query)

    records = [dict(record) for record in results]

    print(len(records))

    return records


