import mapping.mapping_by_transcript as mt

accn='19-191-16207'

a = mt.PathwayMatrixByGenes([])

a.load_from_ngsreporter(accn)

a.number_pathogenic=2

c = a.check_for_common_pathways_in_vus()

print(c)
