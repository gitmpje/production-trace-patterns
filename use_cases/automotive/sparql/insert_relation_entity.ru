base <http://example.org/id/automotive/>
prefix ex: <http://example.org/def/automotive/>
prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
prefix ptp: <http://example.org/def/production-trace-patterns/>

# Insert generic entity relation
insert {
  graph ?g { ?event ptp:entity ?entity }
}
where {
  graph ?g {
    ?event ex:mainEntity|ex:productEntity|ex:allocatedToEntity|ex:locatedAtEntity|ex:contentEntity ?entity .
  }
};

# Infer isPartOf from children relation
insert {
  graph ?g { ?childEntity ptp:isPartOf ?parentEntity }
}
where {
  graph ?g {
    [] ex:mainEntity ?parentEntity ;
      ex:children/ptp:mainEntity ?childEntity .
  }
};
