from DBinteractions.GraphCreation import *
from concurrent.futures import ThreadPoolExecutor, as_completed


def chunk_list(data, chunk_size):
    for i in range(0, len(data), chunk_size):
        yield data[i:i + chunk_size]


def create_TempRel_parallel(databasename, data,
                            chunk_size=10000, max_workers=1):


    # Split input into chunks
    chunks = list(chunk_list(data, chunk_size))

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(create_TempRel, databasename, chunk)
            for chunk in chunks
        ]
    for f in as_completed(futures):
        f.result()



def create_TempRel(databasename, data):
    temp = GraphCreation(DataBaseName=databasename)


    query = f"""
            CALL apoc.periodic.iterate(
            \'
            UNWIND $data AS row
            RETURN row
            \',
            \'
            CREATE (t:TimeAxis)
            
            UNWIND row AS rec
            
            CREATE (s)
            SET s.data = rec.data
            
            CALL apoc.create.addLabels(s, [rec.type]) YIELD node
            
            CREATE (s)-[:start {{time: rec.start}}]->(t)
            CREATE (s)-[:end   {{time: rec.end}}]->(t)
            \',
            {{
              batchSize: 5000,
              parallel: false,
              params: {{data: $data }}
            }}
            )
            """

    temp.send_query_parallel(query=query, data={"data": data})




def get_Temp_Rel(databasename):
    temp = GraphCreation(DataBaseName=databasename)

    query = f"""
            MATCH (c:ConditionGrade)-[start_condition:start]->(t:TimeAxis),
                  (c)-[end_condition:end]->(t),
                  (tr:Traffic)-[start_traffic:start]->(t),
                  (tr)-[end_traffic:end]->(t)
            WHERE
                elementId(c)>elementId(tr)
            AND
                start_condition.time < start_traffic.time
            AND
                end_condition.time > end_traffic.time

            RETURN
                tr.data as traffic,
                c.data as condition
            """

    result = temp.send_query_parallel(query=query)

    data = [
        {"Traffic": row["traffic"], "Condition": row["condition"]}
        for row in result
    ]
    return data
