# http://flask.pocoo.org/

# to launch:
#  FLASK_APP=flaskfe.py flask run
# or with debugging/autorefresh:
# FLASK_APP=flaskfe.py FLASK_DEBUG=1 python -m flask run
from flask import Flask
from flask import request
from flask import render_template
import mapping.mapping_by_transcript as mt
from flask_bootstrap import Bootstrap

app = Flask(__name__)
Bootstrap(app)

@app.route("/")
def hello():
    return samples()


@app.route("/transcripts/<string:transcript_ids>")
def transcripts(transcript_ids):
    part1 = mt.pathways_by_transcript_list(transcript_ids.split(","))

    part2 = "<br/><br/>".join([mt.pathways_by_transcript_id(x)
                               for x in transcript_ids])

    return "<h1>Pathways By Transcript List</h1>" + part1 + "<br/><br/>" + "<h1>Pathways By Transcript</h1>" + part2


def render_gene_list(gene_list):

    a = mt.PathwayMatrixByGenes(gene_list)
    m = a.build_matrix('matrixtest.csv')

    return render_template('gene_list_analysis.html',
                           cypher1=mt.pathways_by_gene_list(gene_list),
                           cypher2=[mt.pathways_by_gene_list(
                               [x]) for x in gene_list],
                           matrix=m, gene_list=gene_list, matrixjson = a.to_json())

# @app.context_processor
# def render_table(data):
#         return "just testing"


@app.route("/genes/<string:gene_names>")
def genes(gene_names):
    gene_list = [g.strip() for g in gene_names.split(",")]
    return render_gene_list(gene_list)


@app.route("/samples")
def samples():
    return ("<ul><li><a href='/transcripts/NM_000038,NM_032043,NM_001114122,NM_001904,"
            "NM_022552,NM_002006,NM_024675,NM_181523,NM_003579,"
            "NM_000321,NM_001127208,NM_000546'>19-086-14883</a></li>"
            "<li><a href='/genes/PIK3R1'>PIK3RI</a></li>"
            "</ul>")


@app.route('/analysis', methods=['GET'])
def get_analysis():
    return render_template('analysis.html')


@app.route('/analysis', methods=['POST'])
def post_analysis():
    gene_list = [g.strip() for g in request.form['gene_list'].split("\n")]
    return render_gene_list(gene_list)
