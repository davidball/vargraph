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
import mapping.mapping_by_transcript as mt
import mapping.cypher_queries as cypher

log = mt.log


class PathwayMatrixByGenes():
    def __init__(self, gene_list=[]):
        self._matrix_loaded = False
        self._json_loaded = False
        self.accession_number = ''
        self.number_pathogenic = 0
        self.gene_list = gene_list

    def test():
        x = PathwayMatrixByGenes([])
        x.load_from_ngsreporter('18-138-14853')
        print(x.gene_list)
        assert x.number_pathogenic == 1
        assert len(x.gene_list) == 6
        print(x.gene_list)

    def reporter_variant_list_to_genes(self, reporter_results, fldname):

        if fldname in reporter_results:
            val = reporter_results[fldname]
            if val:
                all = val.split("\n")
                return [x.strip().split(" ")[0].strip() for x in all]
            else:
                return []
        else:
            return []

    def cache_json_file_name(self, accn=''):
        if accn == '':
            accn = self.accession_number
        if len(accn) == 0:
            raise Exception(
                "Can not generate cache_json_file_name due to no accession_number provided")
        return "accession_json_cache/%s.json" % accn.replace('.', '_').replace('/', '_')

    def cache_matrix_file_name(self, accn=''):
        if accn == '':
            accn = self.accession_number
        return (self.cache_json_file_name(accn) + ".matrix.csv")

    def load_from_cache(self, accession_number):
       # try:
        json_filename = self.cache_json_file_name(accession_number)
        matrix_filename = self.cache_matrix_file_name(accession_number)
        self.pathway_data = None
        log.info("expected cache file names:\n\t%s\n\t%s" %
                 (json_filename, matrix_filename))
        if os.path.exists(json_filename) and os.path.exists(matrix_filename):
            log.info("found in cache, skip building matrix")
            with open(json_filename, 'r') as f:
                accn_json = "\n".join(f.readlines())
                parsed = json.loads(accn_json)
                if "number_pathogenic" in parsed:
                    self.number_pathogenic = parsed['number_pathogenic']
                else:
                    self.number_pathogenic = 0
                if "pathway_data" in parsed:
                    self.pathway_data = parsed['pathway_data']
                self._json = accn_json
                self._json_loaded = True
            self.read_matrix(matrix_filename)

            log.info("Successfully loaded from cache")
            return True
        else:
            log.info("%s is not in cache" % accession_number)
            return False
        # except:
        #     log.error('Error loading %s from cache' % accession_number)
        #     return False

    def reset_state(self):
        self._json_loaded = False
        self._json = False
        self._matrix_loaded = False
        self.matrix = None

    def load_from_ngsreporter(self, accession_number, allow_cache_read=True):
        log.debug("begin load_from_ngsreporter %s" % accession_number)

        self.reset_state

        self.accession_number = accession_number

        if allow_cache_read:
            log.info("Checking cache")
            if self.load_from_cache(accession_number):
                log.info("Found in cache, nothing to do.")
                return
        else:
            log.info("Checking cache not allowed")

        url = "https://ngsreporter.mgl.providence.org/api_get_report_json/%s" % accession_number

        r = requests.get(url, auth=(
            os.environ['REPORTERUNAME'], os.environ['REPORTERPWD']),  verify=False)
        try:
            r = r.json()
        except:
            log.error("Couldn't parse json response from")
            log.error(url)
            # log.error(r.content)

        pathogenic = self.reporter_variant_list_to_genes(
            r, "genomics_alterations_pathogenic")
        likely = self.reporter_variant_list_to_genes(
            r, "genomics_alterations_likely_pathogenic ")
        vus = self.reporter_variant_list_to_genes(
            r, "genomics_alterations_unknown_significance")

        self.number_pathogenic = len(pathogenic)
        all_variants = pathogenic + likely + vus
        genes = [x.strip().split(" ")[0] for x in all_variants]
        self.gene_list = genes
        log.debug("reached end of load_from_ngsreporter")

    def build_matrix(self, path="", force=False):
        log.debug("begin build_matrix debug")

        if not force and self._matrix_loaded:
            return self.matrix

        start_time = time.time()
        results = {}
        pathway_data = defaultdict(list)
        pathway_genes = defaultdict(list)
        gene_pathways = {gene: [] for gene in self.gene_list}

        for gene in self.gene_list:

            pathways = mt.runquery(cypher.pathways_by_gene_list([gene]))

            results[gene] = pathways

            for row in pathways:
                for node in row:
                    node_id = node['stId']
                    print("node_id is %s" % node_id)
                    print(node)
                    pathway_data[node_id] = node
                    pathway_genes[node_id].append(gene)
                    gene_pathways[gene].append(node_id)

        self.pathway_data = pathway_data
        self.pathway_genes = pathway_genes
        self.gene_pathways = gene_pathways

        self.matrix = self.matrix_pathways_by_genes()

        if len(path) > 0:
            self.save_matrix(path)

        if len(self.accession_number) > 0:
            self.save_matrix(self.cache_matrix_file_name())

        self.time_to_build = time.time() - start_time
        return self.matrix

    def pathway_node_id_by_display_name(self, displayName):
        if not hasattr(self, "pathway_data"):
            return "nopathwaydata"
        if not self.pathway_data:
            return "pathwaydataisnone"
        for rid, node in self.pathway_data.items():
            if node['displayName'] == displayName:
                return rid
        return None

    def build_matrix_of_pathway_relationships(self):
        print("coming")

    def genes_from_matrix(self):
        # the top row of the matrix excluding the first and last columns is the gene list
        return [x for x in self.matrix[0][1:-2] if x != '']

    def to_json(self):
        if not self._matrix_loaded:
            self.build_matrix()

        if self._json_loaded:
            return self._json

        gene_nodes = self.gene_json_nodes_from_matrix()

        # fake_division_between_pathogenic_and_vus = int(len(gene_nodes)/2)
        if self.number_pathogenic:
            n_known_clinically_significant = self.number_pathogenic
        else:
            n_known_clinically_significant = 0

        for i in range(0, len(gene_nodes)):
            if i < n_known_clinically_significant:
                classification = "pathogenic"
            else:
                classification = "unknown"
            gene_nodes[i]["classification"] = classification

        pathway_nodes = self.pathway_json_nodes_from_matrix(True)

        nodes = gene_nodes + pathway_nodes

        edges = []
        for ridx in range(1, len(self.matrix)):
            row = self.matrix[ridx]
            for cidx in range(1, len(row)-1):
                cell_value = row[cidx]
                if cell_value == 1:
                    edge = {"source": row[0], "target": self.matrix[0][cidx]}
                    edges.append(edge)

        # remove the orphans before the pathway interrelationships are added
        # to get rid of the gene to 'Disease' useless links

        result_object = {"nodes": nodes, "links": edges}

        result_object = self.remove_orphan_edges(result_object)

        pathway_edges = self.pathway_interrelationships()

        for rel in pathway_edges:
            edge = {"source": rel[0], "target": rel[1]}
            result_object['links'].append(edge)

        result_object = self.remove_orphan_edges(result_object)

        result_object["number_pathogenic"] = n_known_clinically_significant

        result_object["common_pathways"] = self.check_for_common_pathways_in_vus()

        if hasattr(self, "pathway_data"):
            result_object["pathway_data"] = self.pathway_data_to_hash()

        if hasattr(self, 'time_to_build'):
            result_object["time_to_build"] = self.time_to_build
        with open('lastpathwaymatrixdebug.json', 'w') as f:
            f.write(json.dumps(result_object))

        self._json = json.dumps(result_object)
        self._json_loaded = True

        with open(self.cache_json_file_name(), 'w') as f:
            f.write(self._json)

        return self._json

    def gene_json_nodes_from_matrix(self):
        # the gene names are across the first row but not in the first or last column
        # (the first column is empty, the last is a count)
        return [{"id": x, "type": "gene"} for x in self.matrix[0][1:-1] if x != '']

    def pathway_json_nodes_from_matrix(self, exclude_overly_general=True, only_pathways_with_multiple_connections=True):
        if exclude_overly_general:
            exclude_list = ['Disease']
        else:
            exclude_list = []

        pathway_nodes = [{"id": x[0], "type":"pathway"}
                         for x in self.matrix[1:] if x != '' and not x[0] in exclude_list and (not only_pathways_with_multiple_connections or (int(x[-1]) > 1))]

        return pathway_nodes

    def pathway_data_to_hash(self):
        if hasattr(self, "pathway_data"):
            result = {}
            nodes = [v for k, v in self.pathway_data.items()]
            for n in nodes:
                print(n)
                key = n['stId']
                node_val = {k: v for k, v in n.items()}
                node_val['id'] = n.id
                node_val['labels'] = [l for l in n.labels]
                result[key] = node_val
            return result
        else:
            return {}

    def remove_orphan_edges(self, result_object):
        nodes = result_object["nodes"]
        nodes_by_id = {x['id']: True for x in nodes}
        new_edges = []
        for edge in result_object["links"]:
            if edge['source'] in nodes_by_id and edge['target'] in nodes_by_id:
                new_edges.append(edge)
        return {"nodes": nodes, "links": new_edges}

    def pathway_interrelationships(self):
        ids = ",".join([str(n['reactome_pathway_stid'])
                        for k, n in self.pathway_data.items()])
        cy = "MATCH path=()-[:hasEvent]->(n) where id(n) in [%s] return path;" % ids
        g = mt.runquery_asgraph(cy)
        # v =r.values()
        # g = r.graph()
        # generate tuples of from node node, to node name,
        endpoints = [[n.start_node['displayName'],
                      n.end_node['displayName']] for n in g.relationships]
        return endpoints

    def matrix_pathways_by_genes(self):
        gene_keys = self.gene_pathways.keys()
        matrix = []
        header_row = ['Pathway'] + [g for g in gene_keys] + ['Count']
        matrix.append(header_row)
        for k, v in self.pathway_genes.items():
            values = [1 if pk in v else 0 for pk in gene_keys]
            matrix_row = [self.pathway_data[k]
                          ['displayName']] + values + [sum(values)]
            matrix.append(matrix_row)
        return matrix

    # find pathways (excluding overly general ones like 'disease'
    # that are common between more than one gene where at least one of the is a vus
    def check_for_common_pathways_in_vus(self):
        m = self.matrix
        common_pathways = []
        for rowidx in range(1, len(m)):
            # for each pathway (column), assumes all rows have same # of columns
            significant_count = 0
            vus_count = 0
            for colidx in range(1, len(m[0])-1):
                if m[rowidx][colidx] == 1:

                    if colidx <= self.number_pathogenic:
                        significant_count += 1
                    else:
                        vus_count += 1
            # or among vus
            if (significant_count+vus_count > 1) and vus_count > 0:
                common_pathways.append(m[rowidx][0])
        exclude_overgeneral_pathways = ['Disease']

        common_pathways = [
            p for p in common_pathways if not (p.strip() in exclude_overgeneral_pathways)]

        return common_pathways

    def matrix_genes_by_pathways(self):
        pathway_keys = self.pathway_data.keys()
        matrix = []
        header_row = ['Gene'] + [self.pathway_data[pk]['name']
                                 for pk in pathway_keys]
        matrix.append(header_row)
        for k, v in self.gene_pathways.items():
            matrix_row = [k] + [1 if pk in v else 0 for pk in pathway_keys]
            matrix.append(matrix_row)
        return matrix

    def summarize(self):
        print("Total pathways found: %i" % len(self.pathway_data.keys()))

        for k, v in self.gene_pathways.items():
            print("Gene %s: %i pathways" % (k, len(v)))

    def save_matrix(self, path):
        log.debug("save matrix to path %s" % path)
        with open(path, "w") as f:
            writer = csv.writer(f)
            for row in self.matrix:
                writer.writerow(row)

    def read_matrix(self, path):
        m = []
        with open(path, "r") as f:
            cached_matrix_file = csv.reader(f)
            for row in cached_matrix_file:

                m.append([int(v) if v.isdigit() else v for v in row])
        self.matrix = m
        self._matrix_loaded = True
        self.gene_list = self.genes_from_matrix()
        return m

    def test():
        p = PathwayMatrixByGenes(['BRAF', 'KRAS'])
        p.build_matrix()
        p.to_json
        return p
