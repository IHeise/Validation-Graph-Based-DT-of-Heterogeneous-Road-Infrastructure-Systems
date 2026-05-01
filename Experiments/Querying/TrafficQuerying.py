from DBinteractions.GraphCreation import *
from concurrent.futures import ThreadPoolExecutor, as_completed

def chunk_list(data, chunk_size):
    for i in range(0, len(data), chunk_size):
        yield data[i:i + chunk_size]


def get_Traffic_Counts_parallel(databasename, countingpoints,
                                   chunk_size=100000, max_workers=1):

    results = []
    cp_ids = [cp["CountingPoint_ID"] for cp in countingpoints]
    # Split input into chunks
    chunks = list(chunk_list(cp_ids, chunk_size))

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(get_TrafficCounts, databasename, chunk)
            for chunk in chunks
        ]

        for future in as_completed(futures):
            try:
                results.extend(future.result())
            except Exception as e:
                print(f"Worker failed: {e}")

    return results


def get_TrafficCounts(databasename,countingpoints):
    traffic = GraphCreation(DataBaseName=databasename)

    query = f"""
            UNWIND $ids AS id
            MATCH (countingpoint:CountingPoint{{CountingPoint_ID:id}})<--(t:TrafficCounting)
            
            WITH 
                countingpoint, t
                ORDER BY t.Age

            WITH 
                countingpoint.CountingPoint_ID AS cp,
                collect({{Age: t.Age, Traffic: t.Traffic}}) AS TrafficRecords

            RETURN 
                cp as CountingPoint,
                [i IN range(0, size(TrafficRecords)-1) |
                    {{
                        start: CASE WHEN i = 0 THEN 0 ELSE TrafficRecords[i-1].Age END,
                        end: TrafficRecords[i].Age,
                        data: TrafficRecords[i].Traffic,
                        type: "Traffic"
                    }}
                ] AS intervals
            """

    result = traffic.send_query_parallel(query=query,data={"ids":countingpoints})

    #data = [
    #    {"CountingPoint_ID": row["CountingPoint"], "TrafficRecords": row["intervals"]}
    #    for row in result
    #]
    #return data
    return [
        {"CountingPoint_ID": row["CountingPoint"], "TrafficRecords": row["intervals"]}
        for row in result
    ]