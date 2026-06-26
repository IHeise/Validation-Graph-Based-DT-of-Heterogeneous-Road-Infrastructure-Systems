from DBinteractions.GraphCreation import *
def get_BridgeCondition(BridgeCountingpointPairs,databasename):
    #print("2 reached")

    bridge = DBinteraction(database=f"sos-bridge-{databasename}")

    bridge_ids = list({
        item["Bridge_ID"]
        for item in BridgeCountingpointPairs
        if "Bridge_ID" in item and item["Bridge_ID"] is not None
    })

    ids = {"bridge_ids": list(bridge_ids)}

    query = """UNWIND $bridge_ids AS id
                MATCH (b:Bridge {Bridge_ID: id})
                MATCH (b)<--(i:Inspection)
                WITH b.Bridge_ID as Bridge_ID, collect({Year: i.Age, ConditionGrade: i.Condition_Grade}) AS data
                RETURN Bridge_ID, data
                """
    results = bridge.send_query_(query=query, data=ids)

    records = [dict(record) for record in results]
    print(len(records))

    return records

def get_BridgeCondition_mono(BridgeCountingpointPairs,databasename):
    #print("2 reached")

    bridge = DBinteraction(database=f"mono-complete-{databasename}")

    bridge_ids = list({
        item["Bridge_ID"]
        for item in BridgeCountingpointPairs
        if "Bridge_ID" in item and item["Bridge_ID"] is not None
    })

    ids = {"bridge_ids": list(bridge_ids)}

    query = """UNWIND $bridge_ids AS id
                MATCH (b:Bridge {Bridge_ID: id})
                MATCH (b)<--(i:Inspection)
                WITH b.Bridge_ID as Bridge_ID, collect({Year: i.Age, ConditionGrade: i.Condition_Grade}) AS data
                RETURN Bridge_ID, data
                """
    results = bridge.send_query_(query=query, data=ids)

    records = [dict(record) for record in results]
    print(len(records))

    return records


def get_BridgeCondition_red(BridgeCountingpointPairs,databasename):
    #print("2 reached")

    bridge = DBinteraction(database=f"mono-red-{databasename}")

    bridge_ids = list({
        item["Bridge_ID"]
        for item in BridgeCountingpointPairs
        if "Bridge_ID" in item and item["Bridge_ID"] is not None
    })

    ids = {"bridge_ids": list(bridge_ids)}

    query = """UNWIND $bridge_ids AS id
                MATCH (b:Bridge {Bridge_ID: id})
                MATCH (b)<--(i:Inspection)
                WITH b.Bridge_ID as Bridge_ID, collect({Year: i.Age, ConditionGrade: i.Condition_Grade}) AS data
                RETURN Bridge_ID, data
                """
    results = bridge.send_query_(query=query, data=ids)

    records = [dict(record) for record in results]
    print(len(records))

    return records
