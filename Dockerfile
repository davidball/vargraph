FROM python:3.6.5

EXPOSE 5000
RUN pip3 install --upgrade pip
CMD FLASK_APP=flaskfe.py python -m flask run

COPY ./ /vargraph
WORKDIR /vargraph
RUN pip3 install -r requirements.txt 
