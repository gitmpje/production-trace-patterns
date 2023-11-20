# production-trace-patterns
Example data set and patterns accompanying the paper about Production Trace Patterns.

## Content

* `event-data/` contains the example data set (Turtle), split into three files following three ISA-95 levels.
* `sparql/` contains the (template) SPARQL queries that implement the patterns and can be used to derive the 'hidden' information.
* `apply_pattern_use_cases.py` script to execute the pattern queries for a set of use cases on the data in `event-data/`. The results are stored in `results/`.
* `apply_pattern_combined.py` script to execute certain pattern queries in sequence on the data in `event-data/` to demonstrate how patterns can be combined to derive additional information. The results are stored in `results_combined/`.

## Dependencies
Execution of the scripts to apply the patterns requires [rdflib](https://github.com/RDFLib) and its dependencies (BSD 3-clause License) to be installed.