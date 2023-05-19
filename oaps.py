import redis
from sentence_transformers import SentenceTransformer
from redis.commands.search.query import Query
from redis.commands.search.field import TextField, VectorField, TagField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
import numpy as np
import os
import re

from img2vec_pytorch import Img2Vec
from PIL import Image

img2vec = Img2Vec(cuda=False)
IMAGE_VECTOR_DIMENSION=512
model = SentenceTransformer('sentence-transformers/all-MiniLM-L12-v1')
MODELSIZE = 384


def get_db(decode=True):
    try:
        return redis.StrictRedis(host=os.getenv('DB_SERVICE', '127.0.0.1'),
                                 port=int(os.getenv('DB_PORT',6379)),
                                 password=os.getenv('DB_PWD',''),
                                 decode_responses=decode)
    except redis.exceptions.ConnectionError:
        print("connection error")


def init():
    indexes = get_db().execute_command("FT._LIST")
    if "oaps_txt_idx" not in indexes:
        index_def = IndexDefinition(prefix=["oaps:seq:"], index_type=IndexType.JSON)
        schema = (  TextField("$.sentence", as_name="sentence"),
                    VectorField("$.embedding", "HNSW", {"TYPE": "FLOAT32", "DIM": MODELSIZE, "DISTANCE_METRIC": "COSINE"}, as_name="embedding"))
        get_db(False).ft('oaps_txt_idx').create_index(schema, definition=index_def)

    if "oaps_pic_idx" not in indexes:
        index_def = IndexDefinition(prefix=["oaps:pic:"], index_type=IndexType.JSON)
        schema = (  TagField("$.file", as_name="file"),
                    VectorField("$.embedding", "HNSW", {"TYPE": "FLOAT32", "DIM": IMAGE_VECTOR_DIMENSION, "DISTANCE_METRIC": "COSINE"}, as_name="embedding"))
        get_db(False).ft('oaps_pic_idx').create_index(schema, definition=index_def)


def get_embedding_as_vector(text):
    return model.encode(text).tolist()


def get_embedding_as_blob(text):
    return model.encode(text).astype(np.float32).tobytes()


def get_image_embedding_as_vector(imagepath):
    img = Image.open(imagepath).convert('RGB')
    return img2vec.get_vec(img).tolist()


def get_image_embedding_as_blob(imagepath):
    img = Image.open(imagepath).convert('RGB')
    return img2vec.get_vec(img).astype(np.float32).tobytes()


def index_document(pk, text):
    seq = 0
    sentences = re.split("[//.|//!|//?]", text)
    for txt_sentence in sentences:
        sentence = {
            'seq': seq,
            'sentence': txt_sentence,
            'embedding': get_embedding_as_vector(txt_sentence)
        }
        
        get_db(False).json().set("oaps:seq:{}:{}".format(pk,seq), '$', sentence)
        seq = seq + 1


def check_document(text, epsilon):
    res = []
    sentences = re.split("[//.|//!|//?]", text)
    for txt_sentence in sentences:
        q = Query("@embedding:[VECTOR_RANGE $radius $vec]=>{$YIELD_DISTANCE_AS: score}")\
            .sort_by("score", asc=True)\
            .return_field("score")\
            .dialect(2)
            
        p = {"vec": get_embedding_as_blob(txt_sentence), "radius": epsilon}
        
        found = get_db(False).ft("oaps_txt_idx").search(q, p).docs
        if len(found) > 0:
            res.append([x['id'] for x in found])

    return res


def index_image(pk, imagepath):
    pic = {
        'embedding':get_image_embedding_as_vector(imagepath),
        'file':imagepath
    }
    
    get_db(False).json().set("oaps:pic:{}".format(pk), '$', pic)


def check_image(imagepath, epsilon):
    q = Query("@embedding:[VECTOR_RANGE $radius $vec]=>{$YIELD_DISTANCE_AS: score}")\
        .sort_by("score", asc=True)\
        .return_field("score")\
        .return_field("file")\
        .dialect(2)
        
    p = {"vec": get_image_embedding_as_blob(imagepath), "radius": epsilon}
    
    res = get_db(False).ft("oaps_pic_idx").search(q, p).docs
    return res