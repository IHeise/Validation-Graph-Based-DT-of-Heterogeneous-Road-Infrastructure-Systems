
def getAssetsCountingPoints(obj):
    query = """
            MATCH (CP:CountingPoint)--(l1)--(r:ReferenceElement)--(l2)--(B:RoadinfrastructureElement)
            WHERE (l1)--(:HorizontalPositioningOn:VerticalPositioningOn)
            AND (l2)--(:HorizontalPositioningOn:VerticalPositioningOn)
            RETURN DISTINCT
            r.ReferenceElement_ID AS Ref_ID,
            CP.CountingPoint_ID as CP_ID,
            B.RoadinfrastructureElement_ID AS B_ID
            ORDER BY CP.CountingPoint_ID
            """

    results = obj.send_query(query=query)
    records = [dict(record) for record in results]

    pairs = []
    i=0
    for record in records:
        pairs.append({
            "ID": str(i) + "_" + record["Ref_ID"],
            "CountingPoint":
                {
                    "Type": "CountingPoint",
                    "ID": record["CP_ID"],
                    "Data":"xx",
                    "Time":"xx"
                },
            "Asset":
                {
                    "Type": "Asset",
                    "ID": record["B_ID"],
                    "Data": "xx",
                    "Time": "xx"
                }
        })
        i=i+1
    return records, pairs



def getBuildingsData_ConditionGradeBridge(obj,AssetPairs):
    #gathering some bridge data
    query = """
            UNWIND $AssetPairs AS AssetPair
            MATCH (B:Asset:bridge {Asset_ID: AssetPair.B})--(:Inspection)--(I:PRUF_DGF)
            WHERE I.PRUF_DATUM <> 'null' AND I.ZUSTANDSN <> 0.0 AND I.ZUSTANDSN <> 'null'
            RETURN DISTINCT
                AssetPair.AssetPair_ID AS ID,
                AssetPair.ReferenceElement_ID AS Ref_ID,
                AssetPair.Asset1.CP_ID AS CP,
                AssetPair.Asset1.TrafficData AS TD,
                AssetPair.Asset1.Type AS Asset1_Type,
                AssetPair.B AS B_ID,
                collect({
                    CG: I.ZUSTANDSN,
                    Time: date(I.PRUF_DATUM).year
                }) AS CG_List
            """


    results = obj.send_query(query=query, data={"AssetPairs": AssetPairs})
    records = [dict(record) for record in results]

    pairs = []
    for record in records:
        pairs.append({
            "AssetPair_ID": record["ID"],
            "ReferenceElement_ID": record["Ref_ID"],
            "Asset1":   {
                "Type": record["Asset1_Type"],
                "ID": record["CP"],
                "Data": record["TD"]
                   },
            "Asset2":   {
                "Type": "BridgeCondition",
                "ID": record["B_ID"],
                "Data":record["CG_List"]
                    }
        })
    return pairs


