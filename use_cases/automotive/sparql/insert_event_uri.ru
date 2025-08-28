base <http://example.org/id/automotive/>
prefix ex: <http://example.org/def/automotive/>
prefix ptp: <http://example.org/def/production-trace-patterns/>

# Construct URI based on main entity and timestamp
delete {
  graph ?g { ?Event ?p ?o }
}
insert {
  graph ?g { ?EventURI ?p ?o }
}
where {
  graph ?g {
    {
      select distinct
        ?Event
        (uri(concat(str(?mainEntity), "_", str(?atTime))) as ?EventURI)
      where {
        ?Event a ptp:Event ;
          ptp:atTime ?atTime ;
          ex:mainEntity ?mainEntity .
        filter isBlank(?Event)
      }
    }

    ?Event ?p ?o .
  }
};
