# automotive
Automotive data set for demonstrating the patterns and their implementation in SPARQL.

## Content

* `data/` contains the data set (JSON).
* `pattern_use_cases.json` lists use cases for the patterns applicable to the data set.
* `docker-compose.yml` service definition for Jena Fuseki RDF Store.
* `load_data_rdf.py` script to enrich JSON data with JSON-LD context, upload data to RDF Store, and execute queries to align to data model.
* `apply_pattern.py` script to apply Production Trace Patterns implemented in SPARQL (on the data set loaded to the RDF Store).
* `without_pattern.py` script to derive insights without using the data model and Production Trace Patterns.

## Dependencies
* RDF Store, in this example [stain/jena-fuseki](https://hub.docker.com/r/stain/jena-fuseki) is used.

## Use cases for the patterns
1. Number of times a machine state switches during processing of an order.
    * `$IntervalStartType=ptp:TrackIn`
    * `$IntervalEndType=ptp:TrackOut`
    * `$EventType=ptp:SwitchState`
2. List all states of a machine during processing of an order.
    * `$IntervalStartType=ptp:TrackIn`
    * `$IntervalEndType=ptp:TrackOut`
    * `$EventType=ptp:SwitchState`
    * `$attribute=ex:state`
3. Time between processing orders on a machine.
    * `$EventType=ptp:TrackIn`
    * `$PrecedingEventType=ptp:TrackOut`
4. 
    1. Time a machine is in a state.
        * `$EventType=ptp:SwitchState`
        * `$attribute=ex:state`
        * `$ResourceType=ptp:Machine`
    2. Time between observing products at a Work Station.
        * `$EventType=ptp:Observation`
        * `$attribute=ex:mainEntity`
        * `$ResourceType=ptp:WorkStation`
5. Throughput time per product.
    * `$IntervalStartType=ptp:TrackIn`
    * `$IntervalEndType=ptp:TrackOut`
    * `$EntityType=ptp:Product`
6. Relate AGV event to the product/module that the AGV is transporting.
    * `$EventType=ptp:SwitchState`
    * `$PrecedingEventType=ptp:SwitchState`
    * `$ResourceType=ptp:AGV`
    * `$EntityType=ptp:ProductionEntity`
7. Relate machine level track in events to the work station.
    * `$EventType=ptp:TrackIn`
    * `$EntityType=ptp:WorkStation`
8. Relate events related to the modules (components) to the product that is composed of those modules.
    * `$EventType=ptp:Aggregate`
    * `$RelatedEntityType=ptp:Product`
9. -
10. Relate orders to the product they are part of.
    * `$IntervalStartType=ptp:TrackIn`
    * `$IntervalEndType=ptp:TrackOut`
    * `$PartEntityType=ptp:Order`

## How to use
Commands can be executed in the following sequence.
* `docker-compose up -d`
* `python load_data_rdf.py`
* `python apply_pattern.py`
* `python without_pattern.py`
