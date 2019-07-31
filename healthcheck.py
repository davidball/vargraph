import yaml
import csv
from collections import defaultdict
from neo4j.v1 import GraphDatabase
import os
import json
import requests

def healthcheck():
  print("healthcheck begin")
  uri="bolt://neo4j:7687"
  user='neo4j'
  password = os.environ['REACTOME_PWD']
  _driver = GraphDatabase.driver(uri, auth=(user, password))
  _session = _driver.session()
  print("about to test query")
  values = _session.run('MATCH (n) RETURN n Limit 10;').values()
  print(values)
  print("tested_query")
  return values


if __name__ == "__main__":
  healthcheck()

