BASE <http://example.org/id/automotive/>
PREFIX ex: <http://example.org/def/automotive/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX ptp: <http://example.org/def/production-trace-patterns/>

# Infer isPartOf from children relation
INSERT {
  GRAPH ?g { ?o ptp:isPartOf ?s }
}
WHERE {
  GRAPH ?g { ?s ex:children ?o }
}
