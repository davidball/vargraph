# http://flask.pocoo.org/

# to launch:
#  FLASK_APP=flaskfe.py flask run
# or with debugging/autorefresh:
# FLASK_APP=flaskfe.py FLASK_DEBUG=1 python -m flask run
from flask import Flask
from flask import request
from flask import render_template
from flask import session
from flask import flash
import os
import logging
from healthcheck import healthcheck

import mapping.mapping_by_transcript as mt
from flask_bootstrap import Bootstrap
import sys


app_name = 'vargraph'

app = Flask(app_name)
Bootstrap(app)
#app.run(host='0.0.0.0')
app.secret_key = os.urandom(12)

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter(
   '%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
app.logger.addHandler(handler)
app.logger.setLevel(logging.DEBUG)



@app.route("/")
def home():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return samples()

@app.route('/login', methods=['POST'])
def do_admin_login():
    pwd = os.environ.get('VARGRAPHPWD')
    if pwd == None:
        flash("Authentication not configured. Login is impossible.")
    else:
        if request.form['password'] == pwd and request.form['username'] == 'admin':
            session['logged_in'] = True
        else:
            flash('wrong password!')
    return home()

@app.route("/logout")
def logout():
    session['logged_in'] = False
    return home()

@app.route("/transcripts/<string:transcript_ids>")
def transcripts(transcript_ids):
    part1 = mt.pathways_by_transcript_list(transcript_ids.split(","))

    part2 = "<br/><br/>".join([mt.pathways_by_transcript_id(x)
                               for x in transcript_ids])

    return "<h1>Pathways By Transcript List</h1>" + part1 + "<br/><br/>" + "<h1>Pathways By Transcript</h1>" + part2

def render_accession(accession_number):
    print("begin render_accession", file=sys.stderr)
    app.logger.info('via loggerxxxs failed to log in')
    a = mt.PathwayMatrixByGenes([])
    a.load_from_ngsreporter(accession_number)
    m = a.build_matrix('matrixtest.csv')
    print("built matrix", file=sys.stderr)
    return render_template('gene_list_analysis.html',
                           cypher1=mt.pathways_by_gene_list(a.gene_list),
                           cypher2=[mt.pathways_by_gene_list(
                               [x]) for x in a.gene_list],
                           matrix=m, gene_list=a.gene_list, matrixjson = a.to_json())    

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


@app.route('/accession/<string:accession_number>', methods=['GET'])
def get_accession(accession_number):
    return render_accession(accession_number)

@app.route('/analysis', methods=['GET'])
def get_analysis():
    return render_template('analysis.html')


@app.route('/analysis', methods=['POST'])
def post_analysis():
    gene_list = [g.strip() for g in request.form['gene_list'].split("\n")]
    return render_gene_list(gene_list)


@app.route('/jsnetworkx', methods=['GET'])
def jsnetworkx_try():
    return render_template('jsnetworkx.html')


@app.route('/simplegraph', methods=['GET'])
def simplegraph():
    return render_template('simplegraph.html')

@app.route('/test', methods=['GET'])
def test():
   print("in test route about to healthcheck")
   return "I am here. %s" % healthcheck()

app.run(host='0.0.0.0')
