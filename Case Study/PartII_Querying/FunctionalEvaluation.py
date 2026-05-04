def getBridgeConditionData(obj):
    """"relativ großer einfluss: Einschränkung der Prüfungsart"""
    query = """
            MATCH (s:SIBBW_BW_Verzeichnis)--(b:bridge)--(:Inspection)--(i:PRUF_DGF)
            WHERE i.PRUF_DATUM <> 'null' AND s.BAUJAHR <> 'null' AND i.ZUSTANDSN <> 'null'
            AND i.ART = 'Hauptprüfung'
            AND (date(i.PRUF_DATUM).year - toInteger(s.BAUJAHR)) >= 0
            AND toFloat(i.ZUSTANDSN) >= 1.0
            RETURN DISTINCT
                toInteger(s.BAUJAHR) as ConstructionYear, 
                toFloat(i.ZUSTANDSN) as ConditionGrade, 
                date(i.PRUF_DATUM).year AS InspectionYear,
                (date(i.PRUF_DATUM).year - toInteger(s.BAUJAHR)) AS Age
            """
    results = obj.send_query(query=query)
    records = [dict(record) for record in results]
    return records

def getBridgeConditionDataConstructionType(obj,ConstructionType):
# Unterscheidung nach Bauwerkstypen: Hohlkastenbrücke 0,33 ; Plattenbrücke 0,3,Plattenbalkenbrücke, Trägerrostbrücke: 0,4
    query = f"""MATCH (s:SIBBW_BW_Verzeichnis {{Bauwerksart:'{ConstructionType}'//,
                                                //Konstruktion:"2F-SpBFt-PlBa",
                                                //Statisches_System_Laengs:"Mehrf. freiaufl. ohne Durchlaufwirkung, durchl. Ortbetonplatte",
                                                //Tragfaehigkeit:"DIN: 60/30"
                                                }})
                --(:bridge)--(:Inspection)--(i:PRUF_DGF)
                WHERE i.PRUF_DATUM <> "null" AND s.BAUJAHR <> "null" AND i.ZUSTANDSN <> "null"
                //AND i.ART = 'Hauptprüfung'
                WITH date(i.PRUF_DATUM).year as InspYear, toInteger(s.BAUJAHR) as ConsYear, toFloat(i.ZUSTANDSN) as ConditionGrade
                  WHERE 100 > (InspYear-ConsYear) > 0
                  AND 4 > ConditionGrade >= 1.0
                  AND InspYear < 2025
                  //AND ConsYear > 1930
                  RETURN DISTINCT
                      ConsYear as ConstructionYear, 
                      ConditionGrade as ConditionGrade, 
                      InspYear AS InspectionYear,
                      (InspYear-ConsYear) AS Age"""
    print(query)
    results = obj.send_query(query=query)
    records = [dict(record) for record in results]
    return records



def getBridgeConditionDataVariables(obj):
    """"relativ großer einfluss: Einschränkung der Prüfungsart"""
    query = """
            MATCH (s:SIBBW_BW_Verzeichnis)--(b:bridge)--(:Inspection)--(i:PRUF_DGF)
            WHERE i.PRUF_DATUM <> 'null' AND s.BAUJAHR <> 'null' AND i.ZUSTANDSN <> 'null'
            AND i.ART = 'Hauptprüfung'
            AND (date(i.PRUF_DATUM).year - toInteger(s.BAUJAHR)) >= 0
            AND toFloat(i.ZUSTANDSN) >= 1.0
            RETURN DISTINCT
                toInteger(s.BAUJAHR) as ConstructionYear, 
                toFloat(i.ZUSTANDSN) as ConditionGrade, 
                date(i.PRUF_DATUM).year AS InspectionYear,
                (date(i.PRUF_DATUM).year - toInteger(s.BAUJAHR)) AS Age,
                s.Bauwerksart AS BridgeType,
                s.Konstruktion AS ConstructionType,
                s.Statisches_System_Laengs AS StructuralSystem,
                s.Tragfaehigkeit AS DesignStandard
            """
    results = obj.send_query(query=query)
    records = [dict(record) for record in results]
    return records

# Unterscheidung nach Bauwerken mit Instandsetzungsmaßnahmen und ohne

# Verhalten vor der ersten Instandsetzung, Verhalten nach der ersten Instandsetzung

def getInspectionDamages(obj,ConstructionType):
    query = f""" MATCH (s:SIBBW_BW_Verzeichnis{{Bauwerksart:'{ConstructionType}'//,
                                                //Konstruktion:"2F-SpBFt-PlBa",
                                                //Statisches_System_Laengs:"Mehrf. freiaufl. ohne Durchlaufwirkung, durchl. Ortbetonplatte",
                                                //Tragfaehigkeit:"DIN: 60/30"
                                                }})--(b:bridge)--(:Inspection)--(i:PRUF_DGF)
                MATCH (b)--()--(D:damage)
                WHERE i.PRUF_DATUM <> "null" AND s.BAUJAHR <> "null" AND D.PRUFJAHR IS NOT null
                WITH collect (DISTINCT (date(i.PRUF_DATUM).year)) as InspYears, toInteger(s.BAUJAHR) as ConsYear,collect(DISTINCT({{year:D.PRUFJAHR, ID:D.SCHAD_ID, Damage:D.BSP_ID}})) as damages,s
                RETURN DISTINCT
                s.ID_NR as Asset_ID,
                toInteger(s.BAUJAHR) as ConstructionYear,
                InspYears,
                damages
                """
    print(query)
    results = obj.send_query(query=query)
    records = [dict(record) for record in results]
    data = []
    """for record in records:
        data.append({
            "ID":record["Asset_ID"],
            "ConstructionYear":
                {"Type":"ConstructionYear",
                 "ID":"xx",
                 "Time":record["ConstructionYear"],
                 "Data":"xx"
                 },
            "Inspections":
                {"Type":"Inspection",
                 "ID":"xx",
                 "Time":record["ConstructionYear"],
                 "Data":"xx"},
            record["InspYears"],
            "Damages":record["damages"]
        })"""
    return records,data

def getAssetsByID(obj,data,types=[]):
    """
    input data: ID, Asset: {Type,ID,Data,Time}
    type: list of other types
    output data: ID, Bridge: {Type,ID,Data,Time}}
    """
    type_string = " "
    for type in types:
        type_string += f"""data.{type} as {type},"""

    query = f"""
            UNWIND $data as data
            MATCH (s:SIBBW_BW_Verzeichnis{{ID_NR:data.Asset.ID}})--(b:bridge)
            RETURN 
                data.ID as ID,
                {type_string}
                {{Type:"Bridge",ID:data.Asset.ID,Time: "xx",Data:"xx"}} as Bridge
            """
    print(query)
    results = obj.send_query(query=query,data={"data": data})
    records = [dict(record) for record in results]

    return_data = []
    for record in records:
        result_type_dict = {t: record[t] for t in types}
        return_data.append({
            "ID": record["ID"],
            "Bridge": record["Bridge"],
            **result_type_dict
        })
    return records, return_data

def getAssetsByType(obj,ConstructionType):
    """
    input data: none
    output data: {ID, Bridge:{Type,ID,Data,Time}}
    """

    query = f"""
            MATCH (s:SIBBW_BW_Verzeichnis{{Bauwerksart:'{ConstructionType}'//,
                                                //Konstruktion:"2F-SpBFt-PlBa",
                                                //Statisches_System_Laengs:"Mehrf. freiaufl. ohne Durchlaufwirkung, durchl. Ortbetonplatte",
                                                //Tragfaehigkeit:"DIN: 60/30"
                                                }})
                WHERE s.BAUJAHR <> "null" and s.BAUJAHR IS NOT null
            RETURN DISTINCT
                s.ID_NR as ID,
                {{Type:"Bridge",ID: s.ID_NR,Time: "xx",Data:s.Bauwerksart}} as Bridge
                //{{Type:"ConstructionYear",ID:s.ID_NR,Time: tointeger(s.BAUJAHR),Data:"xx"}} as ConstructionYear
                """
    print(query)
    results = obj.send_query(query=query)
    records = [dict(record) for record in results]
    return_data = []
    for record in records:
        return_data.append({
            "ID":record["ID"],
            "Bridge": record["Bridge"]
        })
    return records, return_data

def getInspectionsPerAsset(obj,data,types=[]):
    """
    input data: {ID, Bridge:{Type,ID,Data,Time}}
    type: list of other types
    output data: {ID, Bridge:{Type,ID,Data,Time}, Inspection:{Type,ID,Data,Time},ConstructionYear:{Type,ID,Data,Time}}
    """
    type_string = " "
    for type in types:
        type_string += f"""data.{type} as {type},"""

    query = f"""
            UNWIND $data as data
            MATCH (s:SIBBW_BW_Verzeichnis{{ID_NR:data.Bridge.ID}})--(b:bridge)--(:Inspection)--(i:PRUF_DGF) 
                WHERE i.PRUF_DATUM <> "null" AND i.PRUF_DATUM IS NOT null AND i.ZUSTANDSN <> 0.0 AND i.ZUSTANDSN <> "null" AND i.ZUSTANDSN IS NOT null
            RETURN DISTINCT
                data.ID as ID,
                data.Bridge as Bridge,
                {type_string}
                collect (DISTINCT ({{Type:"Inspection",ID:i.IDENT,Time: date(i.PRUF_DATUM).year,Data:i.ZUSTANDSN}})) as Inspection,
                {{Type:"ConstructionYear",ID:s.IDENT,Time: tointeger(s.BAUJAHR),Data:"xx"}} as ConstructionYear
            """
    print(query)
    results = obj.send_query(query=query,data={"data": data})
    records = [dict(record) for record in results]
    data = []
    for record in records:

        result_type_dict = {t: record[t] for t in types}

        data.append({
            "ID": record["ID"],
            "Bridge": record["Bridge"],
            "ConstructionYear": record["ConstructionYear"],
            **result_type_dict,
            "Inspection": record["Inspection"]
        })
    return records, data

def getDamagesPerAsset(obj,data,types=[]):
    """
    input data: {ID, Bridge:{Type,ID,Data,Time}}
    type: list of other types
    output data: {ID, Bridge:{Type,ID,Data,Time}, Damage:{Type,ID,Data,Time}}
    """
    type_string = " "
    for type in types:
        type_string += f"""data.{type} as {type},"""

    query = f"""
            UNWIND $data as data
            MATCH (s:SIBBW_BW_Verzeichnis{{ID_NR:data.Bridge.ID}})--(:bridge)--(c:ComponentGroup)--(D:damage)
                WHERE D.PRUFJAHR IS NOT null
            RETURN DISTINCT
                data.ID as ID,
                data.Bridge as Bridge,
                {type_string}
                collect (DISTINCT ({{Type:"Damage",ID:D.SCHAD_ID,Time: D.PRUFJAHR,Data:D.BAUTLGRUP}})) as Damage   
            """
    print(query)
    results = obj.send_query(query=query, data={"data": data})
    records = [dict(record) for record in results]
    return_data = []
    for record in records:
        result_type_dict = {t: record[t] for t in types}
        return_data.append({
            "ID": record["ID"],
            "Bridge": record["Bridge"],
            **result_type_dict,
            "Damage": record["Damage"]
        })
    return records, return_data

def getTrafficDataByCountingPoint(obj,data,types=[]):
    """
    input data: {ID, CountingPoint}
    output data {ID, CountingPoint, Traffic}

    """
    type_string = " "
    for type in types:
        type_string += f"""data.{type} as {type},"""

    #"DTV_Kfz_W_Ri1"
    property="DTV_Kfz_MobisSo_Q"
    query = f"""
                UNWIND $data AS data 
                MATCH (CP:CountingPoint {{CountingPoint_ID: data.CountingPoint.ID}})--(TD)
                WHERE TD.{property} <> "" AND TD.{property} <> 'null'
                RETURN DISTINCT
                    data.ID AS ID,
                    {type_string}
                    data.CountingPoint AS CountingPoint,
                    collect(DISTINCT({{Type:"Traffic",ID:"xx",Time:TD.Jahr,Data:tointeger(TD.{property}) }} )) as Traffic    
                """
    print(query)
    results = obj.send_query(query=query, data={"data": data})
    records = [dict(record) for record in results]

    pairs = []
    for record in records:
        result_type_dict = {t: record[t] for t in types}
        pairs.append({
            "ID": record["ID"],
            **result_type_dict,
            "CountingPoint": record["CountingPoint"],
            "Traffic": record["Traffic"]
        })


    return records,pairs

