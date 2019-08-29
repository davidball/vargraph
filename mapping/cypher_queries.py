def subgraph_by_transcript_ids(transcript_ids, with_statement=False):
    cypher_list = "(('%s' in n.otherIdentifier))" % "' in n.otherIdentifier) or ('".join(
        transcript_ids)
    cypher = "match (n:ReferenceGeneProduct) where %s %s n" % (
        cypher_list, ("WITH" if with_statement else "RETURN"))
    return cypher


def subgraph_by_genes(genes, with_statement=False):
    cypher_list = "(('%s' in n.otherIdentifier))" % "' in n.otherIdentifier) or ('".join(
        genes)
    cypher = "match (n:ReferenceGeneProduct) where %s %s n" % (
        cypher_list, ("WITH" if with_statement else "RETURN"))
    return cypher


def subgraph_by_transcript_ids_with_neighbors(transcript_ids):
    # note: filtering out species relationship as it is noise
    cypher_list = "(('%s' in n.otherIdentifier))" % "' in n.otherIdentifier) or ('".join(
        transcript_ids)
    cypher = "match (n)-[r]-(anyneighbor) where not (n)-[r:species]-(anyneighbor) and %s return n, anyneighbor" % cypher_list
    return cypher


def subgraph_by_transcript_ids_with_neighbors_two_deep(transcript_ids):
    # note: filtering out species relationship as it is noise
    cypher_list = "(('%s' in n.otherIdentifier))" % "' in n.otherIdentifier) or ('".join(
        transcript_ids)
    cypher = "match (n)-[r]-(anyneighbor)-[r2]-(n2) where not (anyneighbor:ReferenceDatabase) and not (n2:ReferenceDatabase) and not (anyneighbor:InstanceEdit) and not (n:InstanceEdit) and not (n2:InstanceEdit) and not (n)-[r:species]-(anyneighbor) and not (anyneighbor)-[r2:species]-(n2) and %s return n, anyneighbor,n2" % cypher_list
    return cypher


def subgraph_by_transcript_ids_with_neighbors_three_deep(transcript_ids):
    # note: filtering out species relationship as it is noise
    cypher_list = "(('%s' in n.otherIdentifier))" % "' in n.otherIdentifier) or ('".join(
        transcript_ids)
    cypher = "match (n)-[r]-(anyneighbor)-[r2]-(n2)-[r3]-(n3) where not (anyneighbor:ReferenceDatabase) and not (n2:ReferenceDatabase) and not (anyneighbor:InstanceEdit) and not (n:InstanceEdit) and not (n2:InstanceEdit) and not (n3:InstanceEdit) and not (n3:ReferenceDatabase) and not (n)-[r:species]-(anyneighbor) and not (n3:Species) and not (anyneighbor)-[r2:species]-(n2) and %s return n, anyneighbor,n2,n3" % cypher_list
    return cypher


def layer_filter_clause(layer_node_alias):
    exclude_node_types = [
        'Species',
        'Compartment',
        'ReferenceDatabase',
        'InstanceEdit'
    ]

    filter_list_template = 'not (%s:' + \
        ') and not (%s:'.join(exclude_node_types) + ')'

    layer_node_filter = filter_list_template % (
        (layer_node_alias,) * len(exclude_node_types))
    return layer_node_filter


def layer_clause(from_node_alias, to_node_alias):
    return "MATCH (%s)-[r]-(%s) where %s" % (from_node_alias, to_node_alias, layer_filter_clause(to_node_alias))


def subgraph_by_transcript_ids_using_with(transcript_ids, depth=3):
    # note: filtering out species relationship as it is noise

    cypher_list = "(('%s' in n.otherIdentifier))" % "' in n.otherIdentifier) or ('".join(
        transcript_ids)
    # cypher = "match (n)-[r]-(anyneighbor)-[r2]-(n2)-[r3]-(n3) where not (anyneighbor:ReferenceDatabase) and not (n2:ReferenceDatabase) and not (anyneighbor:InstanceEdit) and not (n:InstanceEdit) and not (n2:InstanceEdit) and not (n3:InstanceEdit) and not (n3:ReferenceDatabase) and not (n)-[r:species]-(anyneighbor) and not (n3:Species) and not (anyneighbor)-[r2:species]-(n2) and %s return n, anyneighbor,n2,n3" % cypher_list

    cypher_variant_filter = "MATCH (n) where %s \nwith n" % cypher_list

    cypher = cypher_variant_filter + "\n" + \
        layer_clause('n', 'n2') + \
        "\nWITH n,n2\n" + \
        layer_clause('n2', 'n3') + \
        "\nWITH n,n2,n3\n" + \
        layer_clause('n3', 'n4') + \
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


# wow
# MATCH (n:ReferenceEntity)<-[r1:referenceEntity]-(re) where ('NM_001127208' in n.otherIdentifier)
# with re,r1,n
# MATCH path1=(re)<-[r:input|output|catalystActivity|physicalEntity|regulatedBy|regulator|hasComponent|hasMember|hasCandidate*]-(c)
# with re,r,c,r1,n,path1
# MATCH path2=(p:Pathway)-[e:hasEvent*]->(c)
# return re,r,c,p,e,r1,n,path1,path2


def finding_by_gene_experiment(gene):
    cypher = 'match path=(n:EntityWithAccessionedSequence{speciesName:"Homo sapiens"})-[r*0..2]-(n2:EntityWithAccessionedSequence{speciesName:"Homo sapiens"}) where "%s" in n.name and "%s" in n2.name  return n,r,n2,path'
    return (cypher % (gene, gene))


def node_finder_clause_by_gene(gene):
    cypher = 'match (n:ReferenceEntity) where "%s" in n.name return n'
    return (cypher % (gene, gene))


def node_finder_clause_by_transcript(transcript_id):
    template = "MATCH (n:ReferenceEntity)<-[r1:referenceEntity]-(re:EntityWithAccessionedSequence{speciesName:'Homo sapiens'}) where ('%s' in n.otherIdentifier) with n,r1,re"
    return template % transcript_id


def pathway_query_from_initial_match_clause(init_clause):
    Pathways_main_part = """MATCH (n)<-[r1:referenceEntity]-(re:EntityWithAccessionedSequence{speciesName:'Homo sapiens'}) \
        with n,r1,re \
        MATCH path1=(re:EntityWithAccessionedSequence{speciesName:'Homo sapiens'})<-[r:input|output|catalystActivity|physicalEntity|regulatedBy|regulator|hasComponent|hasMember|hasCandidate*]-(c) \
        with re,r,c,r1,n,path1 \
        MATCH path2=(p:TopLevelPathway{displayName:'Disease'})-[e:hasEvent*]->(c) \
        with nodes(path2) as pns unwind(pns) as pn with pn MATCH (pn:Pathway) return distinct  pn"""  # re,r,c,p,e,r1
    # strange, filtering by disease seems reasonable but if do so loose tp53 matches
    return ("%s\n%s" % (init_clause, Pathways_main_part))


def pathway_interrelatinships_query_from_initial_match_clause(init_clause):
    Pathways_main_part = """MATCH (n)<-[r1:referenceEntity]-(re:EntityWithAccessionedSequence{speciesName:'Homo sapiens'}) \
        with n,r1,re \
        MATCH path1=(re:EntityWithAccessionedSequence{speciesName:'Homo sapiens'})<-[r:input|output|catalystActivity|physicalEntity|regulatedBy|regulator|hasComponent|hasMember|hasCandidate*]-(c) \
        with re,r,c,r1,n,path1 \
        MATCH path2=(p:TopLevelPathway{displayName:'Disease'})-[e:hasEvent*]->(c) return path2"""

    # strange, filtering by disease seems reasonable but if do so loose tp53 matches
    return ("%s\n%s" % (init_clause, Pathways_main_part))


def pathways_by_transcript_list(transcript_ids):

    return pathway_query_from_initial_match_clause(subgraph_by_transcript_ids(transcript_ids, True))


def pathways_by_transcript_id(transcript_id):

    return pathway_query_from_initial_match_clause(node_finder_clause_by_transcript(transcript_id))


def pathways_by_gene_list(genes):

    return pathway_query_from_initial_match_clause(subgraph_by_genes(genes, True))


def pathway_interrelatinships_query_from_initial_match_clause(genes):

    return pathway_query_from_initial_match_clause(subgraph_by_genes(genes, True))
