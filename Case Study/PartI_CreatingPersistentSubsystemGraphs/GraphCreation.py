from DB_interaction import *
from GraphCreation.AssetData import create_asset_representation, restructure_asset_graph
from GraphCreation.InfraNetRelation import extract_data_from_sib, extract_data_from_asbnet
from GraphCreation.TrafficData import  *
from GraphCreation.AsbNet import *
from GraphCreation.InfraNetRelation import *

#general

class GraphCreation:
    def __init__(self, DataBaseName):
        self.DataBaseName = DataBaseName
        self.DB = DBinteraction(database=self.DataBaseName)

    def cleanDataBase(self):
        query = f"CALL apoc.periodic.iterate(" \
                       f"\"MATCH (n) RETURN n\"," \
                       f"\"DETACH DELETE n\"," \
                       f"{{batchSize:1000, parallel:false}}" \
                       f") "
        self.DB.send_query(query)

    def dropConstraint(self,label,property):
        query=f"DROP CONSTRAINT {label}_{property} IF EXISTS"
        self.DB.send_query(query)

    def createConstraint(self,label,property):
        query=  f"""
                CREATE CONSTRAINT {label}_{property}
                IF NOT EXISTS 
                FOR (n:{label})
                REQUIRE (n.{property}) IS NODE KEY
                """
        self.DB.send_query(query)

    def clearQueryCache(self):
        self.DB.send_query("CALL db.clearQueryCaches()")

    def create_nodes(self, label, list_of_dicts):
        query = f"""
                UNWIND $rows as row
                CREATE (n:{label})
                SET n = row
                """
        self.DB.send_query(query=query, data={"rows": list_of_dicts})

    def send_query(self,query,data=None):
        results=self.DB.send_query(query=query, data=data)
        return results

# TrafficData
    def createTrafficGraph(self):
        print("..................")
        print("Creating traffic data graph:")

        source="sources/Zeitreihe.csv"

        create_traffic_graphrepresentation(csv=source,obj=self)
        restructuring_traffic_graph(obj=self)

        print("Traffic data graph ready to use")
        print("..................")

# Net
    def createNetGraph(self):
        print("..................")
        print("Creating reference elements data graph:")
        print(  "Creating asb net source data graph:")

        self.DataBaseName = "asbnet"
        self.DB = DBinteraction(database=self.DataBaseName)

        create_reference_elements(connection=self.DB,obj=self)
        print("Restructuring asb net source data graph:")
        restructuring_asbsource_graph(connection=self.DB,obj=self)

        print("reference elements data graph ready to use")
        print("..................")

# BridgeData
    def createAssetGraph(self):
        print("..................")
        print("Creating asset data graph:")
        print("Creating SIB BW source data graph:")

        self.DataBaseName = "sib"
        self.DB = DBinteraction(database=self.DataBaseName)

        create_asset_representation(obj=self)
        restructure_asset_graph(obj=self)

        print("SIB BW source data graph ready to use")
        print("..................")

# InfraNetRelation
    def createInfraNetRel(self):
        print("..................")
        print("Creating spatial relations data graph:")
        print("Creating SIB BW source data graph:")



        #add reference elements
        self.DataBaseName = "asbnet"
        self.DB = DBinteraction(database=self.DataBaseName)
        RefE=extract_data_from_asbnet(obj=self)

        self.DataBaseName = "infranetrel"
        self.DB = DBinteraction(database=self.DataBaseName)
        create_refE(obj=self,data=RefE)

        #add assets
        self.DataBaseName = "sib"
        self.DB = DBinteraction(database=self.DataBaseName)
        Assets=extract_data_from_sib(obj=self)

        self.DataBaseName = "infranetrel"
        self.DB = DBinteraction(database=self.DataBaseName)
        create_Assets(obj=self, data=Assets)
        restructuring_Assets(obj=self)


        #add traffic counting points
        self.DataBaseName = "trafficdata"
        self.DB = DBinteraction(database=self.DataBaseName)
        CountingPoints = extract_data_from_trafficdata(obj=self)

        self.DataBaseName = "infranetrel"
        self.DB = DBinteraction(database=self.DataBaseName)
        create_CountingPoints(obj=self, data=CountingPoints)

