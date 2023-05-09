import redis
from sentence_transformers import SentenceTransformer
from redis.commands.search.query import Query
from redis.commands.search.field import TextField, VectorField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
import numpy as np
import os
import nltk

from nltk.tokenize import sent_tokenize

model = SentenceTransformer('sentence-transformers/multi-qa-MiniLM-L6-cos-v1')


def get_db(decode=True):
    try:
        return redis.StrictRedis(host=os.getenv('DB_SERVICE', '127.0.0.1'),
                                 port=int(os.getenv('DB_PORT',6379)),
                                 password=os.getenv('DB_PWD',''),
                                 decode_responses=decode)
    except redis.exceptions.ConnectionError:
        print("connection error")


def init():
    nltk.download('punkt')

    indexes = get_db().execute_command("FT._LIST")
    if "oaps_idx" not in indexes:
        index_def = IndexDefinition(prefix=["oaps:"], index_type=IndexType.JSON)
        schema = (  TextField("$.sentence", as_name="sentence"),
                    VectorField("$.embedding", "HNSW", {"TYPE": "FLOAT32", "DIM": 384, "DISTANCE_METRIC": "COSINE"}, as_name="embedding"))
        get_db(False).ft('oaps_idx').create_index(schema, definition=index_def)


def get_embedding_as_vector(text):
    return model.encode(text).tolist()


def get_embedding_as_blob(text):
    return model.encode(text).astype(np.float32).tobytes()


def index_document(pk, text):
    seq = 0
    for txt_sentence in sent_tokenize(text):
        sentence = {
            'seq': seq,
            'sentence': txt_sentence,
            'embedding': get_embedding_as_vector(txt_sentence)
        }
        
        get_db(False).json().set("oaps:{}:{}".format(pk,seq), '$', sentence)
        seq = seq + 1


def check_document(text, epsilon):
    q = Query("@embedding:[VECTOR_RANGE $radius $vec]=>{$YIELD_DISTANCE_AS: score}")\
        .sort_by("score", asc=True)\
        .return_field("score")\
        .dialect(2)
        
    p = {"vec": get_embedding_as_blob(text), "radius": epsilon}
    
    res = get_db(False).ft("oaps_idx").search(q, p).docs
    return res
