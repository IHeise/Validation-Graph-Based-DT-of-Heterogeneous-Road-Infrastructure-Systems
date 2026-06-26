import json
from QueryPlan_Execution import execute_query_plan

def SoS_5_Querying_rev1(size):
    with open("QueryPlan_5SS.json") as f:
        query_plan = json.load(f)


    function_map={
        "get_Bridge_CountingPoint": "infranetrel.get_Bridge_CountingPoint",
        "get_BridgeCondition": "bridge.get_BridgeCondition",
        "get_TrafficCounting": "traffic.get_TrafficCounting",
        "merge_BridgeCondition_TrafficCounting": "merging.merge_BridgeCondition_TrafficCounting",
        "get_TempRel": "temprel.get_TempRel"
    }
    result = execute_query_plan(query_plan, function_map,databasename=size)

def SoS_4_Querying_rev1(size):
    with open("QueryPlan_4SS.json") as f:
        query_plan = json.load(f)


    function_map={
        "get_Bridge_CountingPoint": "infranetrel.get_Bridge_CountingPoint",
        "get_BridgeCondition": "bridge.get_BridgeCondition",
        "get_TrafficCounting": "traffic.get_TrafficCounting",
        "merge_BridgeCondition_TrafficCounting": "merging.merge_BridgeCondition_TrafficCounting"
    }
  
    result = execute_query_plan(query_plan, function_map,databasename=size)
    



