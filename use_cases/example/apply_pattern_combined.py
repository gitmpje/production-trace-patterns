import os

from rdflib import Graph, Namespace
from time import time

DIR_SPARQL = "../../sparql-templates"

PTP = Namespace("http://example.org/def/production-trace-patterns/")

if __name__ == "__main__":
    # Load data into one graph
    g = Graph()
    g.parse("data/isa-95_1.ttl")
    g.parse("data/isa-95_2.ttl")
    g.parse("data/isa-95_3.ttl")

    # Define the patterns that have to be executed in order and corresponding parameters
    # In this example first additional relations are derived using the ptp:isPartOf relation, followed by an aggregation
    patterns_combined = [
        ("event-entity_partOf.rq", {}),
        (
            "interval_aggregate-attribute.rq",
            {
                "IntervalStartType": PTP.TrackIn,
                "IntervalEndType": PTP.TrackOut,
                "attribute": PTP.measuredValue,
            },
        ),
    ]

    # Execute the pattern queries
    for query_file, bindings in patterns_combined:
        with open(os.path.join(DIR_SPARQL, query_file)) as f:
            query = f.read()

        start = time()
        r = g.query(query, initBindings=bindings)

        # If the result is a graph, add the data to the in-memory graph, otherwise store as CSV
        if r.type == "CONSTRUCT":
            g.parse(data=r.serialize(format="turtle"))
        else:
            r.serialize(
                f"results_combined/{query_file.replace('.rq', '')}_{hash(str(bindings))}.csv",
                format="csv",
            )

        print(f"{query_file:<32}: {time() - start} s")
