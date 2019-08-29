import yaml
import csv
from collections import defaultdict
from neo4j.v1 import GraphDatabase
import os
import json
import requests
import logging
import sys
import time
import mapping.static_reactome_pathways as srp

NEO4J_HOST_NAME = 'neo4j'

app_name = 'vargraph'
log = logging.getLogger(app_name)  # + "." + __name__)


handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
log.addHandler(handler)
log.setLevel(logging.DEBUG)


# factory method to instantiate a PathwayMatrixByGenes and load in a
# case by Accession Number
def load_by_accession_number(accession_number, allow_cache=True):
    pm = PathwayMatrixByGenesStatic()

    pm.load_from_ngsreporter(accession_number, allow_cache)

    return pm


# class ReactomeQuery():

    # hmmm way too broad, but why? not sure yet.

#     MATCH (n:ReferenceEntity)<-[r1:referenceEntity]-(re{speciesName:'Homo sapiens'}) where ('PIK3R1' in n.name)
# with re,r1,n
# MATCH path1=(re)<-[r:input|output|catalystActivity|physicalEntity|regulatedBy|regulator|hasComponent|hasMember|hasCandidate*]-(c)
# with re,r,c,r1,n,path1
# MATCH path2=(p:Pathway)-[e:hasEvent*]->(c)
# return re,r,c,p,e,r1,n,path1,path2 limit 1000

def runquery(cyphertext):
    # these might not work so well I think by the time clients try to acccess the data i.e. via .values()
    # the connection is already closed and an exception is raised
    return ReactomeConnector().runquery(cyphertext)


def runqueryraw(cyphertext):
    # these might not work so well I think by the time clients try to acccess the data i.e. via .values()
    # the connection is already closed and an exception is raised

    return ReactomeConnector().runqueryraw(cyphertext)


def runquery_asgraph(cyphertext):
    # these might not work so well I think by the time clients try to acccess the data i.e. via .values()
    # the connection is already closed and an exception is raised

    return ReactomeConnector().runqueryraw_asgraph(cyphertext)

# print(runquery(pathways_by_gene_list(['PIK3R1'])))
# x = runquery(pathways_by_gene_list(['PIK3R1']))
# n_ids = [r[6].id for r in x]


spacer = "------------------------------"


def dostuff():
    spacer = "------------------------------"

    transcript_path = "data/config_panels_transcripts.yaml"

    with open(transcript_path) as f:
        transcripts = yaml.load(f)

    tst170 = transcripts['tst170']
    cypher_list = "['%s']" % "','".join(tst170.values())
    cypher = "match (n) where size([x IN %s | x in n.otherIdentifier]) >0 return n" % cypher_list
    # match (n:EntityWithAccessionedSequence) where size([x IN ['NM_005157','NM_001014432','NM_001626','NM_005465','NM_004304','NM_000038','NM_000044','NM_006015','NM_000051','NM_001184','NM_001699','NM_004656','NM_000465','NM_000633','NM_001706','NM_004333','NM_007294','NM_000059','NM_032043','NM_000061','NM_032415','NM_053056','NM_001759','NM_001760','NM_001238','NM_001783','NM_000626','NM_004360','NM_016507','NM_000075','NM_001259','NM_000077','NM_004364','NM_001114122','NM_007194','NM_004380','NM_005211','NM_001904','NM_001014796','NM_022552','NM_005228','NM_019063','NM_001429','NM_004448','NM_001982','NM_005235','NM_202001','NM_000400','NM_004449','NM_001122742','NM_005238','NM_004956','NM_001079675','NM_004454','NM_005243','NM_004456','NM_139076','NM_001113378','NM_018062','NM_033632','NM_001144892','NM_004465','NM_175929','NM_005117','NM_002006','NM_020638','NM_005247','NM_002007','NM_004464','NM_020996','NM_002009','NM_033163','NM_002010','NM_023110','NM_000141','NM_000142','NM_022963','NM_002017','NM_002019','NM_004119','NM_023067','NM_182625','NM_002067','NM_002072','NM_000516','NM_000545','NM_005343','NM_005896','NM_002168','NM_003866','NM_004972','NM_000215','NM_002253','NM_004521','NM_000222','NM_005933','NM_004985','NM_005561','NM_002755','NM_030662','NM_021960','NM_002392','NM_002393','NM_001127500','NM_000249','NM_004529','NM_005373','NM_005590','NM_000251','NM_002439','NM_000179','NM_004958','NM_012222','NM_002467','NM_001033082','NM_005378','NM_002468','NM_002485','NM_001042492','NM_017617','NM_024408','NM_000435','NM_002520','NM_002524','NM_013957','NM_002529','NM_006180','NM_002530','NM_024675','NM_181459','NM_002584','NM_006206','NM_002609','NM_006218','NM_006219','NM_005026','NM_001282427','NM_181523','NM_000535','NM_015869','NM_002717','NM_000264','NM_000314','NM_002834','NM_002875','NM_133509','NM_058216','NM_002878','NM_003579','NM_002880','NM_000321','NM_020975','NM_152756','NM_002944','NM_001272060','NM_032444','NM_005359','NM_003073','NM_005631','NM_005417','NM_000455','NM_198253','NM_001127208','NM_001128148','NM_005656','NM_000546','NM_000368','NM_000548','NM_000551','NM_005431'] | x in n.otherIdentifier]) >0 return n.stId, n.otherIdentifier
    print(cypher)

    # note: do not filter by n.speciesName for these, it doesn't seem to exist as a key on the nodes that we are looking for

    cypher_list = "(('%s' in n.otherIdentifier))" % "' in n.otherIdentifier) or ('".join(
        tst170.values())
    cypher = "match (n) where %s return n.stId, n.otherIdentifier" % cypher_list
    print(cypher)

    cypher = "match (n) where %s return n" % cypher_list
    print(cypher)

    #  match (n:EntityWithAccessionedSequence) where n.speciesName='Homo sapiens' and size([x IN ['NM_005157','NM_001014432','NM_001626','NM_005465','NM_004304','NM_000038','NM_000044','NM_006015','NM_000051','NM_001184','NM_001699','NM_004656','NM_000465','NM_000633','NM_001706','NM_004333','NM_007294','NM_000059','NM_032043','NM_000061','NM_032415','NM_053056','NM_001759','NM_001760','NM_001238','NM_001783','NM_000626','NM_004360','NM_016507','NM_000075','NM_001259','NM_000077','NM_004364','NM_001114122','NM_007194','NM_004380','NM_005211','NM_001904','NM_001014796','NM_022552','NM_005228','NM_019063','NM_001429','NM_004448','NM_001982','NM_005235','NM_202001','NM_000400','NM_004449','NM_001122742','NM_005238','NM_004956','NM_001079675','NM_004454','NM_005243','NM_004456','NM_139076','NM_001113378','NM_018062','NM_033632','NM_001144892','NM_004465','NM_175929','NM_005117','NM_002006','NM_020638','NM_005247','NM_002007','NM_004464','NM_020996','NM_002009','NM_033163','NM_002010','NM_023110','NM_000141','NM_000142','NM_022963','NM_002017','NM_002019','NM_004119','NM_023067','NM_182625','NM_002067','NM_002072','NM_000516','NM_000545','NM_005343','NM_005896','NM_002168','NM_003866','NM_004972','NM_000215','NM_002253','NM_004521','NM_000222','NM_005933','NM_004985','NM_005561','NM_002755','NM_030662','NM_021960','NM_002392','NM_002393','NM_001127500','NM_000249','NM_004529','NM_005373','NM_005590','NM_000251','NM_002439','NM_000179','NM_004958','NM_012222','NM_002467','NM_001033082','NM_005378','NM_002468','NM_002485','NM_001042492','NM_017617','NM_024408','NM_000435','NM_002520','NM_002524','NM_013957','NM_002529','NM_006180','NM_002530','NM_024675','NM_181459','NM_002584','NM_006206','NM_002609','NM_006218','NM_006219','NM_005026','NM_001282427','NM_181523','NM_000535','NM_015869','NM_002717','NM_000264','NM_000314','NM_002834','NM_002875','NM_133509','NM_058216','NM_002878','NM_003579','NM_002880','NM_000321','NM_020975','NM_152756','NM_002944','NM_001272060','NM_032444','NM_005359','NM_003073','NM_005631','NM_005417','NM_000455','NM_198253','NM_001127208','NM_001128148','NM_005656','NM_000546','NM_000368','NM_000548','NM_000551','NM_005431'] | x in n.otherIdentifier]) >0 return n.stID, n.otherIdentifier

    # match (n:EntityWithAccessionedSequence) where n.speciesName='Homo sapiens' and size([x IN ['NM_005157','NM_001014432','NM_001626','NM_005465','NM_004304','NM_000038','NM_000044','NM_006015','NM_000051','NM_001184','NM_001699','NM_004656','NM_000465','NM_000633','NM_001706','NM_004333','NM_007294','NM_000059','NM_032043','NM_000061','NM_032415','NM_053056','NM_001759','NM_001760','NM_001238','NM_001783','NM_000626','NM_004360','NM_016507','NM_000075','NM_001259','NM_000077','NM_004364','NM_001114122','NM_007194','NM_004380','NM_005211','NM_001904','NM_001014796','NM_022552','NM_005228','NM_019063','NM_001429','NM_004448','NM_001982','NM_005235','NM_202001','NM_000400','NM_004449','NM_001122742','NM_005238','NM_004956','NM_001079675','NM_004454','NM_005243','NM_004456','NM_139076','NM_001113378','NM_018062','NM_033632','NM_001144892','NM_004465','NM_175929','NM_005117','NM_002006','NM_020638','NM_005247','NM_002007','NM_004464','NM_020996','NM_002009','NM_033163','NM_002010','NM_023110','NM_000141','NM_000142','NM_022963','NM_002017','NM_002019','NM_004119','NM_023067','NM_182625','NM_002067','NM_002072','NM_000516','NM_000545','NM_005343','NM_005896','NM_002168','NM_003866','NM_004972','NM_000215','NM_002253','NM_004521','NM_000222','NM_005933','NM_004985','NM_005561','NM_002755','NM_030662','NM_021960','NM_002392','NM_002393','NM_001127500','NM_000249','NM_004529','NM_005373','NM_005590','NM_000251','NM_002439','NM_000179','NM_004958','NM_012222','NM_002467','NM_001033082','NM_005378','NM_002468','NM_002485','NM_001042492','NM_017617','NM_024408','NM_000435','NM_002520','NM_002524','NM_013957','NM_002529','NM_006180','NM_002530','NM_024675','NM_181459','NM_002584','NM_006206','NM_002609','NM_006218','NM_006219','NM_005026','NM_001282427','NM_181523','NM_000535','NM_015869','NM_002717','NM_000264','NM_000314','NM_002834','NM_002875','NM_133509','NM_058216','NM_002878','NM_003579','NM_002880','NM_000321','NM_020975','NM_152756','NM_002944','NM_001272060','NM_032444','NM_005359','NM_003073','NM_005631','NM_005417','NM_000455','NM_198253','NM_001127208','NM_001128148','NM_005656','NM_000546','NM_000368','NM_000548','NM_000551','NM_005431'] | x in n.otherIdentifier]) >0 return n.stID, n.otherIdentifier,size(filter(y in  [x IN ['NM_005157','NM_001014432','NM_001626','NM_005465','NM_004304','NM_000038','NM_000044','NM_006015','NM_000051','NM_001184','NM_001699','NM_004656','NM_000465','NM_000633','NM_001706','NM_004333','NM_007294','NM_000059','NM_032043','NM_000061','NM_032415','NM_053056','NM_001759','NM_001760','NM_001238','NM_001783','NM_000626','NM_004360','NM_016507','NM_000075','NM_001259','NM_000077','NM_004364','NM_001114122','NM_007194','NM_004380','NM_005211','NM_001904','NM_001014796','NM_022552','NM_005228','NM_019063','NM_001429','NM_004448','NM_001982','NM_005235','NM_202001','NM_000400','NM_004449','NM_001122742','NM_005238','NM_004956','NM_001079675','NM_004454','NM_005243','NM_004456','NM_139076','NM_001113378','NM_018062','NM_033632','NM_001144892','NM_004465','NM_175929','NM_005117','NM_002006','NM_020638','NM_005247','NM_002007','NM_004464','NM_020996','NM_002009','NM_033163','NM_002010','NM_023110','NM_000141','NM_000142','NM_022963','NM_002017','NM_002019','NM_004119','NM_023067','NM_182625','NM_002067','NM_002072','NM_000516','NM_000545','NM_005343','NM_005896','NM_002168','NM_003866','NM_004972','NM_000215','NM_002253','NM_004521','NM_000222','NM_005933','NM_004985','NM_005561','NM_002755','NM_030662','NM_021960','NM_002392','NM_002393','NM_001127500','NM_000249','NM_004529','NM_005373','NM_005590','NM_000251','NM_002439','NM_000179','NM_004958','NM_012222','NM_002467','NM_001033082','NM_005378','NM_002468','NM_002485','NM_001042492','NM_017617','NM_024408','NM_000435','NM_002520','NM_002524','NM_013957','NM_002529','NM_006180','NM_002530','NM_024675','NM_181459','NM_002584','NM_006206','NM_002609','NM_006218','NM_006219','NM_005026','NM_001282427','NM_181523','NM_000535','NM_015869','NM_002717','NM_000264','NM_000314','NM_002834','NM_002875','NM_133509','NM_058216','NM_002878','NM_003579','NM_002880','NM_000321','NM_020975','NM_152756','NM_002944','NM_001272060','NM_032444','NM_005359','NM_003073','NM_005631','NM_005417','NM_000455','NM_198253','NM_001127208','NM_001128148','NM_005656','NM_000546','NM_000368','NM_000548','NM_000551','NM_005431'] | x in n.otherIdentifier] where y is not null )) as theSize

    # match (n:EntityWithAccessionedSequence) where n.speciesName='Homo sapiens' and size(filter(y in  [x IN ['NM_005157','NM_001014432','NM_001626','NM_005465','NM_004304','NM_000038','NM_000044','NM_006015','NM_000051','NM_001184','NM_001699','NM_004656','NM_000465','NM_000633','NM_001706','NM_004333','NM_007294','NM_000059','NM_032043','NM_000061','NM_032415','NM_053056','NM_001759','NM_001760','NM_001238','NM_001783','NM_000626','NM_004360','NM_016507','NM_000075','NM_001259','NM_000077','NM_004364','NM_001114122','NM_007194','NM_004380','NM_005211','NM_001904','NM_001014796','NM_022552','NM_005228','NM_019063','NM_001429','NM_004448','NM_001982','NM_005235','NM_202001','NM_000400','NM_004449','NM_001122742','NM_005238','NM_004956','NM_001079675','NM_004454','NM_005243','NM_004456','NM_139076','NM_001113378','NM_018062','NM_033632','NM_001144892','NM_004465','NM_175929','NM_005117','NM_002006','NM_020638','NM_005247','NM_002007','NM_004464','NM_020996','NM_002009','NM_033163','NM_002010','NM_023110','NM_000141','NM_000142','NM_022963','NM_002017','NM_002019','NM_004119','NM_023067','NM_182625','NM_002067','NM_002072','NM_000516','NM_000545','NM_005343','NM_005896','NM_002168','NM_003866','NM_004972','NM_000215','NM_002253','NM_004521','NM_000222','NM_005933','NM_004985','NM_005561','NM_002755','NM_030662','NM_021960','NM_002392','NM_002393','NM_001127500','NM_000249','NM_004529','NM_005373','NM_005590','NM_000251','NM_002439','NM_000179','NM_004958','NM_012222','NM_002467','NM_001033082','NM_005378','NM_002468','NM_002485','NM_001042492','NM_017617','NM_024408','NM_000435','NM_002520','NM_002524','NM_013957','NM_002529','NM_006180','NM_002530','NM_024675','NM_181459','NM_002584','NM_006206','NM_002609','NM_006218','NM_006219','NM_005026','NM_001282427','NM_181523','NM_000535','NM_015869','NM_002717','NM_000264','NM_000314','NM_002834','NM_002875','NM_133509','NM_058216','NM_002878','NM_003579','NM_002880','NM_000321','NM_020975','NM_152756','NM_002944','NM_001272060','NM_032444','NM_005359','NM_003073','NM_005631','NM_005417','NM_000455','NM_198253','NM_001127208','NM_001128148','NM_005656','NM_000546','NM_000368','NM_000548','NM_000551','NM_005431'] | x in n.otherIdentifier] where y is not null )) >0 return n.stID, n.otherIdentifier,size(filter(y in  [x IN ['NM_005157','NM_001014432','NM_001626','NM_005465','NM_004304','NM_000038','NM_000044','NM_006015','NM_000051','NM_001184','NM_001699','NM_004656','NM_000465','NM_000633','NM_001706','NM_004333','NM_007294','NM_000059','NM_032043','NM_000061','NM_032415','NM_053056','NM_001759','NM_001760','NM_001238','NM_001783','NM_000626','NM_004360','NM_016507','NM_000075','NM_001259','NM_000077','NM_004364','NM_001114122','NM_007194','NM_004380','NM_005211','NM_001904','NM_001014796','NM_022552','NM_005228','NM_019063','NM_001429','NM_004448','NM_001982','NM_005235','NM_202001','NM_000400','NM_004449','NM_001122742','NM_005238','NM_004956','NM_001079675','NM_004454','NM_005243','NM_004456','NM_139076','NM_001113378','NM_018062','NM_033632','NM_001144892','NM_004465','NM_175929','NM_005117','NM_002006','NM_020638','NM_005247','NM_002007','NM_004464','NM_020996','NM_002009','NM_033163','NM_002010','NM_023110','NM_000141','NM_000142','NM_022963','NM_002017','NM_002019','NM_004119','NM_023067','NM_182625','NM_002067','NM_002072','NM_000516','NM_000545','NM_005343','NM_005896','NM_002168','NM_003866','NM_004972','NM_000215','NM_002253','NM_004521','NM_000222','NM_005933','NM_004985','NM_005561','NM_002755','NM_030662','NM_021960','NM_002392','NM_002393','NM_001127500','NM_000249','NM_004529','NM_005373','NM_005590','NM_000251','NM_002439','NM_000179','NM_004958','NM_012222','NM_002467','NM_001033082','NM_005378','NM_002468','NM_002485','NM_001042492','NM_017617','NM_024408','NM_000435','NM_002520','NM_002524','NM_013957','NM_002529','NM_006180','NM_002530','NM_024675','NM_181459','NM_002584','NM_006206','NM_002609','NM_006218','NM_006219','NM_005026','NM_001282427','NM_181523','NM_000535','NM_015869','NM_002717','NM_000264','NM_000314','NM_002834','NM_002875','NM_133509','NM_058216','NM_002878','NM_003579','NM_002880','NM_000321','NM_020975','NM_152756','NM_002944','NM_001272060','NM_032444','NM_005359','NM_003073','NM_005631','NM_005417','NM_000455','NM_198253','NM_001127208','NM_001128148','NM_005656','NM_000546','NM_000368','NM_000548','NM_000551','NM_005431'] | x in n.otherIdentifier] where y is not null )) as theSize

    #     better:

    #     MATCH (n:ReferenceEntity)<-[r:referenceEntity]-(re) where ('NM_001127208' in n.otherIdentifier)
    # with re
    # MATCH (re)<-[r:input|output|catalystActivity|physicalEntity|regulatedBy|regulator|hasComponent|hasMember|hasCandidate*]-(c)
    # return re,r,c
    # sample case:
    # '19-078-11239'
    case_transcripts = ["NM_001127208", "NM_001127208", "NM_032458",
                        "NM_032458", "NM_015338", "NM_032458", "NM_032458", "NM_032458"]
    # x = r('19-078-11239')
    # x.variant_calls.map {|v| v.gene_name}.uniq
    case_genes = ["TET2", "PHF6", "ASXL1"]

    # of those the only ones that actually match in reactome are:
    case_transcripts = ['NM_001127208', 'NM_015338']

    print("subgraph_by_transcript_ids(case_transcripts)")
    print(subgraph_by_transcript_ids(case_transcripts))
    print(spacer)
    print("subgraph_by_transcript_ids_with_neighbors(case_transcripts)")
    print(subgraph_by_transcript_ids_with_neighbors(case_transcripts))
    print(spacer)
    print(subgraph_by_transcript_ids_with_neighbors_two_deep(case_transcripts))
    print(spacer)
    print(subgraph_by_transcript_ids_with_neighbors_three_deep(case_transcripts))
    print(spacer)
    print(subgraph_by_transcript_ids_using_with(case_transcripts, 2))

    print(spacer)

    print(pathways_by_transcript_id('NM_001127208'))

    print(spacer)

    print(pathways_by_transcript_list(case_transcripts))

    print(spacer)
    print("pathways by gene")
    print(pathways_by_gene_list(case_genes))

    print(spacer)
    print("pathways by gene...executes fast but without limit 100ish browser bogs down")
    print(pathways_by_gene_list(['PIK3R1']))


class ReactomeConnector():

    def __init__(self, uri="", user='neo4j', password=os.environ['REACTOME_PWD']):

        if len(uri) == 0:
            uri = ReactomeConnector.default_neo4j_host()

        self._driver = GraphDatabase.driver(uri, auth=(user, password))
        self._session = self._driver.session()
        log.info("Reached end of ReactomeConnector.__init__")

    def default_neo4j_host():
        return "bolt://%s:7687" % NEO4J_HOST_NAME

    def runquery(self, cyphertext):
        log.debug("begin plain 'runquery' method")
        result = self.runqueryraw(cyphertext)
        results = result.values()
        log.debug("Finished query, %i values" % len(results))
        return results

    def runqueryraw(self, cyphertext):
        log.debug("About to run query:")
        log.debug(cyphertext)
        r = self._session.run(cyphertext)
        log.debug("finished query")
        return r

    def runqueryraw_asgraph(self, cyphertext):
        return self.runqueryraw(cyphertext).graph()

# REACTOME = ReactomeConnector()


if __name__ == "__main__":
    dostuff()
    user = 'neo4j'
    password = 'reactome'
    password = os.environ['REACTOME_PWD']
    uri = "bolt://0.0.0.0:7687"
    driver = GraphDatabase.driver(uri, auth=(user, password))
    sess = driver.session()
