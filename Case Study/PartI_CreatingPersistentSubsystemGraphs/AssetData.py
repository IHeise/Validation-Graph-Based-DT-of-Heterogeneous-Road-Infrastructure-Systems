import pandas as pd
from sqlalchemy import create_engine



class SIB_BW_Extraction:
    def __init__(self):
        self.server = r"localhost"
        self.database = "SIB_BAUWERKE_19"

    def get_data(self, tablename, columns):
        connection_string = f"mssql+pyodbc://@{self.server}/{self.database}?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"

        engine = create_engine(connection_string)

        columns_str = ", ".join(columns) if columns else "*"
        query = f"SELECT {columns_str} FROM {tablename};"
        df = pd.read_sql_query(query, engine)
        df = df.fillna("null")

        return df

def translate_keys(df):
    csv_file_path = "sources/ASBINGKEYS.csv"
    mappings = pd.read_csv(csv_file_path, delimiter=';')
    # Create mapping dict from 'nr' to 'drk_text'
    mapping_dict = dict(zip(mappings["nr"], mappings["drk_text"]))

    for col in df.columns:
        if df[col].dtype in ['int64', 'float64', 'object']:
            # Map values in the column if found in mapping_dict, else keep original
            pd.set_option('future.no_silent_downcasting', True)
            df[col] = df[col].map(mapping_dict).fillna(df[col]).infer_objects(copy=False)

    return df

def deleting_empty_spaces(df):
    exclude_cols = ['ID_NR',"TBWNR","TEIL_BWNR","IDENT","REF_SACHV"]
    for col in df.select_dtypes(include='object').columns:
        if col not in exclude_cols:
            df[col] = df[col].apply(lambda x: x.strip() if isinstance(x, str) else x)
    return df

def create_asset_representation(obj):
    tablenames=["SIBBW_BW_Verzeichnis","SIBBW_BAUTEIL_GRUPPEN","BAU_ERHA","SIBBW_AKT_SHAD","AKT_SHAD","AKT_PRUF","FHRB_BEL","BRUECKE","SACHVER","TEIL_BW","NETZ_ZUO","PRUF_DGF","SIBBW_AKT_SHAD","SCHADALT","GIS"]
    for tabelname in tablenames:
        print(f"    get data of {tabelname}")
        df=SIB_BW_Extraction().get_data(tablename=tabelname, columns=[])
        print(f"    translate keys for {tabelname}")
        df_translated = translate_keys(df)
        print(f"    delete empty spaces for {tabelname}")
        df_cleaned = deleting_empty_spaces(df_translated)

        # using chunks
        chunk_size = 10000
        total_rows = len(df_cleaned)

        for start in range(0, total_rows, chunk_size):
            end = start + chunk_size
            chunk_df = df_cleaned.iloc[start:end].fillna('').infer_objects(copy=False)

            chunk_list = chunk_df.to_dict('records')
            print(f"    creating node representation of {tabelname} {start} to {end - 1} of {len(df)}")
            obj.create_nodes(label=tabelname, list_of_dicts=chunk_list)

    print("    ...initial asset data nodes created")

def restructure_building(obj):
    # central TBW node
    label = "Asset"
    ID_property = "Asset_ID"
    obj.createConstraint(label=label, property=ID_property)
    query = f"""
                MATCH (n:TEIL_BW)
                MERGE (a:{label} {{{ID_property}:n.ID_NR}})
                MERGE (a)-[t:IS]->(n)
                """
    obj.send_query(query=query)
    print("central TBW node created")

    # connection BW to TBW
    query = f"""
                MATCH (n:BRUECKE)
                MATCH (a:Asset{{Asset_ID:n.ID_NR}})
                MERGE (a)-[t:IS]->(n)
                """
    obj.send_query(query=query)
    print("BW->TBW created")

    # connection BW-info to TBW
    query = f"""
                    MATCH (n:SIBBW_BW_Verzeichnis)
                    MATCH (a:Asset{{Asset_ID:n.ID_NR}})
                    MERGE (a)-[t:IS]->(n)
                    """
    obj.send_query(query=query)
    print("BW->TBW created")

    # classify bridges
    csv_file_path = "sources/BridgeClassification.csv"
    df = pd.read_csv(csv_file_path, delimiter=';')
    mapping = dict(zip(df["BWART"], df["bridge"]))
    bridges = [val for val, flag in mapping.items() if flag.lower() == "y"]
    query = """
            UNWIND $bridges as bridge
            MATCH (t:TEIL_BW{BWART:bridge})--(a:Asset)
            SET a:bridge
            """
    obj.send_query(query=query,data={"bridges":bridges})


def restructure_asbref(obj):
    # NETZ_ZUO -> TBW
    query = f"""
                MATCH (n:NETZ_ZUO)
                MATCH (a:Asset{{Asset_ID:n.ID_NR}})
                MERGE (a)-[t:NETZ_ZUO]->(n)
                """
    obj.send_query(query=query)
    print("NETZ-ZUO-> TBW created")

    # SACHV -> TBW
    query = f"""
                MATCH (n:SACHVER)
                MATCH (a:Asset{{Asset_ID:n.ID_NR}})
                MERGE (a)-[t:SACHVER]->(n)
                """
    obj.send_query(query=query)
    print("SACHV-> TBW created")

    # SACHV -> NETZ_ZUO (REF_SACHV)
    query = f"""
                MATCH (n:SACHVER)
                MATCH (a:NETZ_ZUO{{REF_SACHV:n.REF_SACHV}})
                MERGE (a)-[t:CONNECTED_TO]->(n)
                """
    obj.send_query(query=query)
    print("SACHV-> NETZ-ZUO created")

    # GIS -> TBW
    query = f"""
                MATCH (n:GIS)
                MATCH (a:Asset{{Asset_ID:n.ID_NR}})
                MERGE (a)-[t:GIS]->(n)
                """
    obj.send_query(query=query)
    print("GIS-> TBW created")

def restructure_inspections(obj):
    #central inspection nodes per building
    print("starting...")
    query = f"""
                CALL apoc.periodic.iterate
                (
                \"
                MATCH (n:PRUF_DGF)
                RETURN DISTINCT n.IDENT as id
                \",
                \"
                MERGE (i:Inspection {{Inspection_ID:id}})
                \",
                {{batchSize: 10000, parallel: false}}
                )
            """
    obj.send_query(query=query)
    print("central Inspection nodes created")

    query = f"""
                CALL apoc.periodic.iterate(
                \"
                MATCH (n:PRUF_DGF)
                MATCH (a:Asset{{Asset_ID:n.ID_NR}}) 
                MATCH (i:Inspection {{Inspection_ID:n.IDENT}})
                RETURN DISTINCT a,i
                \",
                \"
                MERGE (a)-[t:INSPECTED]->(i)
                \",
                {{batchSize: 10000, parallel: false}}
                )
            """
    obj.send_query(query=query)
    print("Asset --> Inspection created")

    query = f"""
                CALL apoc.periodic.iterate(
                \"
                MATCH (n:PRUF_DGF)
                MATCH (i:Inspection {{Inspection_ID:n.IDENT}})
                RETURN DISTINCT n,i
                \",
                \"
                MERGE (n)-[:CONNECTED_TO]->(i)
                \",
                {{batchSize: 10000, parallel: false}}
                )
            """
    obj.send_query(query=query)
    print("PRUF_DGF --> Inspection created")

    print("PRUF_DGF integrated")

    # AKT_DGF-> TBW (ID_NR)
    query = f"""
                CALL apoc.periodic.iterate(
                \"
                MATCH (n:AKT_PRUF)
                MATCH (a:Asset{{Asset_ID:n.ID_NR}}) RETURN n,a 
                \",
                \"WITH n,a  MERGE (i:Inspection {{Inspection_ID:n.IDENT}})
                        MERGE (a)-[t:INSPECTED]->(i)
                        MERGE (n)-[:CONNECTED_TO]->(i)\",
                {{batchSize: 1000, parallel: false}}
                )"""

    obj.send_query(query=query)
    print("AKT_DGF integrated")

    # SIBBW_BAUTEIL_GRUPPEN-> TBW (ID_NR)
    query = f"""
                    CALL apoc.periodic.iterate(
                    \"
                    MATCH (n:SIBBW_BAUTEIL_GRUPPEN)
                    MATCH (a:Asset{{Asset_ID:n.ID_NR}}) RETURN n,a 
                    \",
                    \"WITH n,a  MERGE (i:Inspection {{Inspection_ID:n.IDENT}})
                            MERGE (a)-[t:INSPECTED]->(i)
                            MERGE (n)-[:CONNECTED_TO]->(i)\",
                    {{batchSize: 1000, parallel: false}}
                    )"""

    obj.send_query(query=query)
    print("SIBBW_BAUTEIL_GRUPPEN integrated")

def restructure_damages(obj):
    # central damage node
    # komponent group

    #constraint component group
    query=  """ CREATE CONSTRAINT componentgroup_unique
                IF NOT EXISTS
                FOR (c:ComponentGroup)
                REQUIRE (c.Asset_ID, c.ComponentGroup) IS UNIQUE
            """
    obj.send_query(query=query)

    #creating componentgroups:
    labels=["SCHADALT","AKT_SHAD","SIBBW_AKT_SHAD"]
    for label in labels:
        query=  f""" CALL apoc.periodic.iterate(
                    \"
                    MATCH (s:{label})
                    RETURN s
                    \",
                    \"
                    SET s:damage
                    \",
                    {{batchSize: 10000, parallel: true, retries: 3}})
                """
        obj.send_query(query=query)

    query=  f""" CALL apoc.periodic.iterate(
                \"
                MATCH (s:damage)
                RETURN DISTINCT s.ID_NR AS Asset_ID, s.BAUTLGRUP AS ComponentGroup
                \",
                \"
                MERGE (c:ComponentGroup {{Asset_ID: Asset_ID, ComponentGroup: ComponentGroup}})
                \",
                {{batchSize: 10000, parallel: true, retries: 3}})
            """
    obj.send_query(query=query)
    print("ComponentGroups created")

    #connecting damages to component groups
    query=  f""" CALL apoc.periodic.iterate(
                \"
                MATCH (c:ComponentGroup)
                MATCH (d:damage{{ID_NR:c.Asset_ID,BAUTLGRUP:c.ComponentGroup}})
                RETURN c,d
                \",
                \"
                MERGE (c)-[:HAS_DAMAGE]->(d)",
                {{batchSize: 10000, parallel: false}})

            """
    obj.send_query(query=query)
    print("Damages connected to Component Groups")

    #connect component groups to assets
    query = f""" CALL apoc.periodic.iterate(
                        \"
                        MATCH (c:ComponentGroup)
                        MATCH (a:Asset{{Asset_ID:c.Asset_ID}})
                        RETURN c,a
                        \",
                        \"
                        MERGE (a)-[:HAS_COMPONENTGROUP]->(c)",
                        {{batchSize: 10000, parallel: false}})
                    """
    obj.send_query(query=query)
    print("Component Groups connected to Assets")

    # creating centraldamage node:

    # constraint damage
    query = """ CREATE CONSTRAINT damage_unique
                    IF NOT EXISTS
                    FOR (d:Damage)
                    REQUIRE (d.Asset_ID, d.Damage_ID) IS UNIQUE
                """
    obj.send_query(query=query)

    query = f""" CALL apoc.periodic.iterate(
                    \"
                    MATCH (s:damage)
                    WHERE s.SCHAD_ID <> ''
                    RETURN DISTINCT s.ID_NR AS Asset_ID, s.SCHAD_ID AS Damage
                    \",
                    \"
                    MERGE (c:Damage {{Asset_ID: Asset_ID, Damage_ID: Damage}})
                    \",
                    {{batchSize: 10000, parallel: true, retries: 3}})
                """
    obj.send_query(query=query)
    print("Damage nodes created")

    # connecting damages to Damage nodes
    query = f""" CALL apoc.periodic.iterate(
                    \"
                    MATCH (c:Damage)
                    MATCH (d:damage{{ID_NR:c.Asset_ID,SCHAD_ID:c.Damage_ID}})
                    RETURN c,d
                    \",
                    \"
                    MERGE (c)-[:HAS_DAMAGE]->(d)",
                    {{batchSize: 10000, parallel: false}})
                """
    obj.send_query(query=query)
    print("Damages connected to central Damage nodes")

    # connecting damages to Damage nodes
    query = f""" CALL apoc.periodic.iterate(
                        \"
                        MATCH (c:Damage)--(:damage)--(cg:ComponentGroup)
                        RETURN c,cg
                        \",
                        \"
                        MERGE (cg)-[:HAS_DAMAGE]->(c)",
                        {{batchSize: 10000, parallel: false}})
                    """
    obj.send_query(query=query)
    print("Damages connected to Component Groups")

    # recreation of damage id
    query = """ CALL apoc.periodic.iterate( 
                \"
                MATCH (d1:damage{SCHAD_ID:''})--(cg:ComponentGroup)
                MATCH (D:Damage)--(d2:damage{SCHADEN:d1.SCHADEN})--(cg)
                WHERE d1<>d2 AND d1.PRUFJAHR <> d2.PRUFJAHR AND d1.QUER = d2.QUER AND d1.LAENGS = d2.LAENGS
                RETURN d1,D
                \",
                \"
                MERGE (D)-[:HAS_DAMAGE]->(d1)",
                {batchSize: 10000, parallel: false})
            """
    obj.send_query(query=query)
    print("Damages without ID assigned")

def restructure_maintenance(obj):

    query = f"""
            MATCH (n:BAU_ERHA)
            MATCH (a:Asset{{Asset_ID:n.ID_NR}})
            MERGE (a)-[t:maintained]->(n)
            """
    obj.send_query(query=query)
    print("BW->TBW created")


def restructure_asset_graph(obj):

    restructure_building(obj=obj)

    restructure_asbref(obj=obj)

    restructure_inspections(obj=obj)

    restructure_damages(obj=obj)

    restructure_maintenance(obj=obj)























