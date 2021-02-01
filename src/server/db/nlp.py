from typing import List

import tensorflow.compat.v1 as tf
import tensorflow_hub as tf_hub

from nltk.tokenize.punkt import PunktSentenceTokenizer

from server.config import config


def make_text_preview(text: str, length: int):
    dots = "..."
    e = length - len(dots)
    return (text[:e] + dots) if len(text) > length else text


def get_sentence_spans(text: str):
    for start, end in PunktSentenceTokenizer().span_tokenize(text):
        yield start, end


class TextEmbedding:
    def __init__(self, url):
        self.embed = tf_hub.load(url)

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        vectors = tf.make_ndarray(tf.make_tensor_proto(self.embed(texts))).tolist()
        return vectors


text_embedding = TextEmbedding(config.text_embedding_model_url)
