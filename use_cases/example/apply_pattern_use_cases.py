import os

from rdflib import Graph, Namespace
from string import Template
from time import time

DIR_SPARQL = "../../sparql-templates"

PTP = Namespace("http://example.org/def/production-trace-patterns/")

if __name__ == "__main__":
    # Load data into one graph
    g = Graph()
    g.parse("data/isa-95_1.ttl")
    g.parse("data/isa-95_2.ttl")
    g.parse("data/isa-95_3.ttl")

    # Define the use cases by refering to the pattern query and defining parameters
    pattern_use_cases = [
        (
            "elapsed-time_maximum.rq",
            {"IntervalStartType": PTP.TrackIn, "IntervalEndType": PTP.TrackOut},
        ),
        (
            "elapsed-time_preceding.rq",
            {"EventType": PTP.TrackIn, "PrecedingEventType": PTP.Repair},
        ),
        ("elapsed-time_succeeding-same.rq", {"EventType": PTP.SwitchState}),
        (
            "entity-entity_partOf.rq",
            {
                "IntervalStartType": PTP.TrackIn,
                "IntervalEndType": PTP.TrackOut,
                "PartEntityType": PTP.Product,
            },
        ),
        (
            "event-entity_all-preceding.rq",
            {"EventType": PTP.Split, "RelatedEntityType": PTP.ProductionLot},
        ),
        (
            "event-entity_all-succeeding.rq",
            {"EventType": PTP.Combine, "RelatedEntityType": PTP.ProductionLot},
        ),
        ("event-entity_partOf.rq", {}),
        (
            "event-entity_preceding.rq",
            {"EventType": PTP.TrackIn, "PrecedingEventType": PTP.SwitchTool},
        ),
        (
            "interval_aggregate-attribute.rq",
            {
                "IntervalStartType": PTP.TrackIn,
                "IntervalEndType": PTP.TrackOut,
                "attribute": PTP.rejectedQuantity,
            },
        ),
        (
            "interval_count-event.rq",
            {
                "IntervalStartType": PTP.TrackIn,
                "IntervalEndType": PTP.TrackOut,
                "EventType": PTP.Alarm,
            },
        ),
    ]

    # Execute the pattern queries for the provided use cases
    for query_file, bindings in pattern_use_cases:
        with open(os.path.join(DIR_SPARQL, query_file)) as f:
            query_template = Template(f.read())
        query = query = query_template.substitute(bindings)

        start = time()
        r = g.query(query, initBindings=bindings)

        # If the result is a graph, store results as Turtle, otherwise store as CSV
        if r.type == "CONSTRUCT":
            r.serialize(
                f"results/{query_file.replace('.rq', '')}_{hash(str(bindings))}.ttl",
                format="turtle",
            )
        else:
            r.serialize(
                f"results/{query_file.replace('.rq', '')}_{hash(str(bindings))}.csv",
                format="csv",
            )

        print(f"{query_file:<32}: {time() - start} s")
