import yaml
import csv
from collections import defaultdict
from neo4j.v1 import GraphDatabase
import os
import json
import requests
import logging

app_name = 'vargraph'
log = logging.getLogger(app_name) # + "." + __name__)

def subgraph_by_transcript_ids(transcript_ids, with_statement = False):
    cypher_list ="(('%s' in n.otherIdentifier))" % "' in n.otherIdentifier) or ('".join(transcript_ids)
    cypher = "match (n:ReferenceGeneProduct) where %s %s n" % (cypher_list, ("WITH" if with_statement else "RETURN"))
    return cypher

def subgraph_by_genes(genes, with_statement = False):
    cypher_list ="(('%s' in n.otherIdentifier))" % "' in n.otherIdentifier) or ('".join(genes)
    cypher = "match (n:ReferenceGeneProduct) where %s %s n" % (cypher_list, ("WITH" if with_statement else "RETURN"))
    return cypher

def subgraph_by_transcript_ids_with_neighbors(transcript_ids):
    #note: filtering out species relationship as it is noise
    cypher_list ="(('%s' in n.otherIdentifier))" % "' in n.otherIdentifier) or ('".join(transcript_ids)
    cypher = "match (n)-[r]-(anyneighbor) where not (n)-[r:species]-(anyneighbor) and %s return n, anyneighbor" % cypher_list
    return cypher

def subgraph_by_transcript_ids_with_neighbors_two_deep(transcript_ids):
    #note: filtering out species relationship as it is noise
    cypher_list ="(('%s' in n.otherIdentifier))" % "' in n.otherIdentifier) or ('".join(transcript_ids)
    cypher = "match (n)-[r]-(anyneighbor)-[r2]-(n2) where not (anyneighbor:ReferenceDatabase) and not (n2:ReferenceDatabase) and not (anyneighbor:InstanceEdit) and not (n:InstanceEdit) and not (n2:InstanceEdit) and not (n)-[r:species]-(anyneighbor) and not (anyneighbor)-[r2:species]-(n2) and %s return n, anyneighbor,n2" % cypher_list
    return cypher

def subgraph_by_transcript_ids_with_neighbors_three_deep(transcript_ids):
    #note: filtering out species relationship as it is noise
    cypher_list ="(('%s' in n.otherIdentifier))" % "' in n.otherIdentifier) or ('".join(transcript_ids)
    cypher = "match (n)-[r]-(anyneighbor)-[r2]-(n2)-[r3]-(n3) where not (anyneighbor:ReferenceDatabase) and not (n2:ReferenceDatabase) and not (anyneighbor:InstanceEdit) and not (n:InstanceEdit) and not (n2:InstanceEdit) and not (n3:InstanceEdit) and not (n3:ReferenceDatabase) and not (n)-[r:species]-(anyneighbor) and not (n3:Species) and not (anyneighbor)-[r2:species]-(n2) and %s return n, anyneighbor,n2,n3" % cypher_list
    return cypher


def layer_filter_clause(layer_node_alias):
    exclude_node_types = [
        'Species',
        'Compartment',
        'ReferenceDatabase',
        'InstanceEdit'
    ]

    filter_list_template = 'not (%s:' + ') and not (%s:'.join(exclude_node_types) + ')'
    
    layer_node_filter = filter_list_template % ((layer_node_alias,) * len(exclude_node_types))
    return layer_node_filter

def layer_clause(from_node_alias, to_node_alias):
    return "MATCH (%s)-[r]-(%s) where %s" % (from_node_alias, to_node_alias, layer_filter_clause(to_node_alias))

def subgraph_by_transcript_ids_using_with(transcript_ids, depth = 3):
    #note: filtering out species relationship as it is noise

    

    cypher_list ="(('%s' in n.otherIdentifier))" % "' in n.otherIdentifier) or ('".join(transcript_ids)
    #cypher = "match (n)-[r]-(anyneighbor)-[r2]-(n2)-[r3]-(n3) where not (anyneighbor:ReferenceDatabase) and not (n2:ReferenceDatabase) and not (anyneighbor:InstanceEdit) and not (n:InstanceEdit) and not (n2:InstanceEdit) and not (n3:InstanceEdit) and not (n3:ReferenceDatabase) and not (n)-[r:species]-(anyneighbor) and not (n3:Species) and not (anyneighbor)-[r2:species]-(n2) and %s return n, anyneighbor,n2,n3" % cypher_list
    
    cypher_variant_filter = "MATCH (n) where %s \nwith n" % cypher_list
    

    cypher = cypher_variant_filter + "\n" + \
        layer_clause('n','n2') + \
        "\nWITH n,n2\n" + \
        layer_clause('n2','n3') + \
        "\nWITH n,n2,n3\n"+ \
        layer_clause('n3','n4') + \
        "\nRETURN n,n2,n3,n4"
#    cypher = "%s\nMATCH (n)-[r]-(%s) where %s\nRETURN n,%s" % (cypher_variant_filter, layer_node_alias, layer_node_filter, layer_node_alias)

    return cypher


def profile_protein(transcript_id):
    cypher = "MATCH (n:ReferenceEntity)<-[r:referenceEntity]-(re:EntityWithAccessionedSequence{speciesName:'Homo sapiens'}) where ('NM_001127208' in n.otherIdentifier) \
with re \
MATCH (re)-[r:hasComponent]-(c) \
with re,r,c \
MATCH (c)-[r2:hasComponent]-(n3) \
with re,r,c,n3 \
MATCH (n3)-[r3:input|output]-(n4) \
return re,r,c,n3,n4,r3"
    return cypher







#wow
# MATCH (n:ReferenceEntity)<-[r1:referenceEntity]-(re) where ('NM_001127208' in n.otherIdentifier) 
# with re,r1,n
# MATCH path1=(re)<-[r:input|output|catalystActivity|physicalEntity|regulatedBy|regulator|hasComponent|hasMember|hasCandidate*]-(c)
# with re,r,c,r1,n,path1
# MATCH path2=(p:Pathway)-[e:hasEvent*]->(c)
# return re,r,c,p,e,r1,n,path1,path2


def finding_by_gene_experiment(gene):
    cypher = 'match path=(n:EntityWithAccessionedSequence{speciesName:"Homo sapiens"})-[r*0..2]-(n2:EntityWithAccessionedSequence{speciesName:"Homo sapiens"}) where "%s" in n.name and "%s" in n2.name  return n,r,n2,path'
    return (cypher % (gene,gene))

def node_finder_clause_by_gene(gene):
    cypher = 'match (n:ReferenceEntity) where "%s" in n.name return n'
    return (cypher % (gene,gene))

def node_finder_clause_by_transcript(transcript_id):
    template = "MATCH (n:ReferenceEntity)<-[r1:referenceEntity]-(re:EntityWithAccessionedSequence{speciesName:'Homo sapiens'}) where ('%s' in n.otherIdentifier) with n,r1,re" 
    return template % transcript_id

def pathway_query_from_initial_match_clause(init_clause):
    Pathways_main_part = """MATCH (n)<-[r1:referenceEntity]-(re:EntityWithAccessionedSequence{speciesName:'Homo sapiens'}) \
        with n,r1,re \
        MATCH path1=(re:EntityWithAccessionedSequence{speciesName:'Homo sapiens'})<-[r:input|output|catalystActivity|physicalEntity|regulatedBy|regulator|hasComponent|hasMember|hasCandidate*]-(c) \
        with re,r,c,r1,n,path1 \
        MATCH path2=(p:TopLevelPathway{displayName:'Disease'})-[e:hasEvent*]->(c) \
        with nodes(path2) as pns unwind(pns) as pn with pn MATCH (pn:Pathway) return distinct  pn""" #re,r,c,p,e,r1
    #strange, filtering by disease seems reasonable but if do so loose tp53 matches
    return ("%s\n%s" % (init_clause, Pathways_main_part))

def pathway_interrelatinships_query_from_initial_match_clause(init_clause):
    Pathways_main_part = """MATCH (n)<-[r1:referenceEntity]-(re:EntityWithAccessionedSequence{speciesName:'Homo sapiens'}) \
        with n,r1,re \
        MATCH path1=(re:EntityWithAccessionedSequence{speciesName:'Homo sapiens'})<-[r:input|output|catalystActivity|physicalEntity|regulatedBy|regulator|hasComponent|hasMember|hasCandidate*]-(c) \
        with re,r,c,r1,n,path1 \
        MATCH path2=(p:TopLevelPathway{displayName:'Disease'})-[e:hasEvent*]->(c) return path2"""
        
    #strange, filtering by disease seems reasonable but if do so loose tp53 matches
    return ("%s\n%s" % (init_clause, Pathways_main_part))

def pathways_by_transcript_list(transcript_ids):
    
    return pathway_query_from_initial_match_clause(subgraph_by_transcript_ids(transcript_ids, True))
    

def pathways_by_transcript_id(transcript_id):

    return pathway_query_from_initial_match_clause(node_finder_clause_by_transcript(transcript_id))
    
def pathways_by_gene_list(genes):
    
    return pathway_query_from_initial_match_clause(subgraph_by_genes(genes, True))
    
def pathway_interrelatinships_query_from_initial_match_clause(genes):
    
    return pathway_query_from_initial_match_clause(subgraph_by_genes(genes, True))

#class ReactomeQuery():
    
    #hmmm way too broad, but why? not sure yet. 

#     MATCH (n:ReferenceEntity)<-[r1:referenceEntity]-(re{speciesName:'Homo sapiens'}) where ('PIK3R1' in n.name) 
# with re,r1,n 
# MATCH path1=(re)<-[r:input|output|catalystActivity|physicalEntity|regulatedBy|regulator|hasComponent|hasMember|hasCandidate*]-(c)
# with re,r,c,r1,n,path1 
# MATCH path2=(p:Pathway)-[e:hasEvent*]->(c)
# return re,r,c,p,e,r1,n,path1,path2 limit 1000


class PathwayMatrixByGenes():
    def __init__(self, gene_list):
        self.gene_list = gene_list

    def test():
        x = PathwayMatrixByGenes([])
        x.load_from_ngsreporter('18-138-14853')
        print(x.gene_list)
        assert x.number_pathogenic == 1
        assert len(x.gene_list) == 6
        print(x.gene_list)

    def load_from_ngsreporter(self,accession_number):
        log.debug("begin load_from_ngsreporter %s" % accession_number)
        r = requests.get("https://ngsreporter.mgl.providence.org/api_get_report_json/%s" % accession_number, auth=(os.environ['REPORTERUNAME'], os.environ['REPORTERPWD']),  verify=False)
        r = r.json()
        log.debug(r)
        log.debug("genomics_alterations_pathogenic")
        log.debug(r["genomics_alterations_pathogenic"])
        log.debug("genomics_alterations_unknown_significance")
        log.debug(r["genomics_alterations_unknown_significance"])
        pathogenic = r["genomics_alterations_pathogenic"].split("\n")
        vus = r["genomics_alterations_unknown_significance"].split("\n")
        self.number_pathogenic = len(pathogenic)
        all_variants = pathogenic + vus
        genes = [x.strip().split(" ")[0] for x in all_variants]
        self.gene_list = genes
        log.debug("reached end of load_from_ngsreporter")

    def build_matrix(self, path = ""):
        log.debug("begin build_matrix dubeg")
        results = {}
        pathway_data = defaultdict(list)
        pathway_genes = defaultdict(list)
        gene_pathways =  {gene:[] for gene in self.gene_list}

        log.debug("Count of self.gene_list=%i" % len(self.gene_list))
        for gene in self.gene_list:
            log.info("about to run pathways_by_gene_list for %s" % gene )
            pathways = runquery(pathways_by_gene_list([gene]))
            log.info("ran it, len pathways is %i" % len(pathways))
            results[gene] = pathways
            
            for row in pathways:
                for node in row:
                    node_id = node['stId']
                    pathway_data[node_id] = node                    
                    pathway_genes[node_id].append(gene)
                    gene_pathways[gene].append(node_id)
                        
        self.pathway_data = pathway_data
        self.pathway_genes = pathway_genes
        self.gene_pathways = gene_pathways

        self.matrix = self.matrix_pathways_by_genes()

        if len(path)>0:
            self.save_matrix(path)

        return self.matrix

    def build_matrix_of_pathway_relationships(self):
        print("coming")
        
    def to_json(self):
        gene_nodes =[{"id":x, "type":"gene"} for x in self.matrix[0][1:-2] if x!=''] 

        fake_division_between_pathogenic_and_vus = int(len(gene_nodes)/2)

        for i in range(0, len(gene_nodes)):
            if i < fake_division_between_pathogenic_and_vus:

                classification="pathogenic"
            else:
                classification = "unknown"
            gene_nodes[i]["classification"] = classification
            
        pathway_nodes =[{"id":x[0],"type":"pathway"} for x in self.matrix[:] if x!=''] 
        nodes = gene_nodes + pathway_nodes
        edges = []        
        for ridx in range(1,len(self.matrix)):
            row = self.matrix[ridx]
            for cidx in range(1, len(row)-1):
                cell_value = row[cidx]
                if cell_value == 1:
                    edge = {"source":row[0], "target":self.matrix[0][cidx]}
                    edges.append(edge)

        pathway_edges = self.pathway_interrelationships()

        # for rel in pathway_edges:
        #     edge = {"source":rel[0], "target":rel[1]}
        #     edges.append(edge)


        result_object = {"nodes":nodes, "links":edges}

        result_object = self.remove_orphan_edges(result_object)

        return json.dumps(result_object)

    def remove_orphan_edges(self, result_object):
        nodes = result_object["nodes"]
        nodes_by_id = {x['id']:True for x in nodes}
        new_edges = []
        for edge in result_object["links"]:
            if edge['source'] in nodes_by_id and edge['target'] in nodes_by_id:
                new_edges.append(edge)
        return {"nodes":nodes, "links":new_edges}


    def pathway_interrelationships(self):
        ids = ",".join([str(n.id) for k,n in self.pathway_data.items()])
        cy = "MATCH path=()-[:hasEvent]->(n) where id(n) in [%s] return path;" % ids
        g = runquery_asgraph(cy)
        #v =r.values()
        #g = r.graph()
        #generate tuples of from node node, to node name, 
        endpoints = [[n.start_node['displayName'],n.end_node['displayName']]  for n in g.relationships]
        return endpoints


    def matrix_pathways_by_genes(self):        
        gene_keys = self.gene_pathways.keys()
        matrix = []
        header_row = ['Pathway'] + [g for g in gene_keys] + ['Count']
        matrix.append(header_row)
        for k,v in self.pathway_genes.items():
            values = [1 if pk in v else 0 for  pk in gene_keys]
            matrix_row = [self.pathway_data[k]['displayName']] + values + [sum(values)]
            matrix.append(matrix_row)
        return matrix

    def matrix_genes_by_pathways(self):
        pathway_keys = self.pathway_data.keys()
        matrix = []
        header_row = ['Gene'] + [self.pathway_data[pk]['name'] for pk in pathway_keys ]
        matrix.append(header_row)
        for k,v in self.gene_pathways.items():
            matrix_row = [k] + [1 if pk in v else 0 for  pk in pathway_keys]
            matrix.append(matrix_row)
        return matrix

    def summarize(self):
        print("Total pathways found: %i" % len(self.pathway_data.keys()))

        for k,v in self.gene_pathways.items():
            print("Gene %s: %i pathways" % (k,len(v)))

    def save_matrix(self,path):
        with open(path,"w") as f:
            writer = csv.writer(f)
            for row in self.matrix:
                writer.writerow(row)                

def runquery(cyphertext):
    return ReactomeConnector().runquery(cyphertext)

def runqueryraw(cyphertext):
    return ReactomeConnector().runqueryraw(cyphertext)

def runquery_asgraph(cyphertext):
    return ReactomeConnector().runqueryraw_asgraph(cyphertext)

#print(runquery(pathways_by_gene_list(['PIK3R1']))) 
#x = runquery(pathways_by_gene_list(['PIK3R1']))
#n_ids = [r[6].id for r in x]

spacer = "------------------------------"

def dostuff():
    spacer = "------------------------------"
    
    transcript_path = "data/config_panels_transcripts.yaml"

    with open(transcript_path) as f:
        transcripts = yaml.load(f)

    tst170 = transcripts['tst170']
    cypher_list ="['%s']" % "','".join(tst170.values())
    cypher = "match (n) where size([x IN %s | x in n.otherIdentifier]) >0 return n" % cypher_list
    #match (n:EntityWithAccessionedSequence) where size([x IN ['NM_005157','NM_001014432','NM_001626','NM_005465','NM_004304','NM_000038','NM_000044','NM_006015','NM_000051','NM_001184','NM_001699','NM_004656','NM_000465','NM_000633','NM_001706','NM_004333','NM_007294','NM_000059','NM_032043','NM_000061','NM_032415','NM_053056','NM_001759','NM_001760','NM_001238','NM_001783','NM_000626','NM_004360','NM_016507','NM_000075','NM_001259','NM_000077','NM_004364','NM_001114122','NM_007194','NM_004380','NM_005211','NM_001904','NM_001014796','NM_022552','NM_005228','NM_019063','NM_001429','NM_004448','NM_001982','NM_005235','NM_202001','NM_000400','NM_004449','NM_001122742','NM_005238','NM_004956','NM_001079675','NM_004454','NM_005243','NM_004456','NM_139076','NM_001113378','NM_018062','NM_033632','NM_001144892','NM_004465','NM_175929','NM_005117','NM_002006','NM_020638','NM_005247','NM_002007','NM_004464','NM_020996','NM_002009','NM_033163','NM_002010','NM_023110','NM_000141','NM_000142','NM_022963','NM_002017','NM_002019','NM_004119','NM_023067','NM_182625','NM_002067','NM_002072','NM_000516','NM_000545','NM_005343','NM_005896','NM_002168','NM_003866','NM_004972','NM_000215','NM_002253','NM_004521','NM_000222','NM_005933','NM_004985','NM_005561','NM_002755','NM_030662','NM_021960','NM_002392','NM_002393','NM_001127500','NM_000249','NM_004529','NM_005373','NM_005590','NM_000251','NM_002439','NM_000179','NM_004958','NM_012222','NM_002467','NM_001033082','NM_005378','NM_002468','NM_002485','NM_001042492','NM_017617','NM_024408','NM_000435','NM_002520','NM_002524','NM_013957','NM_002529','NM_006180','NM_002530','NM_024675','NM_181459','NM_002584','NM_006206','NM_002609','NM_006218','NM_006219','NM_005026','NM_001282427','NM_181523','NM_000535','NM_015869','NM_002717','NM_000264','NM_000314','NM_002834','NM_002875','NM_133509','NM_058216','NM_002878','NM_003579','NM_002880','NM_000321','NM_020975','NM_152756','NM_002944','NM_001272060','NM_032444','NM_005359','NM_003073','NM_005631','NM_005417','NM_000455','NM_198253','NM_001127208','NM_001128148','NM_005656','NM_000546','NM_000368','NM_000548','NM_000551','NM_005431'] | x in n.otherIdentifier]) >0 return n.stId, n.otherIdentifier
    print(cypher)

    #note: do not filter by n.speciesName for these, it doesn't seem to exist as a key on the nodes that we are looking for

    cypher_list ="(('%s' in n.otherIdentifier))" % "' in n.otherIdentifier) or ('".join(tst170.values())
    cypher = "match (n) where %s return n.stId, n.otherIdentifier" % cypher_list
    print(cypher)

    cypher = "match (n) where %s return n" % cypher_list
    print(cypher)


    #  match (n:EntityWithAccessionedSequence) where n.speciesName='Homo sapiens' and size([x IN ['NM_005157','NM_001014432','NM_001626','NM_005465','NM_004304','NM_000038','NM_000044','NM_006015','NM_000051','NM_001184','NM_001699','NM_004656','NM_000465','NM_000633','NM_001706','NM_004333','NM_007294','NM_000059','NM_032043','NM_000061','NM_032415','NM_053056','NM_001759','NM_001760','NM_001238','NM_001783','NM_000626','NM_004360','NM_016507','NM_000075','NM_001259','NM_000077','NM_004364','NM_001114122','NM_007194','NM_004380','NM_005211','NM_001904','NM_001014796','NM_022552','NM_005228','NM_019063','NM_001429','NM_004448','NM_001982','NM_005235','NM_202001','NM_000400','NM_004449','NM_001122742','NM_005238','NM_004956','NM_001079675','NM_004454','NM_005243','NM_004456','NM_139076','NM_001113378','NM_018062','NM_033632','NM_001144892','NM_004465','NM_175929','NM_005117','NM_002006','NM_020638','NM_005247','NM_002007','NM_004464','NM_020996','NM_002009','NM_033163','NM_002010','NM_023110','NM_000141','NM_000142','NM_022963','NM_002017','NM_002019','NM_004119','NM_023067','NM_182625','NM_002067','NM_002072','NM_000516','NM_000545','NM_005343','NM_005896','NM_002168','NM_003866','NM_004972','NM_000215','NM_002253','NM_004521','NM_000222','NM_005933','NM_004985','NM_005561','NM_002755','NM_030662','NM_021960','NM_002392','NM_002393','NM_001127500','NM_000249','NM_004529','NM_005373','NM_005590','NM_000251','NM_002439','NM_000179','NM_004958','NM_012222','NM_002467','NM_001033082','NM_005378','NM_002468','NM_002485','NM_001042492','NM_017617','NM_024408','NM_000435','NM_002520','NM_002524','NM_013957','NM_002529','NM_006180','NM_002530','NM_024675','NM_181459','NM_002584','NM_006206','NM_002609','NM_006218','NM_006219','NM_005026','NM_001282427','NM_181523','NM_000535','NM_015869','NM_002717','NM_000264','NM_000314','NM_002834','NM_002875','NM_133509','NM_058216','NM_002878','NM_003579','NM_002880','NM_000321','NM_020975','NM_152756','NM_002944','NM_001272060','NM_032444','NM_005359','NM_003073','NM_005631','NM_005417','NM_000455','NM_198253','NM_001127208','NM_001128148','NM_005656','NM_000546','NM_000368','NM_000548','NM_000551','NM_005431'] | x in n.otherIdentifier]) >0 return n.stID, n.otherIdentifier


    #match (n:EntityWithAccessionedSequence) where n.speciesName='Homo sapiens' and size([x IN ['NM_005157','NM_001014432','NM_001626','NM_005465','NM_004304','NM_000038','NM_000044','NM_006015','NM_000051','NM_001184','NM_001699','NM_004656','NM_000465','NM_000633','NM_001706','NM_004333','NM_007294','NM_000059','NM_032043','NM_000061','NM_032415','NM_053056','NM_001759','NM_001760','NM_001238','NM_001783','NM_000626','NM_004360','NM_016507','NM_000075','NM_001259','NM_000077','NM_004364','NM_001114122','NM_007194','NM_004380','NM_005211','NM_001904','NM_001014796','NM_022552','NM_005228','NM_019063','NM_001429','NM_004448','NM_001982','NM_005235','NM_202001','NM_000400','NM_004449','NM_001122742','NM_005238','NM_004956','NM_001079675','NM_004454','NM_005243','NM_004456','NM_139076','NM_001113378','NM_018062','NM_033632','NM_001144892','NM_004465','NM_175929','NM_005117','NM_002006','NM_020638','NM_005247','NM_002007','NM_004464','NM_020996','NM_002009','NM_033163','NM_002010','NM_023110','NM_000141','NM_000142','NM_022963','NM_002017','NM_002019','NM_004119','NM_023067','NM_182625','NM_002067','NM_002072','NM_000516','NM_000545','NM_005343','NM_005896','NM_002168','NM_003866','NM_004972','NM_000215','NM_002253','NM_004521','NM_000222','NM_005933','NM_004985','NM_005561','NM_002755','NM_030662','NM_021960','NM_002392','NM_002393','NM_001127500','NM_000249','NM_004529','NM_005373','NM_005590','NM_000251','NM_002439','NM_000179','NM_004958','NM_012222','NM_002467','NM_001033082','NM_005378','NM_002468','NM_002485','NM_001042492','NM_017617','NM_024408','NM_000435','NM_002520','NM_002524','NM_013957','NM_002529','NM_006180','NM_002530','NM_024675','NM_181459','NM_002584','NM_006206','NM_002609','NM_006218','NM_006219','NM_005026','NM_001282427','NM_181523','NM_000535','NM_015869','NM_002717','NM_000264','NM_000314','NM_002834','NM_002875','NM_133509','NM_058216','NM_002878','NM_003579','NM_002880','NM_000321','NM_020975','NM_152756','NM_002944','NM_001272060','NM_032444','NM_005359','NM_003073','NM_005631','NM_005417','NM_000455','NM_198253','NM_001127208','NM_001128148','NM_005656','NM_000546','NM_000368','NM_000548','NM_000551','NM_005431'] | x in n.otherIdentifier]) >0 return n.stID, n.otherIdentifier,size(filter(y in  [x IN ['NM_005157','NM_001014432','NM_001626','NM_005465','NM_004304','NM_000038','NM_000044','NM_006015','NM_000051','NM_001184','NM_001699','NM_004656','NM_000465','NM_000633','NM_001706','NM_004333','NM_007294','NM_000059','NM_032043','NM_000061','NM_032415','NM_053056','NM_001759','NM_001760','NM_001238','NM_001783','NM_000626','NM_004360','NM_016507','NM_000075','NM_001259','NM_000077','NM_004364','NM_001114122','NM_007194','NM_004380','NM_005211','NM_001904','NM_001014796','NM_022552','NM_005228','NM_019063','NM_001429','NM_004448','NM_001982','NM_005235','NM_202001','NM_000400','NM_004449','NM_001122742','NM_005238','NM_004956','NM_001079675','NM_004454','NM_005243','NM_004456','NM_139076','NM_001113378','NM_018062','NM_033632','NM_001144892','NM_004465','NM_175929','NM_005117','NM_002006','NM_020638','NM_005247','NM_002007','NM_004464','NM_020996','NM_002009','NM_033163','NM_002010','NM_023110','NM_000141','NM_000142','NM_022963','NM_002017','NM_002019','NM_004119','NM_023067','NM_182625','NM_002067','NM_002072','NM_000516','NM_000545','NM_005343','NM_005896','NM_002168','NM_003866','NM_004972','NM_000215','NM_002253','NM_004521','NM_000222','NM_005933','NM_004985','NM_005561','NM_002755','NM_030662','NM_021960','NM_002392','NM_002393','NM_001127500','NM_000249','NM_004529','NM_005373','NM_005590','NM_000251','NM_002439','NM_000179','NM_004958','NM_012222','NM_002467','NM_001033082','NM_005378','NM_002468','NM_002485','NM_001042492','NM_017617','NM_024408','NM_000435','NM_002520','NM_002524','NM_013957','NM_002529','NM_006180','NM_002530','NM_024675','NM_181459','NM_002584','NM_006206','NM_002609','NM_006218','NM_006219','NM_005026','NM_001282427','NM_181523','NM_000535','NM_015869','NM_002717','NM_000264','NM_000314','NM_002834','NM_002875','NM_133509','NM_058216','NM_002878','NM_003579','NM_002880','NM_000321','NM_020975','NM_152756','NM_002944','NM_001272060','NM_032444','NM_005359','NM_003073','NM_005631','NM_005417','NM_000455','NM_198253','NM_001127208','NM_001128148','NM_005656','NM_000546','NM_000368','NM_000548','NM_000551','NM_005431'] | x in n.otherIdentifier] where y is not null )) as theSize


    #match (n:EntityWithAccessionedSequence) where n.speciesName='Homo sapiens' and size(filter(y in  [x IN ['NM_005157','NM_001014432','NM_001626','NM_005465','NM_004304','NM_000038','NM_000044','NM_006015','NM_000051','NM_001184','NM_001699','NM_004656','NM_000465','NM_000633','NM_001706','NM_004333','NM_007294','NM_000059','NM_032043','NM_000061','NM_032415','NM_053056','NM_001759','NM_001760','NM_001238','NM_001783','NM_000626','NM_004360','NM_016507','NM_000075','NM_001259','NM_000077','NM_004364','NM_001114122','NM_007194','NM_004380','NM_005211','NM_001904','NM_001014796','NM_022552','NM_005228','NM_019063','NM_001429','NM_004448','NM_001982','NM_005235','NM_202001','NM_000400','NM_004449','NM_001122742','NM_005238','NM_004956','NM_001079675','NM_004454','NM_005243','NM_004456','NM_139076','NM_001113378','NM_018062','NM_033632','NM_001144892','NM_004465','NM_175929','NM_005117','NM_002006','NM_020638','NM_005247','NM_002007','NM_004464','NM_020996','NM_002009','NM_033163','NM_002010','NM_023110','NM_000141','NM_000142','NM_022963','NM_002017','NM_002019','NM_004119','NM_023067','NM_182625','NM_002067','NM_002072','NM_000516','NM_000545','NM_005343','NM_005896','NM_002168','NM_003866','NM_004972','NM_000215','NM_002253','NM_004521','NM_000222','NM_005933','NM_004985','NM_005561','NM_002755','NM_030662','NM_021960','NM_002392','NM_002393','NM_001127500','NM_000249','NM_004529','NM_005373','NM_005590','NM_000251','NM_002439','NM_000179','NM_004958','NM_012222','NM_002467','NM_001033082','NM_005378','NM_002468','NM_002485','NM_001042492','NM_017617','NM_024408','NM_000435','NM_002520','NM_002524','NM_013957','NM_002529','NM_006180','NM_002530','NM_024675','NM_181459','NM_002584','NM_006206','NM_002609','NM_006218','NM_006219','NM_005026','NM_001282427','NM_181523','NM_000535','NM_015869','NM_002717','NM_000264','NM_000314','NM_002834','NM_002875','NM_133509','NM_058216','NM_002878','NM_003579','NM_002880','NM_000321','NM_020975','NM_152756','NM_002944','NM_001272060','NM_032444','NM_005359','NM_003073','NM_005631','NM_005417','NM_000455','NM_198253','NM_001127208','NM_001128148','NM_005656','NM_000546','NM_000368','NM_000548','NM_000551','NM_005431'] | x in n.otherIdentifier] where y is not null )) >0 return n.stID, n.otherIdentifier,size(filter(y in  [x IN ['NM_005157','NM_001014432','NM_001626','NM_005465','NM_004304','NM_000038','NM_000044','NM_006015','NM_000051','NM_001184','NM_001699','NM_004656','NM_000465','NM_000633','NM_001706','NM_004333','NM_007294','NM_000059','NM_032043','NM_000061','NM_032415','NM_053056','NM_001759','NM_001760','NM_001238','NM_001783','NM_000626','NM_004360','NM_016507','NM_000075','NM_001259','NM_000077','NM_004364','NM_001114122','NM_007194','NM_004380','NM_005211','NM_001904','NM_001014796','NM_022552','NM_005228','NM_019063','NM_001429','NM_004448','NM_001982','NM_005235','NM_202001','NM_000400','NM_004449','NM_001122742','NM_005238','NM_004956','NM_001079675','NM_004454','NM_005243','NM_004456','NM_139076','NM_001113378','NM_018062','NM_033632','NM_001144892','NM_004465','NM_175929','NM_005117','NM_002006','NM_020638','NM_005247','NM_002007','NM_004464','NM_020996','NM_002009','NM_033163','NM_002010','NM_023110','NM_000141','NM_000142','NM_022963','NM_002017','NM_002019','NM_004119','NM_023067','NM_182625','NM_002067','NM_002072','NM_000516','NM_000545','NM_005343','NM_005896','NM_002168','NM_003866','NM_004972','NM_000215','NM_002253','NM_004521','NM_000222','NM_005933','NM_004985','NM_005561','NM_002755','NM_030662','NM_021960','NM_002392','NM_002393','NM_001127500','NM_000249','NM_004529','NM_005373','NM_005590','NM_000251','NM_002439','NM_000179','NM_004958','NM_012222','NM_002467','NM_001033082','NM_005378','NM_002468','NM_002485','NM_001042492','NM_017617','NM_024408','NM_000435','NM_002520','NM_002524','NM_013957','NM_002529','NM_006180','NM_002530','NM_024675','NM_181459','NM_002584','NM_006206','NM_002609','NM_006218','NM_006219','NM_005026','NM_001282427','NM_181523','NM_000535','NM_015869','NM_002717','NM_000264','NM_000314','NM_002834','NM_002875','NM_133509','NM_058216','NM_002878','NM_003579','NM_002880','NM_000321','NM_020975','NM_152756','NM_002944','NM_001272060','NM_032444','NM_005359','NM_003073','NM_005631','NM_005417','NM_000455','NM_198253','NM_001127208','NM_001128148','NM_005656','NM_000546','NM_000368','NM_000548','NM_000551','NM_005431'] | x in n.otherIdentifier] where y is not null )) as theSize


        #     better:

    #     MATCH (n:ReferenceEntity)<-[r:referenceEntity]-(re) where ('NM_001127208' in n.otherIdentifier) 
    # with re
    # MATCH (re)<-[r:input|output|catalystActivity|physicalEntity|regulatedBy|regulator|hasComponent|hasMember|hasCandidate*]-(c)
    # return re,r,c
    #sample case:
    #'19-078-11239'
    case_transcripts = ["NM_001127208", "NM_001127208", "NM_032458", "NM_032458", "NM_015338", "NM_032458", "NM_032458", "NM_032458"]
    # x = r('19-078-11239')
    # x.variant_calls.map {|v| v.gene_name}.uniq
    case_genes=["TET2", "PHF6", "ASXL1"]

    #of those the only ones that actually match in reactome are:
    case_transcripts = ['NM_001127208' ,'NM_015338']



    
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
    def __init__(self, uri="bolt://neo4j:7687",user='neo4j',password = os.environ['REACTOME_PWD']):
        log.info("about to try to connect to %s with u=%s and pwd=%s" % ( uri, user, password))
        self._driver = GraphDatabase.driver(uri, auth=(user, password))
        self._session = self._driver.session()
        log.info("Reached end of ReactomeConnector.__init__")

    def runquery(self, cyphertext):
        log.debug("begin plain 'runquery' method")
        result = self.runqueryraw(cyphertext)
        results = result.values()
        log.debug("Finished query, %i values" % len(results) )
        return results

    def runqueryraw(self, cyphertext):
        log.debug("About to run query:")
        log.debug(cyphertext)
        r = self._session.run(cyphertext)
        log.debug("finished query")        
        return r

    def runqueryraw_asgraph(self, cyphertext):
        return self.runqueryraw().graph()

#REACTOME = ReactomeConnector()

if __name__ == "__main__":    
    dostuff()    
    user='neo4j'
    password = 'reactome'
    password = os.environ['REACTOME_PWD']
    uri="bolt://0.0.0.0:7687"
    driver = GraphDatabase.driver(uri, auth=(user, password))
    sess = driver.session()
