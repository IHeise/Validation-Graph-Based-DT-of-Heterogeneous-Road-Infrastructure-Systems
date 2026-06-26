import json
from QueryPlan_Execution import execute_query_plan

def Mono_4_Querying_rev1(size):
    with open("QueryPlan_4SS.json") as f:
        query_plan = json.load(f)


    function_map={
        "get_Bridge_CountingPoint": "infranetrel.get_Bridge_CountingPoint_mono",
        "get_BridgeCondition": "bridge.get_BridgeCondition_mono",
        "get_TrafficCounting": "traffic.get_TrafficCounting_mono",
        "merge_BridgeCondition_TrafficCounting": "merging.merge_BridgeCondition_TrafficCounting"
    }
    #sizes = [1,2,3,4,5]
    result = execute_query_plan(query_plan, function_map,databasename=size)
    print(len(result))

def Mono_3_Querying_rev1(size):
    with open("QueryPlan_4SS.json") as f:
        query_plan = json.load(f)


    function_map={
        "get_Bridge_CountingPoint": "infranetrel.get_Bridge_CountingPoint_red",
        "get_BridgeCondition": "bridge.get_BridgeCondition_red",
        "get_TrafficCounting": "traffic.get_TrafficCounting_red",
        "merge_BridgeCondition_TrafficCounting": "merging.merge_BridgeCondition_TrafficCounting"
    }
    #sizes = [1,2,3,4,5]
    result = execute_query_plan(query_plan, function_map,databasename=size)
    print(len(result))

def Mono_3_Querying_all_in_one_rev1(size):
    with open("QueryPlan_mono.json") as f:
        query_plan = json.load(f)


    function_map={
        "get_Bridge_CountingPoint": "all_in_one.get_Bridge_CountingPoint_red"
    }
    #sizes = [1,2,3,4,5]
    result = execute_query_plan(query_plan, function_map,databasename=size)
    print(len(result))

def Mono_4_Querying_all_in_one_rev1(size):
    with open("QueryPlan_mono.json") as f:
        query_plan = json.load(f)


    function_map={
        "get_Bridge_CountingPoint": "all_in_one.get_Bridge_CountingPoint_mono"
    }
    #sizes = [1,2,3,4,5]
    result = execute_query_plan(query_plan, function_map,databasename=size)
    print(len(result))