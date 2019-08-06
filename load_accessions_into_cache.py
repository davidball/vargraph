import yaml
import csv
from collections import defaultdict
from neo4j.v1 import GraphDatabase
import os
import json
import requests
import mapping.mapping_by_transcript as mt
import logging

app_name = 'vargraph'
log = logging.getLogger(app_name)  # + "." + __name__)

mt.NEO4J_HOST_NAME = 'localhost'


def cache_accession_list(path):
    with open(path, 'r') as f:
        accessions = f.readlines()

    for accn in accessions:
        accn = accn.strip()
        if len(accn) > 0:
            print("begin attempt [%s]" % accn)
            pmg = mt.PathwayMatrixByGenes([])
            pmg.load_from_ngsreporter(accn)
            pmg.to_json()


if __name__ == "__main__":
    # load a file of 1 accession number per line and cache the json/matrix
    cache_accession_list('accessions_to_cache.txt')
