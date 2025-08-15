import glob
import json
import requests
import urllib.parse
import zipfile

# Files
CONTEXT_FILE = "context.json"
DATA_DIR = "data"
SPARQL_DIR = "sparql"

# RDF Store
AUTH = ("admin", "admin")
HOST = "localhost:3030"
REPO = "automotive"
EVENT_GRAPH_BASE = "http://example.org/graph/automotive/events/"

# Load JSON-LD context from file
with open(CONTEXT_FILE) as f:
    CONTEXT = json.load(f)["@context"]


### Load data ###
def load_files(file_list: list, graph_name: str):
    # List all files in the ZIP archive
    file_list = zip_ref.namelist()

    contents = []
    i = 0
    for file_name in file_list:
        with zip_ref.open(file_name) as f:
            content = json.load(f)

        # Add context to every object
        if isinstance(content, list):
            for o in content:
                o["@context"] = CONTEXT

        # Collect events in list
        if isinstance(content, list):
            contents.extend(content)
        else:
            contents.append(content)

        # Collect multiple events before uploading
        # Init files are loaded
        i += 1
        if len(contents) % 1000 == 0:
            # Serialize to JSON(-LD)
            jsonld_str = json.dumps(contents)

            response = requests.post(
                f"http://{HOST}/{REPO}?graph={urllib.parse.quote_plus(graph_name)}",
                data=jsonld_str.encode(),
                headers={"Content-Type": "application/ld+json"},
                auth=AUTH,
            )

            if response.status_code // 100 != 2:
                print(contents, response.status_code)
            else:
                print(
                    i,
                    graph_name,
                    file_name,
                    response.status_code,
                    json.loads(response.text).get("count"),
                )

            contents = []

    # Upload remaining events
    jsonld_str = json.dumps(contents)
    response = requests.post(
        f"http://{HOST}/{REPO}?graph={urllib.parse.quote_plus(graph_name)}",
        data=jsonld_str.encode(),
        headers={"Content-Type": "application/ld+json"},
        auth=AUTH,
    )


if __name__ == "__main__":
    # Load data from the ZIP files
    i = 0
    zip_files = [f for f in glob.glob(DATA_DIR + "\\*.zip")]
    for zip_path in zip_files:
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            object_type = zip_path.split("\\")[-1].split(".")[0]

            # Construct graph name from object type
            graph_name = EVENT_GRAPH_BASE + object_type

            load_files(zip_ref, graph_name)

    # Enrich data (SPARQL Update)
    insert_queries = [
        "insert_label.ru",
        "insert_type_entity.ru",
        "insert_type_event.ru",
        "insert_relation_entity.ru",
        "insert_relation_inverse.ru",
    ]

    for file_name in insert_queries:
        file_path = f"{SPARQL_DIR}/{file_name}"
        with open(file_path) as f:
            query = f.read()

        # POST request the UPDATE query
        response = requests.post(
            f"http://{HOST}/{REPO}",
            data=query.encode(),
            headers={"Content-Type": "application/sparql-update"},
            auth=AUTH,
        )

        print(file_path, response.status_code, response.text)
