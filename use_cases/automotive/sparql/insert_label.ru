BASE <http://example.org/id/automotive/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX ptp: <http://example.org/def/production-trace-patterns/>

# Use the id (last part of URI) as the label
INSERT {
  GRAPH ?g {
    ?object rdfs:label ?label .
  }
}
WHERE {
  { SELECT DISTINCT ?g ?object {
    GRAPH ?g {
      {
        [] ?p ?object
      } UNION {
        ?object ?p []
      }
    }
  }}

  FILTER isIRI(?object)
  BIND(strafter(str(?object), str(<>)) AS ?label)
}
