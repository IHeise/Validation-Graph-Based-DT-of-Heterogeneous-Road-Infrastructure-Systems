from DBinteractions.GraphCreation import *
from ExperimentI_GraphSizes.Modul2_Evaluation.Queries.InfraNetQuerying import *
from ExperimentI_GraphSizes.Modul2_Evaluation.Queries.BridgeQuerying import *
from ExperimentI_GraphSizes.Modul2_Evaluation.Queries.TrafficQuerying import *
from ExperimentI_GraphSizes.Modul2_Evaluation.Queries.Temp_Querying import *

def get_condition_grades_with_traffic_SoS(index):
    #infranet
    data = get_Bridge_CountingPoint_Pairs(databasename=f"sos-infranet-{index}")

    #print("infranet done")

    #bridges
    bridge_ids = {d["Bridge_ID"] for d in data}
    bridges = [{"Bridge_ID": bid} for bid in bridge_ids]

    bridge_conditions = get_Bridge_Conditions_parallel(databasename=f"sos-bridge-{index}",bridges=bridges)


    #print("bridge done")

    #traffic
    count_ids = {d["CountingPoint_ID"] for d in data}
    countingpoints = [{"CountingPoint_ID": cid} for cid in count_ids]
    traffic_records = get_Traffic_Counts_parallel(databasename=f"sos-traffic-{index}",countingpoints=countingpoints)

    #print("traffic done")

    #merging
    merged = []


    bridge_map = {
        b["Bridge_ID"]: b["Conditions"]
        for b in bridge_conditions
    }

    count_map = {
        c["CountingPoint_ID"]: c["TrafficRecords"]
        for c in traffic_records
    }

    cp_to_bridges = {}

    for d in data:
        cid = d["CountingPoint_ID"]
        bid = d["Bridge_ID"]

        if cid not in cp_to_bridges:
            cp_to_bridges[cid] = []

        cp_to_bridges[cid].append(bid)

    for cid, bridge_ids in cp_to_bridges.items():
        all_conditions = []

        for bid in bridge_ids:
            if bid in bridge_map:
                all_conditions.extend(bridge_map[bid])

        #merged.append({
        #    "TrafficRecords": count_map.get(cid, []),
        #    "Conditions": all_conditions

        merged.append(
             count_map.get(cid, []) + all_conditions
        )

    #print("merging done")

    create_TempRel_parallel(databasename=f"sos-temp-{index}",data=merged)
    #create_TempRel(databasename=f"sos-temp-{index}", data=merged)

    result = get_Temp_Rel(databasename=f"sos-temp-{index}")

    return result


def get_condition_grades_with_traffic_SoS_withoutTemp(index):
    #infranet
    data = get_Bridge_CountingPoint_Pairs(databasename=f"sos-infranet-{index}")

    #print("infranet done")

    #bridges
    bridge_ids = {d["Bridge_ID"] for d in data}
    bridges = [{"Bridge_ID": bid} for bid in bridge_ids]

    bridge_conditions = get_Bridge_Conditions_parallel(databasename=f"sos-bridge-{index}",bridges=bridges)


    #print("bridge done")

    #traffic
    count_ids = {d["CountingPoint_ID"] for d in data}
    countingpoints = [{"CountingPoint_ID": cid} for cid in count_ids]
    traffic_records = get_Traffic_Counts_parallel(databasename=f"sos-traffic-{index}",countingpoints=countingpoints)

    #print("traffic done")

    #merging
    merged = []


    bridge_map = {
        b["Bridge_ID"]: b["Conditions"]
        for b in bridge_conditions
    }

    count_map = {
        c["CountingPoint_ID"]: c["TrafficRecords"]
        for c in traffic_records
    }

    cp_to_bridges = {}

    for d in data:
        cid = d["CountingPoint_ID"]
        bid = d["Bridge_ID"]

        if cid not in cp_to_bridges:
            cp_to_bridges[cid] = []

        cp_to_bridges[cid].append(bid)

    for cid, bridge_ids in cp_to_bridges.items():
        all_conditions = []

        for bid in bridge_ids:
            if bid in bridge_map:
                all_conditions.extend(bridge_map[bid])

        #merged.append({
        #    "TrafficRecords": count_map.get(cid, []),
        #    "Conditions": all_conditions

        merged.append(
             count_map.get(cid, []) + all_conditions
        )

    #print("merging done")



    return merged


