BASE <http://example.org/id/automotive/>
PREFIX ex: <http://example.org/def/automotive/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX ptp: <http://example.org/def/production-trace-patterns/>

# Infer isPartOf from children relation
INSERT {
  GRAPH ?g { ?Child ptp:isPartOf ?Parent }
}
WHERE {
  GRAPH ?g { 
    [] ex:mainEntity ?Parent ;
      ex:children/ex:mainEntity ?Child .
  }
};
