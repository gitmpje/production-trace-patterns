import json
import os

from rdflib import Dataset, URIRef, Variable
from rdflib.plugins.stores.sparqlstore import SPARQLStore
from string import Template
from time import time

# Files
DIR_SPARQL = "../../sparql-templates"

# RDF Store
AUTH = ("admin", "admin")
HOST = "localhost:3030"
REPO = "automotive"

BASE_URI = URIRef("http://example.org/id/automotive/")

headers = {"Content-Type": "application/sparql-update"}

store = SPARQLStore(
    query_endpoint=f"http://{HOST}/{REPO}/sparql",
    auth=AUTH,
)


if __name__ == "__main__":
    dataset = Dataset(store=store, default_union=True)

    # Define the use cases by refering to the pattern query and defining parameters
    with open("pattern_use_cases.json") as f:
        pattern_use_cases = json.load(f)

    # Execute the pattern queries for the provided use cases
    for k, d in pattern_use_cases.items():
        query_file = d["sparql-template"]
        with open(os.path.join(DIR_SPARQL, query_file)) as f:
            query_template = Template(f.read())

        query = query_template.substitute(
            {k: URIRef(v).n3() for k, v in d["sparql-binding"].items()}
        )
        variable = Variable(d["entity"]["variable"])
        value = BASE_URI + URIRef(d["entity"]["identifier"])
        values_clause = f"VALUES {variable.n3()} {{ {value.n3()} }}"

        start = time()
        r = dataset.query(query.replace("#%VALUES%#", values_clause))
        print(f"Use case {k}: {time() - start} s")

        # Serialize results as CSV
        if r.type == "CONSTRUCT":
            r.graph.query("select distinct ?s ?o { ?s ?p ?o }").serialize(
                f"results/{k}-pattern.csv",
                format="csv",
            )
        else:
            r.serialize(
                f"results/{k}-pattern.csv",
                format="csv",
            )
