from mapping.mapping_by_transcript import *
from mapping.static_reactome_pathways import *


class PathwayMatrixByGenesStatic(PathwayMatrixByGenes):

    def build_matrix(self, path="", force=False):
        log.debug("begin build_matrix debug")
        pathway_cache = srp.StaticReactomePathways()
        if not force and self._matrexix_loaded:
            return self.matrix

        start_time = time.time()
        results = {}
        pathway_data = defaultdict(list)
        pathway_genes = defaultdict(list)
        gene_pathways = {gene: [] for gene in self.gene_list}

        for gene in self.gene_list:

            #pathways = runquery(pathways_by_gene_list([gene]))
            pathways = pathway_cache.pathways_by_gene[gene]
            results[gene] = pathways

            for row in pathways:

                node_id = row['reactome_pathway_stid']
                print("node_id is %s" % node_id)
                print(row)
                row['displayName'] = row['pathway_name']
                pathway_data[node_id] = row
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
            if row[-1] > 1:
                print("%s was %i" % (row[0], row[-1]))
                for cidx in range(1, len(row)-1):
                    cell_value = row[cidx]
                    if cell_value == 1:
                        edge = {"source": row[0],
                                "target": self.matrix[0][cidx]}
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

    def pathway_interrelationships(self):
        ids = "','".join([str(n['reactome_pathway_stid'])
                          for k, n in self.pathway_data.items()])
        cy = "MATCH path=()-[:hasEvent]->(n) where n.stId in ['%s'] return path;" % ids
        g = runquery_asgraph(cy)
        # v =r.values()
        # g = r.graph()
        # generate tuples of from node node, to node name,
        endpoints = [[n.start_node['displayName'],
                      n.end_node['displayName']] for n in g.relationships]
        return endpoints

    def test():
        pp = PathwayMatrixByGenesStatic()
        pp.gene_list.append('BRAF')
        pp.gene_list.append('KRAS')
        pp.build_matrix()

    def test_with_ngsreporter():
        pp = PathwayMatrixByGenesStatic()
        pp.load_from_ngsreporter('19-212-07584')
        pp.to_json()
