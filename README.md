# Open Anti-Plagiarism Software (OAPS)

This is a demo software that helps spot plagiarism attempts.

## Run the demo

Clone the repository, create a virtual environment and install the dependencies.

```
git clone https://github.com/mortensi/oaps.git

python3 -m venv oapsvenv

cd oaps
pip install -e .
```

Now you can execute the demo. The demo will basically:

## 1. Create the index

The index considers JSON documents prefixed as indicated and will consider the vectors stored at the `$.embedding` path. I have added also an inverted index on the text itself in `$sentence` to enable full-text search.

```
FT.CREATE oaps_idx 
ON JSON 
PREFIX 1 oaps:seq: 
SCHEMA $.sentence AS sentence TEXT 
$.embedding AS embedding VECTOR HNSW 6 TYPE FLOAT32 DIM 384 DISTANCE_METRIC COSINE
```

## 2. Import a dataset of short articles

Machine learning models produce embeddings of texts of limited size. As an example, the model [all-MiniLM-L12-v1](https://huggingface.co/sentence-transformers/all-MiniLM-L12-v1) will truncate input text longer than 128 words. 

Because of this, and to increase also the precision of our anti-plagiarism application, we will split and index texts by sentence. We are using a simple regular expression to split the text by the separators `.`, `!`, `?`.


## 3. Run the plagiarism text with a sample text

We pass an arbitrary text including a sentence that was copied from the database. Run the demo:

```
python3 demo.py
```

The output will indicate the most similar sentence (successfully).

```
Indexed 20 elements
oaps:seq:16gpy:1
[' We are a bunch of people convinced that you have to pass through difficult, or better, impossible challenges to see an idea reach the production stage and possibly provide benefits']
```

## API usage

In the file `oaps.py` you can check the three relevant methods in Python.

- `init()` verifies that the index does not exist and proceeds to create it
- `index_document(pk, text)` will index sentences, one by one, in the text
- `check_document(text, epsilon)` will execute Vector Similarity Search and retrieve the most similar document/s based on tolerance. This tolerance-based search, also known as [VSS range query](https://redis.io/docs/stack/search/reference/vectors/#range-queries), depends on epsilon, a coefficient to filter the results by distance from the query vector.




