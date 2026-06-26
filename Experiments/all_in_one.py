from DBinteractions.GraphCreation import *
def get_Bridge_CountingPoint_red(databasename):

    red = DBinteraction(database=f"mono-red-{databasename}")



    query = """MATCH (bridge:Bridge:RoadInfrastructureElement)-[loc1:located_at]->(l1:Localization)-[s1:starts_at]->(ref:ReferenceElement),
                (cp:CountingPoint:RoadInfrastructureElement)-[loc2:located_at]->(l2:Localization)-[s2:starts_at]->(ref)

                WHERE s1 <> s2 AND l1<>l2 AND loc1 <> loc2
                AND bridge.RoadInfrastructureElement_ID < cp.RoadInfrastructureElement_ID

                WITH 
                bridge.RoadInfrastructureElement_ID as Bridge_ID, 
                cp.RoadInfrastructureElement_ID as CountingPoint_ID
                
                MATCH (b:Bridge {Bridge_ID: Bridge_ID})
                MATCH (b)<--(i:Inspection)
                WITH  CountingPoint_ID, Bridge_ID, collect({Year: i.Age, ConditionGrade: i.Condition_Grade}) AS bridge_data
                
                MATCH (cp:CountingPoint{CountingPoint_ID:CountingPoint_ID})
                MATCH (cp)<--(t:TrafficCounting)


                WITH DISTINCT CountingPoint_ID, Bridge_ID, bridge_data,collect({Year: t.Age,Traffic:t.Traffic}) AS traffic_data

                RETURN  traffic_data, bridge_data
                
                """

    results = red.send_query_(query=query)

    records = [dict(record) for record in results]
    print(len(records))

    return records


def get_Bridge_CountingPoint_mono(databasename):


    mono = DBinteraction(database=f"mono-complete-{databasename}")

    query = """MATCH (bridge:Bridge:RoadInfrastructureElement)-[loc1:located_at]->(l1:Localization)-[s1:starts_at]->(ref:ReferenceElement),
                (cp:CountingPoint:RoadInfrastructureElement)-[loc2:located_at]->(l2:Localization)-[s2:starts_at]->(ref)

                WHERE s1 <> s2 AND l1<>l2 AND loc1 <> loc2
                AND bridge.RoadInfrastructureElement_ID < cp.RoadInfrastructureElement_ID

                WITH 
                bridge.RoadInfrastructureElement_ID as Bridge_ID, 
                cp.RoadInfrastructureElement_ID as CountingPoint_ID

                MATCH (b:Bridge {Bridge_ID: Bridge_ID})
                MATCH (b)<--(i:Inspection)
                WITH  CountingPoint_ID, Bridge_ID, collect({Year: i.Age, ConditionGrade: i.Condition_Grade}) AS bridge_data

                MATCH (cp:CountingPoint{CountingPoint_ID:CountingPoint_ID})
                MATCH (cp)<--(t:TrafficCounting)


                WITH DISTINCT CountingPoint_ID, Bridge_ID, bridge_data,collect({Year: t.Age,Traffic:t.Traffic}) AS traffic_data

                RETURN  traffic_data, bridge_data


                """

    results = mono.send_query_(query=query)

    records = [dict(record) for record in results]
    print(len(records))

    return records