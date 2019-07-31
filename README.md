Analyzing Variants Using Reactome data in a web based Front End

A Python Flask app. 

To run the flask app in debug mode:

```FLASK_APP=flaskfe.py FLASK_DEBUG=1 python -m flask run```

Or without debugging, auto code refresh:

```FLASK_APP=flaskfe.py  python -m flask run```

Then visit it at http://localhost:5000/



In lieu of keeping the reactome db in github, it should be downloaded separately

curl https://reactome.org/download/current/reactome.graphdb.tgz --output reactome.graphdb.tgz

tar zxvf reactome.graphdb.tgz

git clone git@github.com:davidball/vargraph.git

mkdir -p vargraph/datafordocker/
mv rea 


To communicate with NgsReporter set environment variables:

# Environment Variables
REPORTERUNAME
REPORTERPWD
