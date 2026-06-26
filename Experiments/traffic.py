from DBinteractions.GraphCreation import *

def get_TrafficCounting(BridgeCountingpointPairs,databasename):
    #print("3 reached")
    traffic = DBinteraction(database=f"sos-traffic-{databasename}")

    cp_ids = list({
        item["CountingPoint_ID"]  # NO strip()
        for item in BridgeCountingpointPairs
        if "CountingPoint_ID" in item and item["CountingPoint_ID"] is not None
    })

    ids = {"cp_ids": cp_ids}

    query = f"""
            UNWIND $cp_ids AS id
            MATCH (cp:CountingPoint{{CountingPoint_ID:id}})
            MATCH (cp)<--(t:TrafficCounting)
   
            
            WITH DISTINCT   cp.CountingPoint_ID AS CountingPoint_ID,
                            collect({{Year: t.Age, 
                            Traffic:t.Traffic}})AS data
                            
            RETURN  CountingPoint_ID, data
            
            """
    results = traffic.send_query(query=query, data=ids)

    records = [dict(record) for record in results]
    print(len(records))

    return records



def get_TrafficCounting_red(BridgeCountingpointPairs, databasename):
    # print("3 reached")
    traffic = DBinteraction(database=f"mono-red-{databasename}")

    cp_ids = list({
        item["CountingPoint_ID"]  # NO strip()
        for item in BridgeCountingpointPairs
        if "CountingPoint_ID" in item and item["CountingPoint_ID"] is not None
    })

    ids = {"cp_ids": cp_ids}

    query = f"""
            UNWIND $cp_ids AS id
            MATCH (cp:CountingPoint{{CountingPoint_ID:id}})
            MATCH (cp)<--(t:TrafficCounting)


            WITH DISTINCT   cp.CountingPoint_ID AS CountingPoint_ID,
                            collect({{Year: t.Age, 
                            Traffic:t.Traffic}})AS data

            RETURN  CountingPoint_ID, data

            """
    results = traffic.send_query(query=query, data=ids)

    records = [dict(record) for record in results]
    print(len(records))

    return records

def get_TrafficCounting_mono(BridgeCountingpointPairs, databasename):
    # print("3 reached")
    traffic = DBinteraction(database=f"mono-complete-{databasename}")

    cp_ids = list({
        item["CountingPoint_ID"]  # NO strip()
        for item in BridgeCountingpointPairs
        if "CountingPoint_ID" in item and item["CountingPoint_ID"] is not None
    })

    ids = {"cp_ids": cp_ids}

    query = f"""
            UNWIND $cp_ids AS id
            MATCH (cp:CountingPoint{{CountingPoint_ID:id}})
            MATCH (cp)<--(t:TrafficCounting)


            WITH DISTINCT   cp.CountingPoint_ID AS CountingPoint_ID,
                            collect({{Year: t.Age, 
                            Traffic:t.Traffic}})AS data

            RETURN  CountingPoint_ID, data

            """
    results = traffic.send_query(query=query, data=ids)

    records = [dict(record) for record in results]
    print(len(records))

    return records
