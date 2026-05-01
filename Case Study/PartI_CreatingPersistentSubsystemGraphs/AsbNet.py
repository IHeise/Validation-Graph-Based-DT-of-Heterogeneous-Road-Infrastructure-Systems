import requests
import xml.etree.ElementTree as ET
import csv
import os


def request_available_featuretypes():
    WFS_URL = "https://inspire.bast.de/geoserver/bisstra.strasse/wfs?service=WFS&request=GetCapabilities"
    OUTPUT_FILE = "../sources/wfs_feature_types.csv"

    # get data
    response = requests.get(WFS_URL)
    response.raise_for_status()  # Raise error if the request failed

    # parse data
    root = ET.fromstring(response.content)

    # Namespace mapping for WFS 2.0
    namespaces = {
        'wfs': 'http://www.opengis.net/wfs/2.0',
        'ows': 'http://www.opengis.net/ows/1.1',
        'xlink': 'http://www.w3.org/1999/xlink'
    }

    # Extract all FeatureType elements in the WFS namespace
    feature_types = []
    for feature in root.findall('.//wfs:FeatureType', namespaces):
        name_el = feature.find('wfs:Name', namespaces)
        title_el = feature.find('wfs:Title', namespaces)
        abstract_el = feature.find('wfs:Abstract', namespaces)
        feature_types.append({
            'Name': name_el.text if name_el is not None else '',
            'Title': title_el.text if title_el is not None else '',
            'Abstract': abstract_el.text if abstract_el is not None else ''
        })

    # feature types to csv to enable outmated querying
    with open(OUTPUT_FILE, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=["Name", "Title","Abstract"])
        writer.writeheader()
        writer.writerows(feature_types)

def download_featuretype_content():
    # --- CONFIGURATION ---
    WFS_BASE_URL = "https://inspire.bast.de/geoserver/bisstra.strasse/wfs?service=WFS"
    OUTPUT_DIR = "../sources"
    INPUT_CSV = "../sources/wfs_feature_types.csv"
    WFS_VERSION = "2.0.0"
    OUTPUT_FORMAT = "application/gml+xml; version=3.2"


    # --- READ CSV ---
    with open(INPUT_CSV, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            feature_type = row["Name"]
            filename = feature_type.replace(":", "_") + ".gml"  # or ".json" if GeoJSON
            filepath = os.path.join(OUTPUT_DIR, filename)

            print(f"Downloading: {feature_type}...")

            # --- CONSTRUCT GETFEATURE REQUEST ---
            params = {
                "service": "WFS",
                "version": WFS_VERSION,
                "request": "GetFeature",
                "typeNames": feature_type,
                "outputFormat": OUTPUT_FORMAT
            }

            try:
                response = requests.get(WFS_BASE_URL, params=params, timeout=60)
                response.raise_for_status()

                with open(filepath, "wb") as f:
                    f.write(response.content)

                print(f"Saved to: {filepath}")

            except Exception as e:
                print(f"Failed to download {feature_type}: {e}")

def create_nodes_out_of_gml(connection, GML_FILE, LABEL,obj):

    NAMESPACE = {
        'gml': 'http://www.opengis.net/gml/3.2',
        'wfs': 'http://www.opengis.net/wfs/2.0',
        'bisstra': 'de.bund.bast.inspire.bisstra/'
    }

    # parsing
    def parse_gml(filepath):
        tree = ET.parse(filepath)
        root = tree.getroot()
        features = []

        for member in root.findall(".//wfs:member", NAMESPACE):
            feature_elem = list(member)[0]  # first child element is the actual feature
            node = {}
            node["id"] = feature_elem.attrib.get('{http://www.opengis.net/gml/3.2}id')

            for child in feature_elem:
                tag = child.tag.split('}')[-1]  # strip namespace
                if child.text and child.text.strip():
                    node[tag] = child.text.strip()
                # Geometry handling
                # --- Point ---
                pos = child.find(".//gml:pos", NAMESPACE)
                if pos is not None:
                    coords = pos.text.strip().split()
                    if len(coords) == 2:
                        node["geometry_type"] = "Point"
                        node["coordinates"] = [float(coords[0]), float(coords[1])]
                    continue

                # --- LineString ---
                pos_list = child.find(".//gml:posList", NAMESPACE)
                if pos_list is not None:
                    coords = list(map(float, pos_list.text.strip().split()))
                    if len(coords) % 2 == 0:
                        pairs = [(coords[i], coords[i + 1]) for i in range(0, len(coords), 2)]
                        wkt_line = "([" + "], [".join(f"{x}, {y}" for x, y in pairs) + "])"

                        #or as actual wkt:
                        #wkt_line = "LINESTRING(" + ", ".join(f"{x} {y}" for x, y in pairs) + ")"

                        node["geometry_type"] = "LineString"
                        node["coordinates"] = wkt_line
                    continue



            features.append(node)
        print(f"{len(features)} :{LABEL} Nodes need to be added")

        return features


    def insert_features_to_neo4j(features, label):
        cypher = f"""
        UNWIND $batch AS row
        MERGE (n:{label} {{id: row.id}})
        SET n += row
        """

        connection.send_query(cypher, data={"batch": features})
        print(f"    -->  Inserted {len(features)} nodes with label :{label}")

    features = parse_gml(GML_FILE)

    chunk_size = 5000
    total_elements = len(features)

    for start in range(0, total_elements, chunk_size):
        end = min(start + chunk_size, total_elements)
        chunk = features[start:end]

        insert_features_to_neo4j(chunk, LABEL)
        obj.clearQueryCache()


def create_reference_elements(connection,obj):

    obj.dropConstraint(label="NetNode", property="NetNode_ID")
    obj.dropConstraint(label="ZeroPoint", property="ZeroPoint_ID")

    create_nodes_out_of_gml(connection=connection,GML_FILE="sources/bisstra.strasse_tbl_BFStr_NK.gml",LABEL="NetNode",obj=obj)
    obj.clearQueryCache()
    create_nodes_out_of_gml(connection=connection, GML_FILE="sources/bisstra.strasse_tbl_BFStr_NP.gml",
                            LABEL="ZeroPoint",obj=obj)
    obj.clearQueryCache()
    create_nodes_out_of_gml(connection=connection, GML_FILE="sources/bisstra.strasse_tbl_BFStr_Sektor.gml",
                            LABEL="Section_Branch",obj=obj)
    obj.clearQueryCache()
    create_nodes_out_of_gml(connection=connection, GML_FILE="sources/bisstra.strasse_tbl_BFStr_Sektor_BA.gml",
                            LABEL="Stationing",obj=obj)
    obj.clearQueryCache()

def restructuring_asbsource_graph(connection,obj):
    #NetNodes
    label = "NetNode"
    ID_property = "NetNode_ID"

    query = f"""
                MATCH (n:NetNode)
                SET n.{ID_property}=n.NK_Kennung
                """
    connection.send_query(query=query)
    obj.createConstraint(label=label, property=ID_property)

    # ZeroPoints
    label = "ZeroPoint"
    ID_property = "ZeroPoint_ID"

    query = f"""
                    MATCH (NP:{label})
                    SET NP.{ID_property}=NP.NP_Kennung
                    WITH NP,substring(NP.NP_Kennung,0,7) as NN
                    MATCH (NK:NetNode{{NetNode_ID:NN}})
                    MERGE (NP)-[r:CONNECTED_TO]->(NK)
                    SET r.label = NP.ZeroPoint_ID
                    """

    connection.send_query(query=query)
    obj.createConstraint(label=label, property=ID_property)

    # Section_Branch
    label = "ReferenceElement"
    ID_property = "ReferenceElement_ID"
    obj.createConstraint(label=label, property=ID_property)
    # create central ReferenceElementNode
    query = f"""
                MATCH (n:Section_Branch)
                MERGE (R:{label} {{{ID_property}:n.Sk_Kennung}})
                MERGE (n)-[r:CONNECTED_TO]->(R)
                SET r.label = R.Sk_Achse
                """
    connection.send_query(query=query)
    # create relation between RefE and ZeroPoints
    query = f"""
                    MATCH (n:ReferenceElement)
                    WITH n,substring(n.ReferenceElement_ID,0,8) as FROM, substring(n.ReferenceElement_ID,8,16) as TO
                    MATCH (NN_from:ZeroPoint{{ZeroPoint_ID:FROM}}) 
                    MATCH (NN_to:ZeroPoint{{ZeroPoint_ID:TO}})
                    MERGE (NN_from)<-[:from]-(n)-[:to]->(NN_to)
                    """
    connection.send_query(query=query)






