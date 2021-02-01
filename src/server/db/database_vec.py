import os

from typing import List

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

from server.config import config

Vector = List[float]


class Document:
    def __init__(self, sentence_id: int, vector: Vector):
        self.sentence_id = sentence_id
        self.vector = vector


class SimilarResult:
    def __init__(self, sentence_id: int, score: float):
        self.sentence_id = sentence_id
        self.score = score


class DatabaseVec:
    def __init__(self, host: str, port: int, index_file: str):
        self.client = Elasticsearch([{'host': host, 'port': port}])
        self.index_name = "sentence_vectors"
        self._ensure_index_created(index_file)

    def add_documents(self, documents: List[Document]):
        requests = []
        for document in documents:
            request = {
                "_id": document.sentence_id,
                "_op_type": "index",
                "_index": self.index_name,
                "vector": document.vector,
            }
            requests.append(request)
        bulk(self.client, requests)

    def search_similar(self, vector: Vector, k: int) -> List[SimilarResult]:
        query = {
            "script_score": {
                "query": {"match_all": {}},
                "script": {
                    "source": "cosineSimilarity(params.query_vector, doc['vector']) + 1.0",
                    "params": {"query_vector": vector}
                }
            }
        }
        response = self.client.search(
            index=self.index_name,
            body={
                "size": k,
                "query": query,
            }
        )
        return [SimilarResult(
            sentence_id=int(hit["_id"]),
            score=hit["_score"]) for hit in response["hits"]["hits"]]

    def _ensure_index_created(self, index_file: str):
        if self.client.indices.exists(self.index_name):
            return
        if index_file and os.path.isfile(index_file):
            with open(index_file) as index_file:
                source = index_file.read().strip()
                self.client.indices.create(index=self.index_name, body=source)
        else:
            self.client.indices.create(index=self.index_name)


database_vec = DatabaseVec(config.database_vec_host, config.database_vec_port, config.database_vec_index_file)


def make_documents(sentence_ids, vectors):
    documents = []
    for i in range(len(sentence_ids)):
        sentence_id = sentence_ids[i]
        vector = vectors[i]
        documents.append(Document(sentence_id=sentence_id, vector=vector))
    return documents
