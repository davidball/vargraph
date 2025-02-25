from mapping.mapping_by_transcript import *
import mapping.pathway_matrix.pathway_matrix_by_genes as p

import mapping.pathway_matrix.pathway_matrix_by_genes_static as pstatic

gene_list = ['APC', 'BRIP1', 'CTNNB1', 'PIK3R1', 'TP53']
a = pstatic.PathwayMatrixByGenesStatic(gene_list)
m = a.build_matrix('matrixtest.csv')
a.summarize()


# url = http://localhost:5000/genes/APC,BRIP1,CTNNB1,PIK3R1,TP53 #
