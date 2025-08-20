base <http://example.org/id/automotive/>
prefix ex: <http://example.org/def/automotive/>
prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
prefix ptp: <http://example.org/def/production-trace-patterns/>

# Derive type based on graphs the entity occurs in
insert {
  graph ?g { ?entity a ?type , ptp:Entity }
}
where {
  { select distinct ?g ?entity ?type {
    graph ?g { [] ex:mainEntity ?entity }

    values (?g ?type) {
      (<http://example.org/graph/automotive/events/stations> ptp:WorkStation)
      (<http://example.org/graph/automotive/events/products> ptp:Product)
      (<http://example.org/graph/automotive/events/modules> ptp:Component)
      (<http://example.org/graph/automotive/events/resources> ptp:Machine)
      (<http://example.org/graph/automotive/events/orders> ptp:Order)
      (<http://example.org/graph/automotive/events/agvs> ptp:AGV)
    }
  }}
};

# Derive abstract type
insert {
  graph ?g { ?entity a ?abstractType }
}
where {
  graph ?g { ?entity a ?type }

  values (?type ?abstractType) {
    (ptp:Machine ptp:Resource)
    (ptp:AGV ptp:Resource)
    (ptp:WorkStation ptp:Resource)
    (ptp:Product ptp:ProductionEntity)
    (ptp:Component ptp:ProductionEntity)
    (ptp:Order ptp:ProductionEntity)
  }
};
