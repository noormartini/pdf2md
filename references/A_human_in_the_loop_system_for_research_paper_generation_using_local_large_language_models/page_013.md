# Chapter 2
**Foundations**
This chapter provides a high-level overview of the core concepts needed to understand
the system design presented in Chapter 4. It covers LLMs, embedding models, retrieval-
augmented generation (RAG) and the HITL paradigm. The explanations focus on what is
relevant to this work and do not aim to be exhaustive.
Large Language Models
LLMs are neural networks trained on large bodies of text [12].
They process text as a sequence of tokens, which are small chunks of text such as words
or parts of words. Given such a sequence, an LLM predicts a probability distribution over
the next token and samples from it to generate text [13]. This process of running an LLM
to produce output is called inference. How the next token is picked from the distribu-
tion depends on the decoding strategy. Parameters like temperature and top-p control the
randomness of sampling and allow the same model to produce predictable or more varied
outputs [14]. A vision-language model (VLM) is a variant of an LLM. A VLM includes an
encoder that converts images into numerical vectors which it can process besides text [15].
On a broader level, LLMs can be divided into two categories: proprietary models, whose
weights are closed-source, and open-weight models, whose weights are publicly available,
which allows end users to run them locally [16]. However, open-weight models generally
score below the top proprietary models on standardized benchmarks [17]. Running an
LLM locally requires enough memory to hold the model weights, either in video random
access memory (VRAM), random access memory (RAM), or a combination of both [18].
Quantization reduces the memory a model consumes by compressing its weights to a lower
numerical precision (for example, storing weights as 8-bit integers instead of 16-bit floats)
at the cost of some accuracy [19, 20]. LLMs also have a fixed context window that limits
how much text they can process in a single call. The performance of LLMs worsens in long
multi-turn conversations, with the models losing coherence from one turn to the next [21].
Hallucination is another problem. LLMs may produce text that is fluent and plausible but
factually wrong when they do not have access to relevant source material [6]. In auto-
mated research contexts, this problem manifests as citation inaccuracies and hallucinated
experimental results [2, 7].
3