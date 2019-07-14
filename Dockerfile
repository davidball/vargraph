FROM python:3.6.5

COPY ./ /vargraph
WORKDIR /vargraph

EXPOSE 5000

RUN pip3 install -r requirements.txt 
CMD FLASK_APP=flaskfe.py FLASK_DEBUG=1 python -m flask run