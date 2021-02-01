FROM python:3.7
WORKDIR /opt
RUN mkdir elastic
ADD init/elastic/index.json ./elastic/index.json
RUN mkdir USE
RUN curl -L "https://tfhub.dev/google/universal-sentence-encoder/4?tf-hub-format=compressed" \
  | tar -xzvC ./USE/
ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt
ADD src src
WORKDIR /opt/src
ENV PYTHONPATH /opt/src
CMD gunicorn -w 2 -k uvicorn.workers.UvicornWorker server.main:app --bind 0.0.0.0:8000
