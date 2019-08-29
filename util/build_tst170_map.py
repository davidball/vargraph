import yaml
import csv


tst170_path = "data/TST170_SNV_INDEL_LIST.txt"

with open(tst170_path) as f:
    tst170 = yaml.load(f)

physical_entities_path = "data/reactome_physical_entities.txt"

with open(physical_entities_path) as f:
    r = csv.reader(f)
    # some strange rows towards the end (at leat) have more than 2 , delimited values....

    # for now just taking the firtst and last , deliminted value of each row
    pe = {rows[0]: rows[-1] for rows in r}


print(tst170)
print(pe)

tst170map = {}
unmapped = []
for gene in tst170:
    if gene in pe:
        tst170map[gene] = pe[gene]
    else:
        unmapped.append(gene)


output_path = "tst170_reactome_map.txt"
with open(output_path, "w") as f:
    w = csv.writer(f)
    for k, v in tst170map.items():
        w.writerow([k, v])

output_path = "tst170_unmapped.txt"
with open(output_path, "w") as f:
    f.write("\n".join(unmapped))


cypherlines = []

reactome_id_list = "['%s']" % "','".join(tst170map.values())
cypher = "MATCH (n:PhysicalEntity) where n.stId in %s RETURN n" % reactome_id_list

cypherlines.append(cypher)


cypher = "MATCH (n:PhysicalEntity)-[r*0..2]-(n2:PhysicalEntity) where n.stId in %s and n2.stId in %s return n,r, n2;" % [
    reactome_id_list]*2


cypherlines.append(cypher)


output_path = "cypher_examples.txt"
with open(output_path, "w") as f:
    f.writelines("\n".join(cypherlines))
