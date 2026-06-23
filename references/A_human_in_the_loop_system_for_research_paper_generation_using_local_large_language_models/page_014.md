Embedding Models and Semantic Similarity
An embedding is a numerical vector that
represents the meaning of a piece of text [22]. The idea originates from the Word2Vec
architecture, which showed that individual words can be mapped to vectors where seman-
tically similar words end up close together in the vector space [22]. Modern embedding
models extend this to full sentences and paragraphs to produce a single vector for an entire
passage [23]. The similarity between two embedding vectors can be measured using cosine
similarity, which quantifies how much two vectors align, regardless of their length [23]. A
cosine similarity close to 1 implies the texts are semantically similar, and a value near or
below 0 implies little relation. This allows comparing texts by meaning instead of match-
ing keywords, for example, which can be helpful when different words express the same
idea.
Retrieval-Augmented Generation
As described above, LLMs can hallucinate, particu-
larly when not provided with relevant source material. RAG addresses this problem by re-
trieving relevant text from documents and injecting it into the prompt before inference [24].
RAG makes use of embeddings and semantic similarity. The original RAG pipeline con-
sists of five steps [25]:
1. Chunking: Documents are split into smaller text segments.
2. Embedding: Each chunk is converted into an embedding vector.
3. Storing: The embedding vectors are stored in a vector database for later retrieval.
4. Retrieving: The system embeds the user’s query and retrieves the most similar
chunks using cosine similarity. Optionally, a reranker can rescore the retrieved
chunks to improve relevance [26].
5. Injecting: The original text of the selected chunks is added to the prompt as addi-
tional context before the LLM generates its answer.
By grounding inference in real documents, RAG reduces the risk of hallucinations [25].
Human-in-the-Loop
HITL is a term for interaction paradigms where humans are part of
the learning or decision-making process of a machine learning (ML) system [27]. It aims
to improve both accuracy and efficiency of ML systems while also making humans more
effective [27]. How this paradigm is applied here is discussed in Chapter 4.
4