BASE <http://example.org/id/automotive/>
PREFIX ex: <http://example.org/def/automotive/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX ptp: <http://example.org/def/production-trace-patterns/>

# Insert generic entity relation
INSERT {
  GRAPH ?g { ?event ptp:entity ?entity }
}
WHERE {
  GRAPH ?g {
    ?event ex:productEntity|ex:allocatedToEntity|ex:locatedAtEntity|ex:contentEntity|ex:fromEntity|ex:toEntity ?entity .
  }
}
