import pandas as pd



def getEventWithinInterval(obj,typeEvent,typeInterval):
    query = f"""
            MATCH (n:Time)
            MATCH (n)--(i:{typeInterval})
            WITH n, i
            ORDER BY i.Time
            WITH n, collect(i) AS {typeInterval}

            MATCH (n)--(t:{typeEvent})
            WITH {typeInterval}, t
            ORDER BY t.Time
            WITH {typeInterval}, collect(t) AS {typeEvent}

            // Iterate over each {typeInterval}
            UNWIND range(0, size({typeInterval})-1) AS idx
            WITH 
              CASE WHEN idx = 0 THEN NULL ELSE {typeInterval}[idx-1] END AS lower,
              {typeInterval}[idx] AS upper,
              {typeEvent}

            WITH lower, upper,
                 CASE 
                   // Interval case: both lower and upper exist
                   WHEN lower IS NOT NULL THEN [t IN {typeEvent} WHERE t.Time >= lower.Time AND t.Time < upper.Time]
                   // Only upper bound exists: pick closest {typeEvent} before the upper bound
                   ELSE [t IN {typeEvent} WHERE t.Time <= upper.Time]
                 END AS candidates

            // Pick the closest candidate if only upper bound exists
            WITH lower, upper, candidates,
                 CASE
                   WHEN lower IS NULL THEN
                     reduce(closest = head(candidates), t IN candidates | 
                       CASE WHEN t.Time > closest.Time THEN t ELSE closest END)
                   ELSE candidates
                 END AS matched_{typeEvent}

            UNWIND matched_{typeEvent} AS t
            RETURN DISTINCT
              {{Time: lower.Time, Data: lower.Data}} AS LowerBoundaryEvent, 
              {{Time: upper.Time, Data: upper.Data}} AS UpperBoundaryEvent, 
              {{Time: t.Time, Data: t.Data}} AS IntervalMatchingEvent
            """
    print(query)
    results = obj.send_query(query=query)
    records = [dict(record) for record in results]
    return_data = []
    for record in records:
        return_data.append({
            "Event":record["IntervalMatchingEvent"],
            "Interval":
                {
                "Start": record["LowerBoundaryEvent"],
                "End": record["UpperBoundaryEvent"]
                }
        })

    return records,return_data

def getCountedEventWithinIntervalPlusAdditionalData(obj,typeEvent,typeInterval,additionalData):
    query = f"""
                MATCH (n:Time)
                MATCH (n)--(i:{typeInterval})
                WITH n, i
                ORDER BY i.Time
                WITH n, collect(i) AS {typeInterval}

                MATCH (n)--(t:{typeEvent})
                WITH n,{typeInterval}, t
                ORDER BY t.Time
                WITH n,{typeInterval}, collect(t) AS {typeEvent}
                
                //additional Data
                OPTIONAL MATCH (n)--({additionalData}:{additionalData})

                // Iterate over each {typeInterval}
                UNWIND range(0, size({typeInterval})-1) AS idx
                WITH 
                  CASE WHEN idx = 0 THEN NULL ELSE {typeInterval}[idx-1] END AS lower,
                  {typeInterval}[idx] AS upper,
                  {typeEvent},
                  {additionalData},{typeInterval}

                UNWIND range(0, size({typeInterval})-1) AS idx
                WITH 
                  CASE WHEN idx = 0 THEN NULL ELSE {typeInterval}[idx-1] END AS lower,
                  {typeInterval}[idx] AS upper,
                  {typeEvent},
                  {additionalData},{typeInterval}

                // Prepare {typeEvent} lists based on boundaries
                WITH lower, upper, {typeEvent}, {additionalData},
                     CASE 
                         WHEN lower IS NULL THEN [] 
                         ELSE [d IN {typeEvent} WHERE d.Time <= lower.Time | d.Time] 
                     END AS {typeEvent}BeforeLower,
                     [d IN {typeEvent} WHERE d.Time < upper.Time | d.Time] AS {typeEvent}BeforeUpper,{typeInterval}
                
                
                WITH Inspection,lower, upper, Damage, ConstructionYear,
                     DamageBeforeLower, DamageBeforeUpper,
                     upper AS currentInspection,
                     lower AS previousInspection,
                     // Compute earliest inspection
                     reduce(minT = null, i IN Inspection | 
                         CASE WHEN minT IS NULL OR i.Time < minT.Time THEN i ELSE minT END
                     ) AS earliestInspection
                WITH earliestInspection,lower, upper, DamageBeforeLower, DamageBeforeUpper,
                     CASE 
                        WHEN ConstructionYear IS NULL THEN {{Time: earliestInspection.Time, Data: earliestInspection.Data}}
                        WHEN earliestInspection.Time < ConstructionYear.Time 
                            THEN {{Time: earliestInspection.Time, Data: earliestInspection.Data}}
                        ELSE {{Time: ConstructionYear.Time, Data: ConstructionYear.Data}}
                     END AS AdditionalData

                RETURN DISTINCT
                  {{Time: lower.Time, Data: lower.Data}} AS LowerBoundaryEvent,
                  {{Time: upper.Time, Data: upper.Data}} AS UpperBoundaryEvent,
                  {typeEvent}BeforeLower AS EventsBeforeLower,
                  {typeEvent}BeforeUpper AS EventsBeforeUpper,
                  {{Time: AdditionalData.Time, Data: AdditionalData.Data}} AS AdditionalData
                """
    print(query)
    results = obj.send_query(query=query)
    records = [dict(record) for record in results]
    return_data = []
    for record in records:
        return_data.append({
            "EventsBeforeStart":record["EventsBeforeLower"],
            "EventsBeforeEnd": record["EventsBeforeUpper"],
            "Interval":
                {
                "Start": record["LowerBoundaryEvent"],
                "End": record["UpperBoundaryEvent"]
                },
            "AdditionalData": record["AdditionalData"]
        })

    return records,return_data

def getConditionGrades_TrafficData(obj):
    query = """
            MATCH (cp:TrafficData)-[cpEvt:EVENT]->(t:Time)<-[brEvt:EVENT]-(br:BridgeCondition)
            MATCH (r:BridgeRepair)-[rEvt:EVENT]->(t)<-[brEvt]-(br)
            WHERE cpEvt.Time < brEvt.Time and rEvt.Time < brEvt.Time
            WITH count(r) as r_num,br, brEvt.Time AS brTime, cp, cpEvt.Time AS cpTime
            ORDER BY br, brTime, cpTime DESC
            WITH r_num,br, brTime, head(collect({cp: cp, cpTime: cpTime})) AS closestCP
            WITH closestCP.cp AS Traffic,br AS Bridge,r_num
            RETURN toFloat(replace(Traffic.value,".","")) AS Traffic,Bridge.value AS BridgeCondition, r_num AS NumberRepairs
            """

    records = obj.send_query(query=query)
    df= pd.DataFrame([dict(record) for record in records])

    return df

def getConditionChanges_TrafficData(obj):
    query=  """
            MATCH (br1:BridgeCondition)-[brEvt1:EVENT]->(t:Time)
            MATCH (br0:BridgeCondition)-[brEvt0:EVENT]->(t)
            WHERE brEvt0.Time < brEvt1.Time
              AND NOT EXISTS {
                MATCH (brMid:BridgeCondition)-[brEvtMid:EVENT]->(t)
                WHERE brEvtMid.Time > brEvt0.Time
                  AND brEvtMid.Time < brEvt1.Time
              }
              AND br1.value - br0.value > 0
            WITH br1, br0, brEvt1.Time AS brTime1,t
            MATCH (cp:TrafficData)-[cpEvt:EVENT]->(t)
            WHERE cpEvt.Time < brTime1
            WITH br1, br0, brTime1, cp, cpEvt.Time AS cpTime
            ORDER BY br1, brTime1, cpTime DESC
            WITH br1, br0, head(collect({cp: cp, cpTime: cpTime})) AS closestCP
            WITH closestCP.cp AS Traffic, (br1.value - br0.value) AS BridgeCondition,br1,br0
            RETURN toFloat(replace(Traffic.value, ".", "")) AS Traffic, BridgeCondition
            """
    records = obj.send_query(query=query)
    df = pd.DataFrame([dict(record) for record in records])

    return df







