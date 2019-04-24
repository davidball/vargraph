# http://flask.pocoo.org/

# to launch:
#  FLASK_APP=flaskfe.py flask run
from flask import Flask
import mapping.mapping_by_transcript as mt

app = Flask(__name__)

@app.route("/")
def hello():
    return samples()

@app.route("/transcripts/<string:transcript_ids>")
def transcripts(transcript_ids):
    part1 = mt.pathways_by_transcript_list(transcript_ids.split(","))

    part2 = "<br/><br/>".join([mt.pathways_by_transcript_id(x) for x in transcript_ids])

     
    return "<h1>Pathways By Transcript List</h1>" + part1 + "<br/><br/>" + "<h1>Pathways By Transcript</h1>" + part2

@app.route("/genes/<string:gene_names>")
def genes(gene_names):
    gene_list = gene_names.split(",")
    part1 = mt.pathways_by_gene_list(gene_list)

    part2 = "<br/><br/>".join([mt.pathways_by_gene_list([x]) for x in gene_list])

    return part1 + "<br/><br/>" + part2

@app.route("/samples")
def samples():
    return ("<ul><li><a href='/transcripts/NM_000038,NM_032043,NM_001114122,NM_001904,"
        "NM_022552,NM_002006,NM_024675,NM_181523,NM_003579,"
        "NM_000321,NM_001127208,NM_000546'>19-086-14883</a></li>"
        "<li><a href='/genes/PIK3R1'>PIK3RI</a></li>"
        "</ul>")
