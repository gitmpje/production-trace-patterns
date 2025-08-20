# production-trace-patterns
Data and code accompanying the paper about Production Trace Patterns.

## Content

* `use_cases` contains data and scripts for the use cases.
* `sparql/` contains the SPARQL query templates that implement the patterns and can be used to derive the 'hidden' information.
* `production-trace-patterns.ttl` contains the (lightweight) ontology.

## Dependencies
Execution of the scripts to apply the patterns requires [rdflib](https://github.com/RDFLib) and its dependencies (BSD 3-clause License) to be installed.

## SPARQL query templates
In the templates the following variables can be used to parametrize the queries:
* `$EventType`: type of event to identify the main events of interest;
* `$EntityType`: type of entity to identify the main entities of interest;
* `$ResourceType`: type of resource to identify the main resources of interest;
* `$IntervalStartType`: type of event used to identify the start of an interval;
* `$IntervalEndType`: type of event used to identify the end of an interval;
* `$PrecedingEventType`: type of event used to identify the (closest) preceding event;
* `$RelatedEntityType`: type of entity used to identify the entity for deriving relations;
* `$PartEntityType`: type of entity used to identify the lower aggregation level entity for deriving part of relation;
* `$attribute`: attribute that should be reported.

The list below gives an overview of the query templates and applicable parameters.
1. *interval_count-event*: `$IntervalStartType`, `$IntervalEndType`, `$EventType`
2. *interval_aggregate-attribute*: `$IntervalStartType`, `$IntervalEndType`, `$EventType`, `$attribute`
3. *elapsed-time_preceding*: `$EventType`, `$PrecedingEventType`
4. *elapsed-time_succeeding-same*: `$EventType`, `$attribute`
5. *elapsed-time_maximum*: `$IntervalStartType`, `$IntervalEndType`
6. *event-entity_preceding*: `$EventType`, `$PrecedingEventType`, `$ResourceType`, `$EntityType`
7. *event-entity_partOf*: `$EventType`, `$EntityType`
8. *event-entity_all-preceding*: `$EventType`, `$RelatedEntityType`
9. *event-entity_all-succeeding*: `$EventType`, `$RelatedEntityType`
10. *entity-entity_partOf*: `$IntervalStartType`, `$IntervalEndType`, `$PartEntityType`

## Notes
The SPARQL templates use filters to derive the chronological relation between events.
For better performance it can be benificial to materialize the chronological relations between events.
Work on Event Knowledge Graphs can be used as a reference for this.
Alternatively, a database with indexing of timestamps will also help to improve performance.
