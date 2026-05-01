import pandas as pd

csv="../sources/Zeitreihe.csv"

def read_csv(csv_path):
    df = pd.read_csv(csv_path,encoding='latin1',sep=';',low_memory=False,decimal=',')
    return df


def create_central_CountingPointNode(obj):
    label = "CountingPoint"
    ID_property = "CountingPoint_ID"
    obj.createConstraint(label=label,property=ID_property)
    query=  f"""
            MATCH (n:TrafficData) WHERE n.Abschnitt_Ast <> ''
            MERGE (CP:{label} {{{ID_property}:n.DZ_Nr+"_"+n.Abschnitt_Ast+"_"+n.Station, RefE:n.Abschnitt_Ast,Station:n.Station}})
            MERGE (CP)-[t:time{{Year:n.Jahr}}]->(n)
            """
    obj.send_query(query=query)

    query = f"""
                MATCH (n:TrafficData) WHERE n.Abschnitt_Ast = ''
                MERGE (CP:{label} {{{ID_property}:n.DZ_Nr+"_"+n.Koor_WGS84_N+"_"+n.Koor_WGS84_E, Koor_WGS84_N:n.Koor_WGS84_N,Koor_WGS84_E:n.Koor_WGS84_E}})
                MERGE (CP)-[t:time{{Year:n.Jahr}}]->(n)
                """
    obj.send_query(query=query)

def create_traffic_graphrepresentation(csv,obj):

    df=read_csv(csv_path=csv)

    #using chunks
    chunk_size=10000
    total_rows = len(df)

    for start in range(0, total_rows, chunk_size):
        end = start + chunk_size
        chunk_df = df.iloc[start:end].fillna('')
        chunk_list = chunk_df.to_dict('records')
        print(f"    creating node representation of traffic dataset {start} to {end - 1} of {len(df)}")
        obj.create_nodes(label="TrafficData", list_of_dicts=chunk_list)
        #create_nodes(connection=connection, label="TrafficData", list_of_dicts=chunk_list)

    print( "    ...initial traffic nodes created")

def restructuring_traffic_graph(obj):
    print( "    restructuring traffic data graph")
    #create counting point node
    create_central_CountingPointNode(obj=obj)
    print( "    traffic data graph restructured")





