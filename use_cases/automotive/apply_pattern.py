import os
import time

from rdflib import Dataset, Namespace
from rdflib.plugins.stores.sparqlstore import SPARQLUpdateStore

DIR_SPARQL = "../../sparql-templates"

AUTH = ("admin", "admin")
HOST = "localhost:8080"
REPO = "automotive"

PTP = Namespace("http://example.org/def/production-trace-patterns/")
PTP = Namespace("http://example.org/def/automotive/")

headers = {"Content-Type": "application/sparql-update"}

store = SPARQLUpdateStore(
    query_endpoint=f"http://{HOST}/{REPO}/sparql",
    update_endpoint=f"http://{HOST}/{REPO}/update",
)
store.http_auth = AUTH


if __name__ == "__main__":
    dataset = Dataset(default_union=True)

    # Define the use cases by refering to the pattern query and defining parameters
    pattern_use_cases = [
        # 1) Number of times a machine state switches during processing of an order.
        (
            "interval_count-event.rq",
            {
                "IntervalStartType": PTP.TrackIn,
                "IntervalEndType": PTP.TrackOut,
                "EventType": PTP.SwitchState,
            },
        ),
        # 2) List all states of a machine during processing of an order.
        (
            "interval_aggregate-attribute.rq",
            {
                "IntervalStartType": PTP.TrackIn,
                "IntervalEndType": PTP.TrackOut,
                "EventType": PTP.SwitchState,
                "attribute": EX.state,
            },
        ),
        # 3) Time between processing orders on a machine.
        (
            "elapsed-time_preceding.rq",
            {
                "EventType": PTP.TrackIn,
                "PrecedingEventType": PTP.TrackOut,
            },
        ),
        # 4.1) Time a machine is in a state.
        (
            "elapsed-time_succeeding-same.rq",
            {
                "EventType": PTP.SwitchState,
                "attribute": EX.state,
                "ResourceType": PTP.Machine,
            },
        ),
        # 4.2) Time between observing products at a Work Station.
        (
            "elapsed-time_succeeding-same.rq",
            {
                "EventType": PTP.Observation,
                "attribute": EX.mainEntity,
                "ResourceType": PTP.WorkStation,
            },
        ),
        # 5) Throughput time per product.
        (
            "elapsed-time_maximum.rq",
            {
                "IntervalStartType": PTP.TrackIn,
                "IntervalEndType": PTP.TrackOut,
                "EntityType": PTP.Product,
            },
        ),
        # 6) Relate AGV TrackIn event to the product that the AGV was transporting.
        (
            "event-entity_preceding.rq",
            {
                "EventType": PTP.TrackIn,
                "PrecedingEventType": PTP.TrackOut,
                "ResourceType": PTP.AGV,
                "EntityType": PTP.ProductionEntity,
            },
        ),
        # 7) Relate machine level track in events to the work station.
        (
            "event-entity_partOf.rq",
            {
                "EventType": PTP.TrackIn,
                "EntityType": PTP.WorkStation,
            },
        ),
        # 8) Relate events related to the modules (components) to the product that is composed of those modules.
        (
            "event-entity_all-preceding.rq",
            {
                "EventType": PTP.Aggregate,
                "RelatedEntityType": PTP.Product,
            },
        ),
    ]

    # Execute the pattern queries for the provided use cases
    for query_file, bindings in pattern_use_cases:
        with open(os.path.join(DIR_SPARQL, query_file)) as f:
            query = f.read()

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

