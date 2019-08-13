import json
import glob
import csv





#[
#  "common_pathways",
#  "links",
#  "nodes",
#  "number_pathogenic",
#  "pathway_data",
#  "time_to_build"
#]

def find_cache_stats():
    cache = glob.glob('*.json')
    field_names = ['accession_number', 'time_to_build', 'count_of_genes', 'count_of_pathways','count_of_common_pathways','common_pathways']

    with open('cache_stats.csv', 'w' ) as output_file:
        output = csv.writer(output_file, quotechar='|', quoting=csv.QUOTE_MINIMAL)
        output.writerow(field_names)    
        for p in cache:
            with open(p,'r') as f:
                d = json.load(f)
                t = d['time_to_build']
                nodes = d['nodes']
                genes = [n for n in nodes if n['type']=='gene']
                pathways = [n for n in nodes if n['type']=='pathway']
                
                output.writerow([p.replace(".json",""), t, len(genes), len(pathways), len(d['common_pathways']), ";".join(d['common_pathways'])])
         


find_cache_stats()
#
