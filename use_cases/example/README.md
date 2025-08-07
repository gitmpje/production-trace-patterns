# example
Small example data set for demonstrating the patterns and their implementation in SPARQL.

## Content

* `data/` contains the example data set (Turtle), split into three files following three ISA-95 levels.
* `apply_pattern_use_cases.py` script to execute the pattern queries for a set of use cases on the data in `event-data/`. The results are stored in `results/`.
* `apply_pattern_combined.py` script to execute certain pattern queries in sequence on the data in `event-data/` to demonstrate how patterns can be combined to derive additional information. The results are stored in `results_combined/`.

The scripts load the data to an in-memory graph on which the SPARQL query with parameter bindings are executed.
