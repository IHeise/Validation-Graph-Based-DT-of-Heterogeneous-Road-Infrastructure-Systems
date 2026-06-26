from DBinteractions.GraphCreation import *

def get_TempRel(ConditionCountingPairs,databasename):
    #print("5 reached")

    temprel = DBinteraction(database=f"sos-temp-{databasename}")

    # emptying database
    query = """MATCH (n)
        CALL (n){
        DETACH DELETE n
    } IN TRANSACTIONS OF 10000 ROWS """
    #temprel.send_query_(query=query)

    #creating data

    query = """UNWIND $data AS sg

                CALL (sg) {
                    CREATE (t:TimeAxis {id: randomUUID()})
                
                    UNWIND sg.data AS row
                
                    WITH t, row,
                         [k IN keys(row) WHERE k <> 'Year'][0] AS metric
                
                    CREATE (d:DataPoint {
                        year: row.Year,
                        value: row[metric],
                        metric: metric
                    })
                    
                    CREATE (d)-[:end{year:d.year}]->(t)
                }
                IN CONCURRENT TRANSACTIONS OF 500 ROWS
                """
    for i in range(0, len(ConditionCountingPairs), 10000):
        chunk = ConditionCountingPairs[i:i + 10000]

        temprel.send_create_query_(query=query, data = {"data": chunk})

    #print("created")

    # labels
    query = """
                MATCH (d:DataPoint)
                
            CALL (d) {
                SET d:$(d.metric)}
            IN CONCURRENT TRANSACTIONS OF 500 ROWS"""


    temprel.send_create_query_(query=query)

    print("labeled")

    # interval boundaries

    query = """ MATCH (t:TimeAxis)

                CALL (t) {
                MATCH (t)<-[h:end]-(n)
                
                WHERE any(l IN labels(n) WHERE l IN ['ConditionGrade', 'Traffic'])
                WITH t,n,
                    CASE
                    WHEN 'ConditionGrade' IN labels(n) THEN 'ConditionGrade'
                        WHEN 'Traffic' IN labels(n) THEN 'Traffic'
                    END AS type

                WITH t, type, n
                ORDER BY t, type, n.year ASC

                WITH t, type, collect(n) AS nodes

                WITH t,nodes UNWIND range(0,size(nodes)-2) AS i
                WITH t,nodes[i] AS startNode,nodes[i+1] AS endNode
                CREATE (endNode)-[:start {year: startNode.year}]->(t)
                }
                IN CONCURRENT TRANSACTIONS OF 800 ROWS"""
    temprel.send_create_query_(query=query)

    #print("interval boundaries set")

    # extraction/association

    query = """
            MATCH (c_current:ConditionGrade)-[start_con:start]->(time:TimeAxis)
            MATCH (time)<-[end_traf:end]-(traffic:Traffic)

            WHERE end_traf.year <= c_current.year
              AND end_traf.year > start_con.year
            
            WITH DISTINCT
                time,
                c_current,
                start_con,
                collect(traffic.value) AS Traffic



                WITH DISTINCT
                    time,
                    c_current,
                    Traffic
                RETURN 
                    Traffic,
                    {
                        ConditionGrade: c_current.value,
                        InspectionDate: c_current.year
                    } AS Current
                            """
    results = temprel.send_query_(query=query)


    records = [dict(record) for record in results]
    return records

