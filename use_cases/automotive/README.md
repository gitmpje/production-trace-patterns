# automotive
Automotive data set for demonstrating the patterns and their implementation in SPARQL.

## Content

* `data/` contains the data set (JSON).
* `docker-compose.yml` service definition for Jena Fuseki RDF Store.
* `load_data_rdf.py` script to enrich JSON data with JSON-LD context, upload data to RDF Store, and execute queries to align to data model.
* `apply_pattern.py` script to apply Production Trace Patterns implemented in SPARQL (on the data set loaded to the RDF Store).
* `without_pattern.py` script to derive insights without using the data model and Production Trace Patterns.

## Dependencies
* RDF Store, in this example [stain/jena-fuseki](https://hub.docker.com/r/stain/jena-fuseki) is used.

## Application of the patterns
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
4. Time a machine is in a state.
    * `$EventType=ptp:SwitchState`
5. Throughput time per product.
    * `$IntervalStartType=ptp:TrackIn`
    * `$IntervalEndType=ptp:TrackOut`
6. Relate event start processing on a machine to the AGV that delivered the product to that machine.
    * `$EventType=ptp:TrackIn`
    * `$PrecedingEventType=ptp:TrackOut` # TODO: derive AGV TrackIn/TrackOut events
7. Relate machine level events to the station.
8. 
9. 
10. 