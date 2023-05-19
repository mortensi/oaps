# Open Anti-Plagiarism Software (OAPS)

This is a demo software that helps spot plagiarism attempts in texts and images.
It uses [Redis Stack](https://redis.io/docs/stack/) Vector Similarity Search (VSS) feature. Learn about [VSS](https://redis.io/docs/stack/search/reference/vectors/).


## Run the demo

First, start a Redis Stack instance. You can use a [Docker container](https://hub.docker.com/r/redis/redis-stack). Start it as follows:

```
docker run -d --name redis-stack -p 6379:6379 -p 8001:8001 redis/redis-stack:latest
```

Now, clone the repository, create a virtual environment and install the dependencies in the environment.

```
git clone https://github.com/mortensi/oaps.git

python3 -m venv oapsvenv
source oapsvenv/bin/activate

cd oaps
pip install -e .
```

Now you can execute the demo. 

```
python3 demo.py
```


## API usage

In the file `oaps.py` you can check the three relevant methods in Python.

- `init()` verifies that the index does not exist and proceeds to create it
- `index_document(pk, text)` will index sentences, one by one, in the text
- `check_document(text, epsilon)` will execute Vector Similarity Search and retrieve the most similar document/s based on tolerance. This tolerance-based search, also known as [VSS range query](https://redis.io/docs/stack/search/reference/vectors/#range-queries), depends on epsilon, a coefficient to filter the results by distance from the query vector.
- `index_image(pk, imagepath)` will index the picture stored at the indicated path
- `check_image(imagepath, epsilon)` will execute Vector Similarity Search and retrieve the most similar image/s based on tolerance


## Plagiarism of documents

The demo creates an index that considers JSON documents that are prefixed `oaps:seq:` and will consider the vectors stored at the `$.embedding` path in the documents. I have added also an inverted index on the text itself in `$sentence` to enable full-text search.

```
FT.CREATE oaps_txt_idx 
ON JSON 
PREFIX 1 oaps:seq: 
SCHEMA $.sentence AS sentence TEXT 
$.embedding AS embedding VECTOR HNSW 6 TYPE FLOAT32 DIM 384 DISTANCE_METRIC COSINE
```

The demo imports the dataset `demo/mortensi.csv`, which stores a collection of sample articles from [my blog](https://www.mortensi.com/)

Machine learning models produce embeddings of texts of limited size. As an example, the model [all-MiniLM-L12-v1](https://huggingface.co/sentence-transformers/all-MiniLM-L12-v1) will truncate input text longer than 128 words. 

Because of this, and to increase also the precision of our anti-plagiarism application, we will split and index texts by sentence. We are using a simple regular expression to split the text by the separators `.`, `!`, `?`.

To test this functionality, we pass an arbitrary text including a sentence that was copied from the dataset. 

The output will indicate the most similar sentence (successfully).

```
Indexed 20 elements
oaps:seq:16gpy:1
[' We are a bunch of people convinced that you have to pass through difficult, or better, impossible challenges to see an idea reach the production stage and possibly provide benefits']
```


## Similarity of images

The index for images is created with the following syntax:

```
FT.CREATE oaps_pic_idx 
ON JSON 
PREFIX 1 oaps:pic: 
SCHEMA $.file AS file TAG SEPARATOR , 
$.embedding AS embedding VECTOR HNSW 6 TYPE FLOAT32 DIM 512 DISTANCE_METRIC COSINE
```

For the test, three sample images are vectorized and stored (a spoon, a cup, and a glass).

As a test, we propose another glass and have it identified (as a glass).