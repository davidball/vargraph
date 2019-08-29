import csv
from collections import defaultdict


class StaticReactomePathways():
    def __init__(self):
        saved_pathway_data_path = 'static/reactome_pe_and_pathway_for_mgl_genes.csv'
        with open(saved_pathway_data_path) as f:
            r = csv.reader(f)
            pathways_by_gene = defaultdict(list)

            # some strange rows towards the end (at leat) have more than 2 , delimited values....

            # for now just taking the firtst and last , deliminted value of each row
            first = True
            for row in r:
                if first:
                    field_names = row
                    first = False
                else:
                    rowh = dict(zip(field_names, row))
                    pathways_by_gene[rowh['gene'].upper()].append(rowh)
        self.pathways_by_gene = pathways_by_gene

    def __getitem__(self, gene):
        return self.pathways_by_gene[gene.upper()]

    def test():
        pathways = StaticReactomePathways()
        print(pathways['BRAF'])
