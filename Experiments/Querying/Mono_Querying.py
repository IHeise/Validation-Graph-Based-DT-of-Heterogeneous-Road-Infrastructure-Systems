from DBinteractions.GraphCreation import *
from ExperimentI_GraphSizes.Modul2_Evaluation.Queries.InfraNetQuerying import *
from ExperimentI_GraphSizes.Modul2_Evaluation.Queries.BridgeQuerying import *
from ExperimentI_GraphSizes.Modul2_Evaluation.Queries.TrafficQuerying import *
from ExperimentI_GraphSizes.Modul2_Evaluation.Queries.Temp_Querying import *

def get_condition_grades_with_traffic_mono_old(index):
    mono = GraphCreation(DataBaseName=f"mono-complete-{index}")


    query = f"""
            MATCH (ref:ReferenceElement)

            MATCH (bridge:Bridge:RoadInfrastructureElement)
              -[:located_at]->(l1:Localization)
              -[:starts_at]->(ref)

            MATCH (cp:CountingPoint:RoadInfrastructureElement)
                  -[:located_at]->(l2:Localization)
                  -[:starts_at]->(ref)

            WHERE l1 <> l2
              AND bridge.RoadInfrastructureElement_ID < cp.RoadInfrastructureElement_ID
              
            WITH bridge, cp

            // Aggregate conditions per bridge
            CALL (bridge){{
              MATCH (bridge)<--(i:Inspection)
              RETURN collect({{Age: i.Age, ConditionGrade: i.Condition_Grade}}) AS Conditions
            }}

            // Aggregate traffic per counting point
            CALL (cp){{
              MATCH (cp)<--(t:TrafficCounting)
              RETURN collect({{Age: t.Age, Traffic: t.Traffic}}) AS TrafficRecords
            }}

            RETURN DISTINCT
              bridge.RoadInfrastructureElement_ID AS Bridge,
              cp.RoadInfrastructureElement_ID AS CountingPoint,
              Conditions,
              TrafficRecords

            """
    result = mono.send_query_parallel(query=query)

    data = [
        {"Bridge_ID": row["Bridge"],
         "Conditions": row["Conditions"],
         "CountingPoint_ID": row["CountingPoint"],
         "TrafficRecords": row["TrafficRecords"]}
        for row in result
    ]
    return data

def get_condition_grades_with_traffic_mono(index):
    #infranet
    data = get_Bridge_CountingPoint_Pairs(databasename=f"mono-complete-{index}")

    #print("infranet done")

    #bridges
    bridge_ids = {d["Bridge_ID"] for d in data}
    bridges = [{"Bridge_ID": bid} for bid in bridge_ids]

    bridge_conditions = get_Bridge_Conditions_parallel(databasename=f"mono-complete-{index}",bridges=bridges)


    #print("bridge done")

    #traffic
    count_ids = {d["CountingPoint_ID"] for d in data}
    countingpoints = [{"CountingPoint_ID": cid} for cid in count_ids]
    traffic_records = get_Traffic_Counts_parallel(databasename=f"mono-complete-{index}",countingpoints=countingpoints)

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

    return merged


def get_condition_grades_with_traffic_mono_red_old(index):
    mono = GraphCreation(DataBaseName=f"mono-red-{index}")

    query = f"""
            MATCH (ref:ReferenceElement)

            MATCH (bridge:Bridge:RoadInfrastructureElement)
              -[:located_at]->(l1:Localization)
              -[:starts_at]->(ref)

            MATCH (cp:CountingPoint:RoadInfrastructureElement)
                  -[:located_at]->(l2:Localization)
                  -[:starts_at]->(ref)

            WHERE l1 <> l2
              AND bridge.RoadInfrastructureElement_ID < cp.RoadInfrastructureElement_ID

            WITH bridge, cp

            // Aggregate conditions per bridge
            CALL (bridge){{
              MATCH (bridge)<--(i:Inspection)
              RETURN collect({{Age: i.Age, ConditionGrade: i.Condition_Grade}}) AS Conditions
            }}

            // Aggregate traffic per counting point
            CALL (cp){{
              MATCH (cp)<--(t:TrafficCounting)
              RETURN collect({{Age: t.Age, Traffic: t.Traffic}}) AS TrafficRecords
            }}

            RETURN DISTINCT
              bridge.RoadInfrastructureElement_ID AS Bridge,
              cp.RoadInfrastructureElement_ID AS CountingPoint,
              Conditions,
              TrafficRecords

            """
    result = mono.send_query_parallel(query=query)

    data = [
        {"Bridge_ID": row["Bridge"],
         "Conditions": row["Conditions"],
         "CountingPoint_ID": row["CountingPoint"],
         "TrafficRecords": row["TrafficRecords"]}
        for row in result
    ]
    return data


def get_condition_grades_with_traffic_mono_red(index):
    # infranet
    data = get_Bridge_CountingPoint_Pairs(databasename=f"mono-red-{index}")

    # print("infranet done")

    # bridges
    bridge_ids = {d["Bridge_ID"] for d in data}
    bridges = [{"Bridge_ID": bid} for bid in bridge_ids]

    bridge_conditions = get_Bridge_Conditions_parallel(databasename=f"mono-red-{index}", bridges=bridges)

    # print("bridge done")

    # traffic
    count_ids = {d["CountingPoint_ID"] for d in data}
    countingpoints = [{"CountingPoint_ID": cid} for cid in count_ids]
    traffic_records = get_Traffic_Counts_parallel(databasename=f"mono-red-{index}", countingpoints=countingpoints)

    # print("traffic done")

    # merging
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

        # merged.append({
        #    "TrafficRecords": count_map.get(cid, []),
        #    "Conditions": all_conditions

        merged.append(
            count_map.get(cid, []) + all_conditions
        )
    print(len(merged))
    return merged




