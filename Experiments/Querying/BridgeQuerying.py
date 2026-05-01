from DBinteractions.GraphCreation import *
from concurrent.futures import ThreadPoolExecutor, as_completed

def chunk_list(data, chunk_size):
    for i in range(0, len(data), chunk_size):
        yield data[i:i + chunk_size]


def get_Bridge_Conditions_parallel(databasename, bridges,
                                   chunk_size=50000, max_workers=1):

    results = []
    bridge_ids = [b["Bridge_ID"] for b in bridges]

    # Split input into chunks
    chunks = list(chunk_list(bridge_ids, chunk_size))

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(get_Bridge_Conditions, databasename, chunk)
            for chunk in chunks
        ]

        for future in as_completed(futures):
            try:
                results.extend(future.result())
            except Exception as e:
                print(f"Worker failed: {e}")

    return results


def get_Bridge_Conditions(databasename,bridges):
    bridge = GraphCreation(DataBaseName=databasename)

    query = f"""
            UNWIND $ids AS id
            MATCH (bridge:Bridge {{Bridge_ID: id}})<--(i:Inspection)
            WITH 
                bridge, i
                ORDER BY i.Age
            
            WITH 
                bridge.Bridge_ID AS bridge,
                collect({{Age: i.Age, ConditionGrade: i.Condition_Grade}}) AS Conditions
            
            RETURN 
                bridge as Bridge,
                [i IN range(0, size(Conditions)-1) |
                    {{
                        start: CASE WHEN i = 0 THEN 0 ELSE Conditions[i-1].Age END,
                        end: Conditions[i].Age,
                        data: Conditions[i].ConditionGrade,
                        type: "ConditionGrade"
                    }}
                ] AS intervals
            """
    # query = f"""
    #             UNWIND $ids as id
    #             MATCH (b:Bridge {{Bridge_ID: id}})<--(i:Inspection)
    #             WITH
    #                 b.Bridge_ID as bridge,
    #                 i
    #                 ORDER BY i.Age
    #
    #         WITH
    #             bridge,
    #             collect({{Age: i.Age, ConditionGrade: i.Condition_Grade}}) as Conditions
    #
    #         WITH
    #             bridge,
    #             Conditions,
    #             range(0, size(Conditions)-1) as idx
    #
    #         RETURN
    #             bridge as Bridge,
    #             [i IN idx |
    #                 {{
    #                     start: CASE WHEN i = 0 THEN 0 ELSE Conditions[i-1].Age END,
    #                     end: Conditions[i].Age,
    #                     data: Conditions[i].ConditionGrade,
    #                     type: "ConditionGrade"
    #                 }}
    #             ] as intervals
    #             """

    result = bridge.send_query_parallel(query=query,data={"ids":bridges})

    #data = [
    #    {"Bridge_ID": row["Bridge"], "Conditions": row["intervals"]}
    #    for row in result
    #]
    #return data
    return[
        {"Bridge_ID": row["Bridge"], "Conditions": row["intervals"]}
    for row in result
    ]


# def get_Bridge_Conditions_parallel_(databasename, bridges,
#                                    chunk_size=10000, max_workers=16):
#     results = []
#     bridge_ids = [b["Bridge_ID"] for b in bridges]
#     # Split input into chunks
#     chunks = list(chunk_list(bridge_ids, chunk_size))
#
#     with ThreadPoolExecutor(max_workers=max_workers) as executor:
#         futures = [
#             executor.submit(get_Bridge_Conditions, databasename, chunk)
#             for chunk in chunks
#         ]
#
#         for future in as_completed(futures):
#             try:
#                 results.extend(future.result())
#             except Exception as e:
#                 print(f"Worker failed: {e}")
#
#     return results
#
#
# def get_Bridge_Conditions_(databasename, bridges):
#     bridge = GraphCreation(DataBaseName=databasename)
#
#     query = f"""
#             UNWIND $data as b
#             MATCH (bridge:Bridge{{Bridge_ID:b.Bridge_ID}})<--(i:Inspection)
#             WITH
#                 b.Bridge_ID as bridge,
#                 collect({{Age:i.Age,ConditionGrade:i.Condition_Grade}}) as Conditions
#
#             WITH
#                 bridge,
#                 Conditions,
#                 range(0, size(Conditions)-1) as idx
#
#             RETURN DISTINCT
#             bridge as Bridge,
#             [i IN idx |
#                 {{
#                     start: CASE WHEN i = 0 THEN 0 ELSE Conditions[i-1].Age END,
#                     end: Conditions[i].Age,
#                     data: Conditions[i].ConditionGrade,
#                     type: \"ConditionGrade\"
#                 }}
#             ] as intervals
#             """
#     query = f"""
#             UNWIND $data as b
#             MATCH (bridge:Bridge {{Bridge_ID: b.Bridge_ID}})<--(i:Inspection)
#             WITH
#                 b.Bridge_ID as bridge,
#                 i
#                 ORDER BY i.Age
#
#         WITH
#             bridge,
#             collect({{Age: i.Age, ConditionGrade: i.Condition_Grade}}) as Conditions
#
#         WITH
#             bridge,
#             Conditions,
#             range(0, size(Conditions)-1) as idx
#
#         RETURN
#             bridge as Bridge,
#             [i IN idx |
#                 {{
#                     start: CASE WHEN i = 0 THEN 0 ELSE Conditions[i-1].Age END,
#                     end: Conditions[i].Age,
#                     data: Conditions[i].ConditionGrade,
#                     type: "ConditionGrade"
#                 }}
#             ] as intervals
#             """
#
#
#     result = bridge.send_query_parallel(query=query, data={"data": bridges})
#
#     data = [
#         {"Bridge_ID": row["Bridge"], "Conditions": row["intervals"]}
#         for row in result
#     ]
#     return data