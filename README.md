# production-trace-patterns
Example data set and patterns accompanying the paper about Production Trace Patterns.

## Content

* `event-data/` contains the example data set (Turtle), split into three files following three ISA-95 levels.
* `sparql/` contains the SPARQL query templates that implement the patterns and can be used to derive the 'hidden' information.
* `apply_pattern_use_cases.py` script to execute the pattern queries for a set of use cases on the data in `event-data/`. The results are stored in `results/`.
* `apply_pattern_combined.py` script to execute certain pattern queries in sequence on the data in `event-data/` to demonstrate how patterns can be combined to derive additional information. The results are stored in `results_combined/`.

## Dependencies
Execution of the scripts to apply the patterns requires [rdflib](https://github.com/RDFLib) and its dependencies (BSD 3-clause License) to be installed.

## SPARQL query templates
In the templates the following variables can be used to parametrize the queries:
* `$EventType`: type of event to identify the main events of interest;
* `$IntervalStartType`: type of event used to identify the start of an interval;
* `$IntervalEndType`: type of event used to identify the end of an interval;
* `$PrecedingEventType`: type of event used to identify the (closest) preceding event;
* `$RelatedEntityType`: type of entity used to identify the entity for deriving relations;
* `$PartEntityType`: type of entity used to identify the lower aggregation level entity for deriving part of relation;
* `$attribute`: attribute that should be aggregated.

The list below gives an overview of the query templates and applicable parameters.
1. *interval_count-event*: `$IntervalStartType`, `$IntervalEndType`, `$EventType`
2. *interval_aggregate-attribute*: `$IntervalStartType`, `$IntervalEndType`, `$EventType`, `$attribute`
3. *elapsed-time_preceding*: `$EventType`, `$PrecedingEventType`
4. *elapsed-time_succeeding-same*: `$EventType`
5. *elapsed-time_maximum*: `$IntervalStartType`, `$IntervalEndType`
6. *event-entity_preceding*: `$EventType`, `$PrecedingEventType`
7. *entity-entity_partOf*
8. *event-entity_all-preceding*: `$RelatedEntityType`
9. *event-entity_all-succeeding*: `$RelatedEntityType`
10. *event-entity_partOf*: `$IntervalStartType`, `$IntervalEndType`, `$PartEntityType`