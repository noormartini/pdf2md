# Chapter 3: Related Work

Since 2024, a growing number of LLM-based systems have attempted to automate the scientific research process [28]. This chapter provides an overview of these systems with a focus on three aspects relevant to this thesis: the degree of human involvement, the execution environment (cloud versus local) and the user interface.

## 3.1 Automated Research Systems

data-to-paper [1], released in April 2024, was the first system to generate full research manuscripts automatically. Based on user-provided annotated datasets and metadata about them, it combines interacting LLM agents with programmatic information tracing and produces backward-traceable manuscripts where every numeric value links directly to the code that generated it. It supports both a fully autonomous mode and a copilot mode for human review after each step, though it requires annotated datasets as input and depends on cloud-hosted LLMs.

Four months later, The AI Scientist [2] was released, which removed the dataset requirement. With a broad research direction and a human-authored code template, it generates ideas, executes experiments, writes a full LATEX paper and evaluates the result without human intervention, at a cost of approximately $15 per paper. Its successor, The AI Scientist v2 [7], removed the dependency on code templates, introduced a parallelized tree search over experiment paths and added VLMs for evaluating generated figures.

Agent Laboratory [3] takes a human-provided research idea and processes it through three sequential phases: a literature review phase that collects and analyzes papers from arXiv, an experimentation phase that uses HuggingFace datasets and Python, and a report writing phase that produces a LATEX manuscript and code repository. It reports an 84% cost reduction compared to The AI Scientist. Unlike The AI Scientist, it is designed with optional human feedback between phases.

Jr. AI Scientist [29] takes a different starting point and builds on a human-provided baseline paper. Based on a paper with its code, the system identifies limitations, proposes improvements
