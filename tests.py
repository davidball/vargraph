from mapping.mapping_by_transcript import *
gene_list = ['APC','BRIP1','CTNNB1','PIK3R1','TP53']
a = PathwayMatrixByGenes(gene_list)
m = a.build_matrix('matrixtest.csv')
a.summarize()


#url = http://localhost:5000/genes/APC,BRIP1,CTNNB1,PIK3R1,TP53