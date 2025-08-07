# example
Small example data set for demonstrating the patterns and their implementation in SPARQL.

## Content

* `data/` contains the example data set (Turtle), split into three files following three ISA-95 levels.
* `apply_pattern_use_cases.py` script to apply Production Trace Patterns implemented in SPARQL for a set of use cases on the data in `data/`. The results are stored in `results/`.
* `apply_pattern_combined.py` script to apply certain patterns in sequence on the data in `data/` to demonstrate how patterns can be combined to derive additional information. The results are stored in `results_combined/`.

The scripts load the data to an in-memory graph on which the SPARQL query with parameter bindings are executed.
