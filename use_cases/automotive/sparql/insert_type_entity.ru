BASE <http://example.org/id/automotive/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX ptp: <http://example.org/def/production-trace-patterns/>

# Derive type based on graphs the entity occurs in
INSERT {
  GRAPH ?g { ?entity a ?type , ptp:Entity }
}
WHERE {
  { SELECT DISTINCT ?g ?entity ?type {
    GRAPH ?g { [] ptp:entity ?entity }

    VALUES (?g ?type) {
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
INSERT {
  GRAPH ?g { ?entity a ?abstractType }
}
WHERE {
  GRAPH ?g { ?entity a ?type }

  VALUES (?type ?abstractType) {
    (ptp:Machine ptp:Resource)
    (ptp:AGV ptp:Resource)
    (ptp:WorkStation ptp:Resource)
    (ptp:Product ptp:ProductionEntity)
    (ptp:Component ptp:ProductionEntity)
    (ptp:Order ptp:ProductionEntity)
  }
}
