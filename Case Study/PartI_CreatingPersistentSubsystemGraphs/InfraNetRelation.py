
def extract_data_from_asbnet(obj):
    query = f"""
                MATCH (r:ReferenceElement)
                RETURN 
                r.ReferenceElement_ID AS Ref_ID
                """

    results = obj.send_query(query=query)
    records = [dict(record) for record in results]

    refE = []
    for record in records:
        refE.append({
            "ReferenceElement_ID": record["Ref_ID"],
        })


    return refE

def create_refE(obj,data):
    query = f"""
            UNWIND $data AS item    
            CREATE (r:ReferenceElement{{ReferenceElement_ID: item.ReferenceElement_ID}})"""
    obj.send_query(query=query,data={"data":data})


def extract_data_from_sib(obj):
    query = f"""
            MATCH (b:Asset)--(n:NETZ_ZUO)--(s:SACHVER)
            RETURN 
            b.Asset_ID AS asset, 
            n.NACH_NK AS EndN, 
            n.VON_NK AS StartN,
            n.STAT_ANF AS StartS,
            n.STAT_MITT AS MidS,
            n.STAT_END AS EndS,
            s.LAGE AS Pos
            """

    results = obj.send_query(query=query)
    records = [dict(record) for record in results]

    assets = []
    for record in records:
        if len(record["StartN"])==7:
            start=record["StartN"]+"O"
        else: start=record["StartN"]
        if len(record["EndN"])==7:
            end=record["EndN"]+"O"
        else: end=record["EndN"]
        print(start+end)

        assets.append({
            "Asset_ID": record["asset"],
            "Localisation": {
                "StartN": start,
                "EndN": end,
                "RefE":start+end,
                "StartS": record["StartS"],
                "MidS": record["MidS"],
                "EndS": record["EndS"],
            },
            "Positioning": {
                "hor": record["Pos"]
            }
        })
    #print(assets)


    return assets

def create_Assets(obj,data):

    print(len(data))

    query = """
            CALL apoc.periodic.iterate(
            "UNWIND $data AS item RETURN item",
            "MERGE (r:RoadinfrastructureElement {RoadinfrastructureElement_ID: item.Asset_ID})",
            {params: {data: $data}, batchSize: 1000, parallel: false}
            )
            """

    obj.send_query(query=query, data={"data": data})

    print("Asset nodes created")

    query = """
            CALL apoc.periodic.iterate(
              "UNWIND $data AS item RETURN item",
              "
              MATCH (r:RoadinfrastructureElement {RoadinfrastructureElement_ID: item.Asset_ID})
              WITH r, item
              MATCH (rE:ReferenceElement {ReferenceElement_ID: item.Localisation.RefE})
              CREATE (r)-[:located_with]->(l:Localisation)
              CREATE (l)-[:StartPoint {Station: item.Localisation.StartS}]->(rE)
              CREATE (l)-[:MidPoint {Station: item.Localisation.MidS}]->(rE)
              CREATE (l)-[:EndPoint {Station: item.Localisation.EndS}]->(rE)
              CREATE (l)-[:positioned_with]->(p:Positioning {Lage: item.Positioning.hor})
              ",
              {params: {data: $data}, batchSize: 100, parallel: false}
            )
            """
    for i in range(0, len(data), 10000):
        data = data[i:i + 10000]
        obj.send_query(query=query, data={"data": data})
    print("Net Relations for Assets created")

    query = """
            CALL apoc.periodic.iterate(
              "MATCH p=()-[r:StartPoint{Station:$test}]-() RETURN r"," DELETE r",
              { batchSize: 1000, parallel: false,params: {test: 'null'}}
            )
            """
    obj.send_query(query=query)

    query = """
            CALL apoc.periodic.iterate(
              "MATCH p=()-[r:EndPoint{Station:$test}]-() RETURN r"," DELETE r",
              {batchSize: 1000, parallel: false,params: {test: 'null'}}
            )
            """
    obj.send_query(query=query)

    query = """
            CALL apoc.periodic.iterate(
              "MATCH p=()-[r:MidPoint{Station:$test}]-() RETURN r"," DELETE r",
              {batchSize: 1000, parallel: false,params: {test: 'null'}}
            )
            """
    obj.send_query(query=query)
    print("Cleaning done")

def restructuring_Assets(obj):
    # creating positioning nodes out of Lage attribute
    mapping_h = [
        {"Lage": "Oben liegend", "label": "HorizontalPositioningOn"},
        {"Lage": "Oben entlang liegend", "label": "HorizontalPositioningOn"},
        {"Lage": "Unten liegend", "label": "HorizontalPositioningAbove"},
        {"Lage": "Unten entlang liegend", "label": "HorizontalPositioningAbove"}
    ]
    mapping_v = [
        {"Lage": "Oben liegend", "label": "VerticalPositioningOn"},
        {"Lage": "Oben entlang liegend", "label": "VerticalPositioningNextTo"},
        {"Lage": "Unten liegend", "label": "VerticalPositioningOn"},
        {"Lage": "Unten entlang liegend", "label": "VerticalPositioningNextTo"}
    ]

    query = """WITH $mapping AS mappings
                   UNWIND mappings AS mapEntry
                   MATCH (n:Positioning {Lage : mapEntry.Lage})
                   CALL apoc.create.addLabels(n, [mapEntry.label]) YIELD node
        RETURN count(node) AS updatedCount
            """

    obj.send_query(query=query, data={"mapping": mapping_h})
    obj.send_query(query=query, data={"mapping": mapping_v})
def extract_data_from_trafficdata(obj):
    query = f"""
            MATCH (c:CountingPoint)
            RETURN 
            c.CountingPoint_ID AS CP, c.Station AS Station, c.RefE as ReferenceElement
            """

    results = obj.send_query(query=query)
    records = [dict(record) for record in results]

    CPs = []

    for record in records:
        CPs.append({
            "CP_ID": record["CP"],
            "Localisation": {
                "RefE": record["ReferenceElement"],
                "MidS": record["Station"],
            }
        })
    print(CPs)
    return CPs

def create_CountingPoints(obj,data):

    print(len(data))

    query = """
            CALL apoc.periodic.iterate(
            "UNWIND $data AS item RETURN item",
            "MERGE (r:CountingPoint {CountingPoint_ID: item.CP_ID})",
            {params: {data: $data}, batchSize: 1000, parallel: false}
            )
            """

    obj.send_query(query=query, data={"data": data})

    print("Counting Point nodes created")

    query = """
            CALL apoc.periodic.iterate(
              "UNWIND $data AS item RETURN item",
              "
              MATCH (r:CountingPoint {CountingPoint_ID: item.CP_ID})
              WITH r, item
              MATCH (rE:ReferenceElement {ReferenceElement_ID: item.Localisation.RefE})
              CREATE (r)-[:located_with]->(l:Localisation)
              CREATE (l)-[:MidPoint {Station: item.Localisation.MidS}]->(rE)
              CREATE (l)-[:positioned_with]->(p:Positioning:HorizontalPositioningOn:VerticalPositioningOn)
              ",
              {params: {data: $data}, batchSize: 100, parallel: false}
            )
            """
    obj.send_query(query=query, data={"data": data})

    print("Net Relations for Counting Points created")

