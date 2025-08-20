base <http://example.org/id/automotive/>
prefix ex: <http://example.org/def/automotive/>
prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
prefix ptp: <http://example.org/def/production-trace-patterns/>

# Objects that are subject of entity relation are Events
insert {
  graph ?g { ?event a ptp:Event }
}
where {
  { select distinct ?g ?event {
    graph ?g {
      ?event ex:mainEntity [] .
      minus { ?event a ptp:Event }
    }
  }}
};

# Derive type based on graphs the entity occurs in
insert {
  graph ?g { ?event a ?type }
}
where {
  { select distinct ?g ?event ?type {
    graph ?g { ?event a ptp:Event }

    values (?g ?type) {
      (<http://example.org/graph/automotive/events/agvs> ptp:SwitchState)
      (<http://example.org/graph/automotive/events/modules> ptp:Observation)
      (<http://example.org/graph/automotive/events/products> ptp:Observation)
      (<http://example.org/graph/automotive/events/resources> ptp:SwitchState)
    }
  }}
};

# Derive order event type based on attributes
with <http://example.org/graph/automotive/events/orders>
insert {
  ?event a ?type .
}
where {
  {
    bind ( ptp:TrackIn as ?type )
    ?event a ptp:Event .
    minus { ?event ex:finished [] }
  } union {
    bind ( ptp:TrackOut as ?type )
    ?event a ptp:Event ;
      ex:finished [] .
  }
};

# Derive relation between module and product by comparing descriptions
insert {
  graph <http://example.org/graph/automotive/events/modules> {
    ?Module ptp:isPartOf ?Product .
  }
}
where {
  # Products with related modules
  graph <http://example.org/graph/automotive/events/products> {
    select distinct * {
      [] ex:mainEntity ?Product ;
        ex:productDescriptor ?productDescription .
    }
  }
  graph <http://example.org/graph/automotive/events/modules> {
    select distinct * {
      [] ex:mainEntity ?Module ;
        ex:description ?moduleDescription .
    }
  }
  filter regex(?moduleDescription, concat("^", ?productDescription))
};

# Derive aggregation of module into product by
# selecting on resources where modules are joined to the product
insert {
  graph <http://example.org/graph/automotive/events/orders> {
    ?Event a ptp:Aggregate ;
      ptp:entity ?Module .
  }
}
where {
  graph <http://example.org/graph/automotive/events/modules> {
    ?Module ptp:isPartOf ?Product .
  }

  # Order events
  graph <http://example.org/graph/automotive/events/orders> {
    ?Event a ptp:TrackOut ;
      ex:productEntity ?Product ;
      ex:allocatedToEntity ?Resource .
  }

  # Resources
  values ?Resource {
    <http://example.org/id/automotive/fbefdec2f0015c2c45d7356f> # F1_J1
    <http://example.org/id/automotive/9e198cf8cd73b25b153ce27d> # F1_J2
    <http://example.org/id/automotive/7454c32cca8e5c7e6c9d086e> # R1_J1
    <http://example.org/id/automotive/8f9e8c99cb96805cbecec2c6> # R1_J2
  }
};
