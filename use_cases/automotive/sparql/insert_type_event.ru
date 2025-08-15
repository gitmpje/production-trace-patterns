BASE <http://example.org/id/automotive/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX ptp: <http://example.org/def/production-trace-patterns/>

# Objects that are subject of entity relation are Events
INSERT {
  GRAPH ?g { ?event a ptp:Event }
}
WHERE {
  { SELECT DISTINCT ?g ?event {
    GRAPH ?g {
      ?event ptp:entity [] .
      MINUS { ?event a ptp:Event }
    }
  }}
};

# Derive type based on graphs the entity occurs in
INSERT {
  GRAPH ?g { ?event a ?type }
}
WHERE {
  { SELECT DISTINCT ?g ?event ?type {
    GRAPH ?g { ?event a ptp:Event }

    VALUES (?g ?type) {
      (<http://example.org/graph/automotive/events/resources> ptp:SwitchState)
    }
  }}
};

# Derive type based on attributes
WITH <http://example.org/graph/automotive/events/orders>
INSERT {
  ?event a ?type .
}
WHERE {
  {
    ?event a ptp:Event .
    MINUS { ?event ex:finished [] }
    BIND ( ptp:TrackIn AS ?type )
  } UNION {
    ?event a ptp:Event ;
      ex:finished [] .
    BIND ( ptp:TrackOut AS ?type )
  }
}
