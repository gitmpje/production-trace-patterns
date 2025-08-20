base <http://example.org/id/automotive/>
prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
prefix ptp: <http://example.org/def/production-trace-patterns/>

# Use the id (last part of URI) as the label
insert {
  graph ?g {
    ?object rdfs:label ?label .
  }
}
where {
  { select distinct ?g ?object {
    graph ?g {
      {
        [] ?p ?object
      } union {
        ?object ?p []
      }
    }
  }}

  filter isIRI(?object)
  bind(strafter(str(?object), str(<>)) as ?label)
};
