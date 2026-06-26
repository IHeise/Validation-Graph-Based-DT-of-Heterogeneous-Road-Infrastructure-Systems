def merge_BridgeCondition_TrafficCounting(input,databasename):

    #print("4 reached")
    D_bridge, D_traffic = input["data"]
    M = input["mapping"]

    bridge_map = {x["Bridge_ID"]: x["data"] for x in D_bridge}
    traffic_map = {x["CountingPoint_ID"]: x["data"] for x in D_traffic}

    R = []

    for t in M:
        entry = []
        bridge_id = t["Bridge_ID"]
        cp_id = t["CountingPoint_ID"]

        # skip if either side is missing
        if bridge_id not in bridge_map:
            continue

        if cp_id not in traffic_map:
            continue

        merged_entry = {"data":bridge_map[bridge_id]+traffic_map[cp_id]}


        R.append(merged_entry)
    print(len(R))
    return R


